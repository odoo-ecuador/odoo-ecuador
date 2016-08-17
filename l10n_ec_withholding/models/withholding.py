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


class AccountWithdrawing(models.Model):
    """ Implementacion de documento de retencion """

    @api.multi
    def name_get(self):
        """
        TODO
        """
        result = []
        for withdrawing in self:
            result.append((withdrawing.id, withdrawing.name))
        return result

    @api.one
    @api.depends('tax_ids.amount')
    def _amount_total(self):
        """
        TODO
        """
        self.amount_total = sum(tax.amount for tax in self.tax_ids)

    @api.multi
    def _get_period(self):
        result = {}
        for obj in self:
            result[obj.id] = self.env['account.period'].find(obj.date)[0]
        return result

    @api.multi
    def _get_type(self):
        context = self._context
        if 'type' in context and context['type'] in ['in_invoice', 'out_invoice']:  # noqa
            return 'in_invoice'
        else:
            return 'liq_purchase'

    @api.multi
    def _get_in_type(self):
        context = self._context
        if 'type' in context and context['type'] in ['in_invoice', 'liq_purchase']:  # noqa
            return 'ret_in_invoice'
        else:
            return 'ret_out_invoice'

    STATES_VALUE = {'draft': [('readonly', False)]}

    _name = 'account.retention'
    _description = 'Withdrawing Documents'
    _order = 'date ASC'

    name = fields.Char(
        'Número',
        size=64,
        readonly=True,
        required=True,
        states=STATES_VALUE
        )
    internal_number = fields.Char(
        'Número Interno',
        size=64,
        readonly=True,
        required=True,
        default='/'
        )
    manual = fields.Boolean(
        'Numeración Manual',
        readonly=True,
        states=STATES_VALUE,
        default=True
        )
    num_document = fields.Char(
        'Num. Comprobante',
        size=50,
        readonly=True,
        states=STATES_VALUE
        )
    auth_id = fields.Many2one(
        'account.authorisation',
        'Autorizacion',
        required=True,
        readonly=True,
        states=STATES_VALUE,
        domain=[('in_type', '=', 'interno')]
        )
    type = fields.Selection(
        related='invoice_id.type',
        string='Tipo Comprobante',
        readonly=True,
        store=True
        )
    in_type = fields.Selection(
        [
            ('ret_in_invoice', u'Retención a Proveedor'),
            ('ret_out_invoice', u'Retención de Cliente')
        ],
        string='Tipo',
        states=STATES_VALUE,
        readonly=True,
        default=_get_in_type
        )
    date = fields.Date(
        'Fecha Emision',
        readonly=True,
        states={'draft': [('readonly', False)]}, required=True)
    tax_ids = fields.One2many(
        'account.invoice.tax',
        'retention_id',
        'Detalle de Impuestos',
        readonly=True,
        states=STATES_VALUE
        )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Documento',
        required=False,
        readonly=True,
        states=STATES_VALUE,
        domain=[('state', '=', 'open')]
        )
    partner_id = fields.Many2one(
        'res.partner',
        string='Empresa',
        required=True,
        readonly=True,
        states=STATES_VALUE
        )
    move_id = fields.Many2one(
        related='invoice_id.move_id',
        string='Asiento Contable',
        readonly=True,
        store=True
        )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('early', 'Anticipado'),
            ('done', 'Validado'),
            ('cancel', 'Anulado')
        ],
        readonly=True,
        string='Estado',
        default='draft'
        )
    amount_total = fields.Float(
        compute='_amount_total',
        string='Total',
        store=True,
        digits_compute=dp.get_precision('Account')
        )
    to_cancel = fields.Boolean(
        string='Para anulación',
        readonly=True,
        states=STATES_VALUE
        )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        change_default=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.invoice')  # noqa
        )

    _sql_constraints = [
        (
            'unique_number_partner',
            'unique(name,partner_id,type)',
            u'El número de retención es único.'
        )
    ]

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.state in ['done']:
                raise UserError('No se permite borrar retenciones validadas.')
        res = super(AccountWithdrawing, self).unlink()
        return res

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.name = self.name.zfill(9)

    @api.onchange('to_cancel')
    def onchange_tocancel(self):
        if self.to_cancel:
            self.partner_id = self.company_id.partner_id.id

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if not self.invoice_id:
            return
        self.num_document = self.invoice_id.invoice_number
        self.type = self.invoice_id.type

    @api.multi
    def button_validate(self):
        """
        Botón de validación de Retención que se usa cuando
        se creó una retención manual, esta se relacionará
        con la factura seleccionada.
        """
        for ret in self:
            if ret.manual:
                self.action_validate(ret.name)
                invoice = self.env['account.invoice'].browse(ret.invoice_id.id)
                invoice.write({'retention_id': ret.id})
            else:
                self.action_validate()
        return True

    @api.multi
    def action_validate(self, number=None):
        """
        number: Número posible para usar en el documento

        Método que valida el documento, su principal
        accion es numerar el documento segun el parametro number
        """
        for wd in self:
            if wd.to_cancel:
                raise UserError('El documento fue marcado para anular.')
            sequence = wd.invoice_id.journal_id.auth_ret_id.sequence_id
            if wd.internal_number and not number:
                wd_number = wd.internal_number[6:]
            elif number is None:
                wd_number = self.env['ir.sequence'].get_id(sequence.id)
            else:
                wd_number = str(number).zfill(sequence.padding)
            number = '{0}{1}{2}'.format(wd.auth_id.serie_entidad,
                                        wd.auth_id.serie_emision,
                                        wd_number)
            wd.write({'state': 'done',
                      'name': number,
                      'internal_number': number})
        return True

    @api.multi
    def action_cancel(self):
        """
        Método para cambiar de estado a cancelado el documento
        """
        auth_obj = self.env['account.authorisation']
        for ret in self:
            data = {'state': 'cancel'}
            if ret.to_cancel:
                if len(ret.name) == 9 and auth_obj.is_valid_number(ret.auth_id.id, int(ret.name)):  # noqa
                    number = ret.auth_id.serie_entidad + ret.auth_id.serie_emision + ret.name  # noqa
                    data.update({'name': number})
                else:
                    raise except_orm(
                        'Error',
                        u'El número no es de 9 dígitos y/o no pertenece a la autorización seleccionada.'  # noqa
                    )
            self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_early(self):
        # Método para cambiar de estado a cancelado el documento
        self.write({'state': 'early'})
        return True

    @api.multi
    def action_print(self):
        report_name = 'l10n_ec_withdrawing.account_withdrawing'
        datas = {'ids': [self.id], 'model': 'account.retention'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'account.retention',
            'datas': datas,
            'nodestroy': True,
            }


