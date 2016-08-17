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
    Warning as UserError,
    RedirectWarning
    )
import openerp.addons.decimal_precision as dp

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}


class Invoice(models.Model):

    _inherit = 'account.invoice'
    __logger = logging.getLogger(_inherit)

    @api.multi
    def print_invoice(self):
        # Método para imprimir reporte de liquidacion de compra
        datas = {'ids': [self.id], 'model': 'account.invoice'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'invoice_report',
            'model': 'account.invoice',
            'datas': datas,
            'nodestroy': True,
            }

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
            raise UserError('Aviso', u'No tiene retención')
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.retention',
            'model': 'account.retention',
            'datas': datas,
            'nodestroy': True,
        }

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)  # noqa
        for line in self.tax_line_ids:
            if line.tax_group == 'vat':
                self.amount_vat += line.base
                self.amount_tax += line.amount
            elif line.tax_group == 'vat0':
                self.amount_vat_cero += line.base
            elif line.tax_group == 'novat':
                self.amount_novat += line.base
            elif line.tax_group == 'no_ret_ir':
                self.amount_noret_ir += line.base
            elif line.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:
                self.amount_tax_retention += line.amount
                if line.tax_group == 'ret_vat_b':
                    self.amount_tax_ret_vatb += line.base
                    self.taxed_ret_vatb += line.amount
                elif line.tax_group == 'ret_vat_srv':
                    self.amount_tax_ret_vatsrv += line.base
                    self.taxed_ret_vatsrv += line.amount
                elif line.tax_group == 'ret_ir':
                    self.amount_tax_ret_ir += line.base
                    self.taxed_ret_ir += line.amount
            elif line.tax_group == 'ice':
                self.amount_ice += line.amount
        if self.amount_vat == 0 and self.amount_vat_cero == 0:
        # base vat not defined, amount_vat by default
            self.amount_vat_cero = self.amount_untaxed
        self.amount_total = self.amount_untaxed + self.amount_tax + self.amount_tax_retention  # noqa
        self.amount_pay = self.amount_tax + self.amount_untaxed

    @api.multi
    def name_get(self):
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Supplier Invoice'),
            'out_refund': _('Refund'),
            'in_refund': _('Supplier Refund'),
            'liq_purchase': _('Liquid. de Compra')
        }
        result = []
        for inv in self:
            result.append((inv.id, "%s %s" % (inv.number or TYPES[inv.type], inv.name or '')))  # noqa
        return result

    @api.one
    @api.depends('tax_line_ids.tax_group')
    def _check_retention(self):
        for inv in self:
            for tax in inv.tax_line_ids:
                if tax.tax_group in ['ret_vat_b', 'ret_vat_srv']:
                    self.retention_vat = True
                elif tax.tax_group == 'ret_ir':
                    self.retention_ir = True
                elif tax.tax_group == 'no_ret_ir':
                    self.no_retention_ir = True

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
    retention_ir = fields.Boolean(
        compute='_check_retention',
        string="Tiene Retención en IR",
        store=True,
        readonly=True,
        )
    retention_vat = fields.Boolean(
        compute='_check_retention',
        string='Tiene Retencion en IVA',
        store=True,
        readonly=True,
        )
    no_retention_ir = fields.Boolean(
        string='No objeto de Retención',
        store=True, readonly=True, compute='_check_retention')
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
    sustento_id = fields.Many2one(
        'account.ats.sustento',
        string='Sustento del Comprobante'
    )

    @api.multi
    def onchange_journal_id(self, journal_id=False):
        # Método redefinido para cargar la autorizacion de facturas de venta
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)

            if self.type == 'out_invoice' and not journal.auth_id:
                return {
                    'warning': {
                        'title': 'Error',
                        'message': u'No se ha configurado una autorización en este diario.'  # noqa
                        }
                    }
            return {
                'value': {
                    'currency_id': journal.currency.id or journal.company_id.currency_id.id,  # noqa
                    'company_id': journal.company_id.id,
                    'auth_inv_id': journal.auth_id.id
                }
            }
        return {}

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

    _constraints = [
        (
            _check_invoice_number,
            u'Número fuera de rango de autorización activa.',
            [u'Número Factura']
        ),
    ]

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
        Redefinicion de metodo para borrar la retencion asociada.
        CHECK: saber si es correcto eliminar o hacer cache del
        numero del documento.
        """
        for inv in self:
            if inv.retention_id:
                inv.retention_id.unlink()
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

            if not (inv.retention_ir or inv.retention_vat):
                continue

            if inv.create_retention_type == 'no_retention':
                continue

            wd_number = False

            if inv.create_retention_type == 'auto':
                sequence = inv.journal_id.auth_ret_id.sequence_id
                wd_number = self.env['ir.sequence'].get(sequence.code)
            else:
                if inv.withdrawing_number <= 0:
                    raise except_orm(_('Error!'),
                                     u'El número de retención es incorrecto.')
                wd_number = inv.withdrawing_number  # TODO: validate number

            if inv.retention_id:
                inv.retention_id.action_validate(wd_number)
                continue

            if inv.type in ['in_invoice', 'liq_purchase'] and not inv.journal_id.auth_ret_id:  # noqa
                raise except_orm(
                    'Error',
                    'No ha configurado la autorización de retenciones en el diario.'  # noqa
                )

            withdrawing_data = {
                'partner_id': inv.partner_id.id,
                'name': wd_number,
                'invoice_id': inv.id,
                'auth_id': inv.journal_id.auth_ret_id.id,
                'type': inv.type,
                'in_type': 'ret_%s' % inv.type,
                'date': inv.date_invoice,
                'num_document': self.invoice_number,
            }

            withdrawing = self.env['account.retention'].create(withdrawing_data)  # noqa

            tids = [l.id for l in inv.tax_line_ids if l.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']]  # noqa
            account_invoice_tax = self.env['account.invoice.tax'].browse(tids)
            account_invoice_tax.write({'retention_id': withdrawing.id, 'num_document': inv.supplier_invoice_number})  # noqa

            if inv.type in TYPES_TO_VALIDATE:
                withdrawing.action_validate(wd_number)

            inv.write({'retention_id': withdrawing.id})
        return True

    @api.multi
    def recreate_retention(self):
        """Método que implementa la recreacion de la retención
        TODO: recibir el numero de retención del campo manual
        """
        self._context.update({'recreate_retention': True})
        for inv in self:
            self.action_retention_cancel()
            self.action_retention_create([inv.id])
        return True

    @api.multi
    def action_retention_cancel(self):
        for inv in self:
            if inv.retention_id:
                inv.retention_id.action_cancel()
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def move_line_get(self, invoice_id):
        inv = self.env['account.invoice'].browse(invoice_id)
        currency = inv.currency_id.with_context(date=inv.date_invoice)
        company_currency = inv.company_id.currency_id

        res = []
        for line in inv.invoice_line_ids:
            mres = self.move_line_get_item(line)
            mres['invl_id'] = line.id
            res.append(mres)
            tax_code_found = False
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, inv.partner_id)['taxes']
            for tax in taxes:
                if inv.type in ('out_invoice', 'in_invoice', 'liq_purchase'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = tax['price_unit'] * line.quantity * tax['base_sign']  # noqa
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = tax['price_unit'] * line.quantity * tax['ref_base_sign']  # noqa

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(line))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = currency.compute(tax_amount, company_currency)  # noqa
        return res

    @api.multi
    def product_id_change(self, product, uom_id, qty=0,
                          name='', type='out_invoice',
                          partner_id=False, fposition_id=False,
                          price_unit=False, currency_id=False,
                          company_id=None):
        context = self._context
        company_id = company_id if company_id is not None else context.get('company_id', False)  # noqa
        self = self.with_context(company_id=company_id, force_company=company_id)  # noqa

        if not partner_id:
            raise except_orm(_('No Partner Defined!'), _("You must first select a partner!"))  # noqa
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain': {'uos_id': []}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain': {'uos_id': []}}

        values = {}

        part = self.env['res.partner'].browse(partner_id)
        fpos = self.env['account.fiscal.position'].browse(fposition_id)

        if part.lang:
            self = self.with_context(lang=part.lang)
        product = self.env['product.product'].browse(product)

        values['name'] = product.partner_ref
        if type in ['out_invoice', 'out_refund']:
            account = product.property_account_income or product.categ_id.property_account_income_categ  # noqa
        else:
            account = product.property_account_expense or product.categ_id.property_account_expense_categ  # noqa
        account = fpos.map_account(account)
        if account:
            values['account_id'] = account.id

        if type in ('out_invoice', 'out_refund'):
            taxes = product.taxes_id or account.tax_ids
            if product.description_sale:
                values['name'] += '\n' + product.description_sale
        else:
            taxes = product.supplier_taxes_id or account.tax_ids
            if product.description_purchase:
                values['name'] += '\n' + product.description_purchase

        taxes = fpos.map_tax(taxes)
        values['invoice_line_tax_id'] = taxes.ids

        if type in ('in_invoice', 'in_refund'):
            values['price_unit'] = price_unit or product.standard_price
        else:
            values['price_unit'] = product.list_price

        values['uos_id'] = product.uom_id.id
        if uom_id:
            uom = self.env['product.uom'].browse(uom_id)
            if product.uom_id.category_id.id == uom.category_id.id:
                values['uos_id'] = uom_id

        domain = {'uos_id': [('category_id', '=', product.uom_id.category_id.id)]}  # noqa

        company = self.env['res.company'].browse(company_id)
        currency = self.env['res.currency'].browse(currency_id)

        if company and currency:
            if company.currency_id != currency:
                if type in ('in_invoice', 'in_refund'):
                    values['price_unit'] = product.standard_price
                values['price_unit'] = values['price_unit'] * currency.rate

            if values['uos_id'] and values['uos_id'] != product.uom_id.id:
                values['price_unit'] = self.env['product.uom']._compute_price(
                    product.uom_id.id, values['price_unit'], values['uos_id'])

        return {'value': values, 'domain': domain}
