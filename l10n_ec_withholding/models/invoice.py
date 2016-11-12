# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import time
import logging

from openerp import (
    models,
    fields,
    api,
    _
)
from openerp.exceptions import (
    except_orm,
    Warning as UserError
)
import openerp.addons.decimal_precision as dp

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
    'liq_purchase': 'purchase'
}


class Invoice(models.Model):

    _inherit = 'account.invoice'
    __logger = logging.getLogger(_inherit)

    @api.model
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    @api.multi
    def print_move(self):
        # Método para imprimir comprobante contable
        return self.env['report'].get_action(
            self.move_id,
            'l10n_ec_withholding.account_move_report'
        )

    @api.multi
    def print_liq_purchase(self):
        # Método para imprimir reporte de liquidacion de compra
        datas = {'ids': [self.id], 'model': 'account.invoice'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_liq_purchase',
            'model': 'account.invoice',
            'datas': datas,
            'nodestroy': True,
            }

    @api.multi
    def print_retention(self):
        """
        Método para imprimir reporte de retencion
        """
        datas = {
            'ids': [self.retention_id.id],
            'model': 'account.retention'
        }
        if not self.retention_id:
            raise UserError(u'No tiene retención')
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.retention',
            'model': 'account.retention',
            'datas': datas,
            'nodestroy': True,
        }

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id')  # noqa
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)  # noqa
        amount_manual = 0
        for line in self.tax_line_ids:
            if line.manual:
                amount_manual += line.amount
            if line.tax_id.tax_group_id.code == 'vat':
                self.amount_vat += line.base
                self.amount_tax += line.amount
            elif line.tax_id.tax_group_id.code == 'vat0':
                self.amount_vat_cero += line.base
            elif line.tax_id.tax_group_id.code == 'novat':
                self.amount_novat += line.base
            elif line.tax_id.tax_group_id.code == 'no_ret_ir':
                self.amount_noret_ir += line.base
            elif line.tax_id.tax_group_id.code in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:  # noqa
                self.amount_tax_retention += line.amount
                if line.tax_id.tax_group_id.code == 'ret_vat_b':
                    self.amount_tax_ret_vatb += line.base
                    self.taxed_ret_vatb += line.amount
                elif line.tax_id.tax_group_id.code == 'ret_vat_srv':
                    self.amount_tax_ret_vatsrv += line.base
                    self.taxed_ret_vatsrv += line.amount
                elif line.tax_id.tax_group_id.code == 'ret_ir':
                    self.amount_tax_ret_ir += line.base
                    self.taxed_ret_ir += line.amount
            elif line.tax_id.tax_group_id.code == 'ice':
                self.amount_ice += line.amount
        if self.amount_vat == 0 and self.amount_vat_cero == 0:
            # base vat not defined, amount_vat by default
            self.amount_vat_cero = self.amount_untaxed
        self.amount_total = self.amount_untaxed + self.amount_tax + self.amount_tax_retention + amount_manual  # noqa
        self.amount_pay = self.amount_tax + self.amount_untaxed
        # continue odoo code for *signed fields
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:  # noqa
            amount_total_company_signed = self.currency_id.compute(self.amount_total, self.company_id.currency_id)  # noqa
            amount_untaxed_signed = self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id)  # noqa
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    def name_get(self):
        result = []
        for inv in self:
            result.append((inv.id, "%s %s" % (inv.reference, inv.number and inv.number or '*')))  # noqa
        return result

    @api.one
    @api.depends('tax_line_ids.tax_id')
    def _check_retention(self):
        TAXES = ['ret_vat_b', 'ret_vat_srv', 'ret_ir', 'no_ret_ir']  # noqa
        for tax in self.tax_line_ids:
            if tax.tax_id.tax_group_id.code in TAXES:
                self.has_retention = True

    HELP_RET_TEXT = '''Automatico: El sistema identificara los impuestos
    y creara la retencion automaticamente,
    Manual: El usuario ingresara el numero de retencion
    Agrupar: Podra usar la opcion para agrupar facturas
    del sistema en una sola retencion.'''

    PRECISION_DP = dp.get_precision('Account')

    amount_ice = fields.Float(
        string='ICE', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_vat = fields.Float(
        string='Base 12 %', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_untaxed = fields.Float(
        string='Untaxed', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Float(
        string='Tax', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Float(
        string='Total a Pagar', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_pay = fields.Float(
        string='Total', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_noret_ir = fields.Float(
        string='Monto no sujeto a IR', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_tax_retention = fields.Float(
        string='Total Retenciones', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_tax_ret_ir = fields.Float(
        string='Base IR', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    taxed_ret_ir = fields.Float(
        string='Impuesto IR', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_tax_ret_vatb = fields.Float(
        string='Base Ret. IVA', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    taxed_ret_vatb = fields.Float(
        string='Retencion en IVA', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_tax_ret_vatsrv = fields.Float(
        string='Base Ret. IVA', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    taxed_ret_vatsrv = fields.Float(
        string='Retencion en IVA', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_vat_cero = fields.Float(
        string='Base IVA 0%', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    amount_novat = fields.Float(
        string='Base No IVA', digits_compute=PRECISION_DP,
        store=True, readonly=True, compute='_compute_amount')
    retention_id = fields.Many2one(
        'account.retention',
        string='Retención de Impuestos',
        store=True, readonly=True,
        copy=False
    )
    has_retention = fields.Boolean(
        compute='_check_retention',
        string="Tiene Retención en IR",
        store=True,
        readonly=True
        )
    type = fields.Selection(
        [
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Supplier Invoice'),
            ('out_refund', 'Customer Refund'),
            ('in_refund', 'Supplier Refund'),
            ('liq_purchase', 'Liquidacion de Compra')
        ], 'Type', readonly=True, select=True, change_default=True)
    withholding_number = fields.Integer(
        'Num. Retención',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False
    )
    create_retention_type = fields.Selection(
        [('auto', 'Electrónico'),
         ('manual', 'Manual')],
        string='Numerar Retención',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='auto'
    )
    reference = fields.Char(copy=False)

    @api.onchange('auth_inv_id')
    def _onchange_auth(self):
        if self.auth_inv_id and not self.auth_inv_id.is_electronic:
                self.auth_number = self.auth_inv_id.name

    @api.multi
    def _check_invoice_number(self):
        """Método de validacion de numero de factura y numero de
        retencion

        número de factura: suppplier_invoice_number
        número de retención: withdrawing_number
        """
        INV_LIMIT = 9  # CHECK: mover a compañia ?

        for obj in self:
            if obj.state in ['open', 'paid', 'cancel']:
                return True
            if obj.type == 'out_invoice':
                return True
            if not len(obj.supplier_invoice_number) == INV_LIMIT:
                raise UserError('Error', u'Son %s dígitos en el núm. de Factura.' % INV_LIMIT)  # noqa

            auth = obj.auth_inv_id

            inv_number = obj.supplier_invoice_number

            if not auth:
                raise except_orm(
                    'Error!',
                    u'No se ha configurado una autorización de documentos, revisar Partner y Diario Contable.'  # noqa
                )

            if not self.env['account.authorisation'].is_valid_number(auth.id, int(inv_number)):  # noqa
                raise UserError('Error!', u'Número de factura fuera de rango.')

            # validacion de numero de retencion para facturas de proveedor
            if obj.type == 'in_invoice':
                if not obj.journal_id.auth_ret_id:
                    raise except_orm(
                        'Error!',
                        u'No ha configurado una autorización de retenciones.'
                    )

                if not self.env['account.authorisation'].is_valid_number(obj.journal_id.auth_ret_id.id, int(obj.withdrawing_number)):  # noqa
                    raise except_orm(
                        'Error!',
                        u'El número de retención no es válido.'
                    )
        return True

    _sql_constraints = [
        (
            'unique_inv_supplier',
            'unique(reference,type,partner_id)',
            u'El número de factura es único.'
        )
    ]

    @api.multi
    def action_cancel_draft(self):
        """
        Redefinicion de metodo para cancelar la retencion asociada.
        En facturacion electronica NO se puede borrar el documento.
        Redefinicion de metodo para borrar la retencion asociada.
        TODO: reversar secuencia si fue auto ?
        """
        for inv in self:
            if inv.retention_id:
                inv.retention_id.action_draft()
        super(Invoice, self).action_cancel_draft()
        return True

    @api.multi
    def action_retention_create(self):
        """
        Este método genera el documento de retencion en varios escenarios
        considera casos de:
        * Generar retencion automaticamente
        * Generar retencion de reemplazo
        * Cancelar retencion generada
        """
        TYPES_TO_VALIDATE = ['in_invoice', 'liq_purchase']
        for inv in self:
            if not self.has_retention:
                continue

            if inv.type in ['in_invoice', 'liq_purchase'] and not inv.journal_id.auth_ret_id:  # noqa
                raise except_orm(
                    'Error',
                    'No ha configurado la autorización de retenciones en el diario.'  # noqa
                )

            wd_number = False

            if inv.create_retention_type == 'auto':
                sequence = inv.journal_id.auth_ret_id.sequence_id
                wd_number = self.env['ir.sequence'].get(sequence.code)
            else:
                if inv.withdrawing_number <= 0:
                    raise except_orm(_('Error!'),
                                     u'El número de retención es incorrecto.')
                wd_number = inv.withdrawing_number  # TODO: validate number

            tids = [l.id for l in inv.tax_line_ids if l.tax_id.tax_group_id.code in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']]  # noqa
            account_invoice_tax = self.env['account.invoice.tax'].browse(tids)

            if inv.retention_id:
                account_invoice_tax.write({
                    'retention_id': inv.retention_id.id,
                    'num_document': inv.invoice_number
                })
                inv.retention_id.action_validate(wd_number)
                continue

            withdrawing_data = {
                'partner_id': inv.partner_id.id,
                'name': wd_number,
                'invoice_id': inv.id,
                'auth_id': inv.journal_id.auth_ret_id.id,
                'type': inv.type,
                'in_type': 'ret_%s' % inv.type,
                'date': inv.date_invoice,
                'num_document': self.invoice_number,
                'manual': False
            }

            withdrawing = self.env['account.retention'].create(withdrawing_data)  # noqa

            account_invoice_tax.write({'retention_id': withdrawing.id, 'num_document': inv.reference})  # noqa

            if inv.type in TYPES_TO_VALIDATE:
                withdrawing.action_validate(wd_number)

            inv.write({'retention_id': withdrawing.id})
        return True

    @api.multi
    def action_retention_cancel(self):
        """
        TODO: revisar si este metodo debe llamarse desde el cancelar
        factura
        """
        for inv in self:
            if inv.retention_id:
                inv.retention_id.action_cancel()
        return True

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):  # noqa
        new_invoices = super(Invoice, self).refund(date_invoice, date, description, journal_id)  # noqa
        new_invoices._onchange_journal_id()
        return new_invoices


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    def _set_taxes(self):
        """
        Redefinicion para leer impuestos desde category_id
        TODO: leer impuestos desde category_id
        """
        super(AccountInvoiceLine, self)._set_taxes()


class AccountInvoiceTax(models.Model):

    _inherit = 'account.invoice.tax'

    fiscal_year = fields.Char(
        'Ejercicio Fiscal',
        size=4,
        default=time.strftime('%Y')
    )
    group_id = fields.Many2one(
        related='tax_id.tax_group_id',
        store=True,
        string='Grupo'
    )
    percent = fields.Char(related='tax_id.porcentaje', string='% Aplicado')
    code = fields.Char(related='tax_id.description', string='Código')
    retention_id = fields.Many2one(
        'account.retention',
        'Retención',
        select=True
    )

    @api.onchange('tax_id')
    def _onchange_tax(self):
        if not self.tax_id:
            return
        self.name = self.tax_id.description
        self.account_id = self.tax_id.account_id and self.tax_id.account_id.id
        self.amount = self.tax_id.compute_all(self.invoice_id.amount_untaxed)['taxes'][0]['amount']  # noqa


class AccountInvoiceRefund(models.TransientModel):

    _inherit = 'account.invoice.refund'

    @api.model
    def _get_reason(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if not active_id:
            return ''
        inv = self.env['account.invoice'].browse(active_id)
        return inv.invoice_number

    description = fields.Char(default=_get_reason)