class AccountInvoiceTax(models.Model):

    _inherit = 'account.invoice.tax'

    fiscal_year = fields.Char('Ejercicio Fiscal', size=4)
    tax_group = fields.Selection(
        [
            ('vat', 'IVA Diferente de 0%'),
            ('vat0', 'IVA 0%'),
            ('novat', 'No objeto de IVA'),
            ('ret_vat_b', 'Retención de IVA (Bienes)'),
            ('ret_vat_srv', 'Retención de IVA (Servicios)'),
            ('ret_ir', 'Ret. Imp. Renta'),
            ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'),
            ('imp_ad', 'Imps. Aduanas'),
            ('ice', 'ICE'),
            ('other', 'Other')
        ],
        'Grupo',
        required=True,
        default='vat'
    )
    percent = fields.Char('Porcentaje', size=20)
    retention_id = fields.Many2one(
        'account.retention',
        'Retención',
        select=True
    )

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))  # noqa
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line_ids:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),  # noqa
                    'tax_group': tax['tax_group'],
                    'percent': tax['porcentaje'],
                }
                # Hack to EC
                if tax['tax_group'] in ['ret_vat_b', 'ret_vat_srv']:
                    ret = float(str(tax['porcentaje'])) / 100
                    bi = tax['price_unit'] * line['quantity']
                    imp = (abs(tax['amount']) / (ret * bi)) * 100
                    val['base'] = (tax['price_unit'] * line['quantity']) * imp / 100  # noqa
                else:
                    val['base'] = tax['price_unit'] * line['quantity']

                if invoice.type in ['out_invoice', 'in_invoice']:
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)  # noqa
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)  # noqa
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id  # noqa
                    val['account_analytic_id'] = tax['account_analytic_collected_id']  # noqa
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)  # noqa
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)  # noqa
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id  # noqa
                    val['account_analytic_id'] = tax['account_analytic_paid_id']  # noqa

                # If the taxes generate moves on the same financial account as the invoice line  # noqa
                # and no default analytic account is defined at the tax level, propagate the  # noqa
                # analytic account from the invoice line to the tax line. This is necessary  # noqa
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.  # noqa
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:  # noqa
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])  # noqa
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])
        return tax_grouped

    _defaults = {
        'fiscal_year': time.strftime('%Y'),
    }


class AccountInvoiceRefund(models.Model):

    _inherit = 'account.invoice.refund'

    @api.model
    def _get_description(self):
        number = '/'
        active_id = self._context.get('active_id', False)
        if not active_id:
            return number
        invoice = self.env['account.invoice'].browse(active_id)
        if invoice.type == 'out_invoice':
            number = invoice.number
        else:
            number = invoice.supplier_invoice_number
        return number

    description = fields.Char(default=_get_description)
