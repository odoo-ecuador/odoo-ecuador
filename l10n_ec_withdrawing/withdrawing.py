# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2014-Today Cristian Salamea All Rights Reserved
#    Copyright (C) 2015-Today Alcides Rivera <alcides@virtualsami.com.ec>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import json
import time
import logging

from openerp import api, fields, models, _

from openerp.exceptions import UserError, RedirectWarning, ValidationError

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}


class AccountWithdrawing(models.Model):

    @api.multi
    def name_get(self):
        result = []
        for withdrawing in self:
            result.append((withdrawing.id, withdrawing.name))
        return result

    @api.one
    @api.depends('tax_ids.amount')
    def _amount_total(self):
        self.amount_total = sum(tax.amount for tax in self.tax_ids)

    @api.multi
    def _get_type(self):
        context = self._context
        if context.has_key('type') and \
        context['type'] in ['in_invoice', 'out_invoice']:
            return 'in_invoice'
        else:
            return 'liq_purchase'

    @api.multi
    def _get_in_type(self):
        context = self._context
        if context.has_key('type') and \
        context['type'] in ['in_invoice', 'liq_purchase']:
            return 'ret_in_invoice'
        else:
            return 'ret_in_invoice'    

    STATES_VALUE = {'draft': [('readonly', False)]}

    _name = 'account.retention'
    _description = 'Withdrawing Documents'
    _order = 'date desc, name desc'

    name = fields.Char(
        'Número',
        size=64,
        readonly=True,
        required=True,
        states=STATES_VALUE,
        default='/'
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
        readonly=True,
        states=STATES_VALUE,
        required=True,
        domain=[('in_type','=','interno')]
        )
    type = fields.Selection(
        [('in_invoice','Factura'),
        ('liq_purchase','Liquidacion Compra')],
        string='Tipo Comprobante',
        readonly=True,
        required=True,
        states=STATES_VALUE,
        default=_get_type
        )
    in_type = fields.Selection(
        [('ret_in_invoice', u'Retención a Proveedor'),
        ('ret_out_invoice', u'Retención de Cliente')],
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
        domain=[('state','=','open')]
        )
    partner_id = fields.Many2one(
        related='invoice_id.partner_id',
        string='Empresa',
        store=True
        )
    move_id = fields.Many2one(
        related='invoice_id.move_id',
        string='Asiento Contable',
        readonly=True,
        store=True
        )
    state = fields.Selection(
        [('draft','Borrador'),
        ('early','Anticipado'),
        ('done','Validado'),
        ('cancel','Anulado')],
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
        states={'draft':[('readonly',False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.invoice')
        )

    _sql_constraints = [('unique_number_name', 'unique(name)', u'El número de retención es único.')]

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.state in ['done']:
                raise Warning(_('No se permite borrar retenciones validadas.'))
        res = super(AccountWithdrawing, self).unlink()
        return res

    @api.multi
    def onchange_invoice(self, invoice_id):
        res = {'value': {'num_document': ''}}
        if not invoice_id:
            return res
        invoice = self.env['account.invoice'].browse(invoice_id)
        if not invoice.auth_inv_id:
            return res
        num_document = invoice.supplier_number
        res['value']['num_document'] = num_document
        res['value']['type'] = invoice.type
        return res

    @api.multi
    def button_validate(self):
        """
        Botón de validación de Retención que se usa cuando
        se creó una retención manual, esta se relacionará
        con la factura seleccionada.
        """
        for ret in self:
            if ret.manual:
                self.action_validate(ret.id, ret.name)
                invoice = self.env['account.invoice'].browse(ret.invoice_id.id)
                invoice.write({'retention_id': ret.id})
            else:
                self.action_validate(ret.id)
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
                raise Warning(_('El documento fue marcado para anular.'))
            sequence = wd.invoice_id.journal_id.auth_ret_id.sequence_id
            if wd.internal_number and not number:
                wd_number = wd.internal_number[6:]
            elif number is None:
                wd_number = self.env['ir.sequence'].get_id(sequence.id)
            else:
                wd_number = str(number).zfill(sequence.padding)
            number = '{0}{1}{2}'.format(wd.auth_id.serie_entidad, wd.auth_id.serie_emision, wd_number)
            wd.write({'state': 'done', 'name': number, 'internal_number': number})
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
                if len(ret.name) == 9 and auth_obj.is_valid_number(ret.auth_id.id, int(ret.name)):
                    number = ret.auth_id.serie_entidad + ret.auth_id.serie_emision + ret.name
                    data.update({'name': number})
                else:
                    raise UserError(_(u'El número no es de 9 dígitos y/o no pertenece a la autorización seleccionada.'))
            self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_draft(self):
        for obj in self:
            name = obj.name[6:]
            self.write({'state': 'draft', 'name': name})
        return True

    @api.multi
    def action_cancel_draft(self):
        """
        Metodo que se ejecuta cuando el registro ha sido anulado
        y el usuario decide volver al estado borrador.
        """
        self.write({'state': 'draft', 'name': '/'})
        return True

    @api.multi
    def action_early(self):
        # Método para cambiar de estado a cancelado el documento
        self.write({'state': 'early'})
        return True        

class AccountInvoiceTax(models.Model):
    _inherit = 'account.invoice.tax'
   
    fiscal_year = fields.Char('Ejercicio Fiscal', size = 4, default=time.strftime('%Y'))
    tax_group = fields.Selection([('vat','IVA Diferente de 0%'),
                                        ('vat0','IVA 0%'),
                                        ('novat','No objeto de IVA'),
                                        ('ret_vat_b', 'Retención de IVA (Bienes)'),
                                        ('ret_vat_srv', 'Retención de IVA (Servicios)'),
                                        ('ret_ir', 'Ret. Imp. Renta'),
                                        ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'), 
                                        ('imp_ad', 'Imps. Aduanas'),
                                        ('ice', 'ICE'),
                                        ('other','Other')], 'Grupo', required=True, default='vat')
    percent = fields.Char('Porcentaje', size=20, default=12)
    num_document = fields.Char('Num. Comprobante', size=50)
    retention_id = fields.Many2one('account.retention', 'Retención', select=True)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    __logger = logging.getLogger(_inherit)

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': self.id,
                    'name': tax['name'],
                    'tax_id': tax['id'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
                    'account_id': self.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or line.account_id.id) or (tax['refund_account_id'] or line.account_id.id),
                    'tax_group': tax['tax_group'],
                    'percent': tax['porcentaje'],
                }
                # Hack to EC
                if tax['tax_group'] in ['ret_vat_b', 'ret_vat_srv']:
                    ret = float(str(tax['porcentaje'])) / 100
                    bi = price_unit * line['quantity']
                    imp = (abs(tax['amount']) / (ret * bi)) * 100
                    val['base'] = (price_unit * line['quantity']) * imp / 100
                else:
                    val['base'] = price_unit * line['quantity']

                # If the taxes generate moves on the same financial account as the invoice line,
                # propagate the analytic account from the invoice line to the tax line.
                # This is necessary in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = tax['id']
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
        return tax_grouped

    #@api.onchange('sustento_id')
    #def _onchange_sustento_id(self):
    #    res = {'value': {}}
    #    if not self.sustento_id:
    #        return res
    #    sustento = self.env['account.ats.sustento'].browse(self.sustento_id)
    #    res['value']['name'] = sustento.type
    #    return res

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
        datas = {'ids': [self.move_id.id], 'model': 'account.move'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,                        
            }

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
        datas = {'ids' : [self.retention_id.id], 'model': 'account.retention'}
        if not self.retention_id:
            raise Warning('Aviso', u'No tiene retención')
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.retention',
            'model': 'account.retention',
            'datas': datas,
            'nodestroy': True,            
        }

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        for line in self.tax_line_ids:
            if line.tax_group == 'vat':
                self.amount_vat += sum(line.price_subtotal for line in self.invoice_line_ids)
                self.amount_tax += line.amount
            elif line.tax_group == 'vat0':
                self.amount_vat_cero += sum(line.price_subtotal for line in self.invoice_line_ids)
            elif line.tax_group == 'novat':
                self.amount_novat += sum(line.price_subtotal for line in self.invoice_line_ids)
            elif line.tax_group == 'no_ret_ir':
                self.amount_noret_ir += sum(line.price_subtotal for line in self.invoice_line_ids)
            elif line.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:
                self.amount_tax_retention += line.amount
                if line.tax_group == 'ret_vat_b':#in ['ret_vat_b', 'ret_vat_srv']:
                    self.amount_tax_ret_vatb += sum(line.price_subtotal for line in self.invoice_line_ids)
                    self.taxed_ret_vatb += line.amount
                elif line.tax_group == 'ret_vat_srv':
                    self.amount_tax_ret_vatsrv += sum(line.price_subtotal for line in self.invoice_line_ids)
                    self.taxed_ret_vatsrv += line.amount                        
                elif line.tax_group == 'ret_ir':
                    self.amount_tax_ret_ir += sum(line.price_subtotal for line in self.invoice_line_ids)
                    self.taxed_ret_ir += line.amount
            elif line.tax_group == 'ice':
                self.amount_ice += line.amount
        # base vat not defined, amount_vat_cero by default
        if self.amount_vat == 0 and self.amount_vat_cero == 0:
            self.amount_vat_cero = self.amount_untaxed
        self.amount_total = self.amount_untaxed + self.amount_tax + self.amount_tax_retention
        self.amount_pay = self.amount_tax + self.amount_untaxed
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            amount_total_company_signed = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    def _get_invoice_line(self, invoice_id):
        result = {}
        for line in self.env['account.invoice.line'].browse(invoice_id):
            result[line.invoice_id.id] = True
        return result.keys()

    @api.multi
    def _get_invoice_tax(self, invoice_id):
        result = {}
        for tax in self.env['account.invoice.tax'].browse(invoice_id):
            result[tax.invoice_id.id] = True
        return result.keys()        
    
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
            result.append((inv.id, "%s %s" % (inv.number or TYPES[inv.type], inv.name or '')))
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

    @api.multi
    def _get_supplier_number(self):
        result = {}
        for inv in self:
            number = '/'
            if inv.type == 'in_invoice' and inv.auth_inv_id:
                n = inv.invoice_number and inv.invoice_number.zfill(9) or '*'
                number = ''.join([inv.auth_inv_id.serie_entidad,inv.auth_inv_id.serie_emision,n])
            result[inv.id] = number
        return result

    HELP_RET_TEXT = '''Automatico: El sistema identificara los impuestos y creara la retencion automaticamente, \
    Manual: El usuario ingresara el numero de retencion \
    Agrupar: Podra usar la opcion para agrupar facturas del sistema en una sola retencion.'''

    invoice_number = fields.Char(string='Invoice Number', size=9)
    supplier_number = fields.Char(string='Factura de Proveedor', 
        size=32, store=True, readonly=True, compute='_get_supplier_number')
    
    amount_ice = fields.Monetary(string='ICE',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_vat = fields.Monetary(string='Base 12 %',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_untaxed = fields.Monetary(string='Untaxed Amount',
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_untaxed_signed = fields.Monetary(string='Untaxed Amount', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax',
        store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Total a Pagar',
        store=True, readonly=True, compute='_compute_amount')
    amount_total_signed = fields.Monetary(string='Total a Pagar', currency_field='currency_id',
        store=True, readonly=True, compute='_compute_amount',
        help="Total amount in the currency of the invoice, negative for credit notes.")
    amount_total_company_signed = fields.Monetary(string='Total a Pagar', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_amount',
        help="Total amount in the currency of the company, negative for credit notes.")
    amount_pay = fields.Monetary(string='Total',
        store=True, readonly=True, compute='_compute_amount')
    amount_noret_ir = fields.Monetary(string='Monto no sujeto a IR',
        store=True, readonly=True, compute='_compute_amount')
    amount_tax_retention = fields.Monetary(string='Total Retenciones',
        store=True, readonly=True, compute='_compute_amount')
    amount_tax_ret_ir = fields.Monetary(string='Base IR',
        store=True, readonly=True, compute='_compute_amount')
    taxed_ret_ir = fields.Monetary(string='Impuesto IR',
        store=True, readonly=True, compute='_compute_amount')
    amount_tax_ret_vatb = fields.Monetary(string='Base Ret. IVA',
        store=True, readonly=True, compute='_compute_amount')
    taxed_ret_vatb = fields.Monetary(string='Retencion en IVA',
        store=True, readonly=True, compute='_compute_amount')
    amount_tax_ret_vatsrv = fields.Monetary(string='Base Ret. IVA',
        store=True, readonly=True, compute='_compute_amount')
    taxed_ret_vatsrv = fields.Monetary(string='Retencion en IVA',
        store=True, readonly=True, compute='_compute_amount')
    amount_vat_cero = fields.Monetary(string='Base IVA 0%',
        store=True, readonly=True, compute='_compute_amount')
    amount_novat = fields.Monetary(string='Base No IVA',
        store=True, readonly=True, compute='_compute_amount')

    auth_inv_id = fields.Many2one('account.authorisation', string='Autorización SRI',
         readonly=True, states={'draft': [('readonly', False)]},
         help = 'Autorizacion del SRI para documento recibido')
    retention_id = fields.Many2one('account.retention', string='Retención de Impuestos',
         store=True, readonly=True)
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
    no_retention_ir = fields.Boolean(string='No objeto de Retención', 
         store=True, readonly=True, compute='_check_retention')
    type = fields.Selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ('liq_purchase','Liquidacion de Compra')
            ],'Type', readonly=True, select=True, change_default=True)
    withdrawing_number = fields.Integer(
        'Num. Retención', 
        readonly=True,
        states = {'draft': [('readonly', False)]}
    )
    create_retention_type = fields.Selection(
        [('auto', 'Automático'),
         ('manual', 'Manual')],
        string='Numerar Retención',
        required=True,
        default='auto'
    )
    sustento_id = fields.Many2one('account.ats.sustento', string='Sustento del Comprobante')

    @api.multi
    def onchange_journal_id(self, journal_id=False):
        # Método redefinido para cargar la autorizacion de facturas de venta
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id
            self.auth_inv_id = self.journal_id.auth_id.id


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
            if not len(obj.invoice_number) ==  INV_LIMIT:
                raise Warning('Error', u'Son %s dígitos en el núm. de Factura.' % INV_LIMIT)

            auth = obj.auth_inv_id

            inv_number = obj.invoice_number

            if not auth:
                raise UserError(_(u'No se ha configurado una autorización de documentos, revisar Partner y Diario Contable.'))

            if not self.env['account.authorisation'].is_valid_number(auth.id, int(inv_number)):
                raise Warning(_('Error!'), _(u'Número de factura fuera de rango.'))

            # validacion de numero de retencion para facturas de proveedor
            if obj.type == 'in_invoice':
                if not obj.journal_id.auth_ret_id:
                    raise UserError(_(u'No ha cofigurado una autorización de retenciones.'))

                if not self.env['account.authorisation'].is_valid_number(obj.journal_id.auth_ret_id.id, int(obj.withdrawing_number)):
                    raise UserError(_(u'El número de retención no es válido.'))
        return True

    _constraints = [
        (_check_invoice_number,
        u'Número fuera de rango de autorización activa.', ['Número Factura']),
    ]

    _sql_constraints = [
        ('unique_inv_supplier', 'unique(invoice_number,auth_inv_id,type,partner_id)', u'El número de factura es único.'),
    ]    

    @api.multi
    def copy_data(self):
        res = super(Invoice, self).copy_data()
        data = {
            'reference': False,
            'auth_inv_id': False,
            'retention_id': False,
            'supplier_invoice_number': False,
            'wthidrawing_number': False,
            'retention_numbers': False
        }
        res.update(data)
        return res

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False, 
            payment_term=False, partner_bank_id=False, company_id=False):    
        res1 = super(Invoice, self).onchange_partner_id(type, partner_id, date_invoice,
                                                        payment_term, partner_bank_id,
                                                        company_id)
        if res1['value'].has_key('reference_type'):
            res1['value'].pop('reference_type')
        res = self.env['account.authorisation'].search([('partner_id','=',partner_id),('in_type','=','externo')], limit=1)
        if res:
            res1['value']['auth_inv_id'] = res[0]
        return res1

    @api.multi
    def action_cancel_draft(self):
        """
        Redefinicion de metodo para borrar la retencion asociada.
        CHECK: saber si es correcto eliminar o hacer cache del
        numero del documento.
        """
        for inv in self:
            if inv.retention_id:
                inv.retention_id.action_cancel_draft()
        super(AccountInvoice, self).action_cancel_draft()
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
        for inv in self:
            if inv.create_retention_type == 'no_retention':
                continue

            wd_number = False            
            if inv.create_retention_type == 'manual':
                if inv.withdrawing_number <= 0:
                    raise UserError(_(u'El número de retención es incorrecto.'))
                wd_number = inv.withdrawing_number                
            
            if inv.retention_id:
                inv.retention_id.action_validate(wd_number)
                continue

            if inv.type == 'out_invoice':
                return True
            if inv.type not in ['in_invoice', 'liq_purchase'] and (inv.retention_ir or inv.retention_vat):
                return True
            if not inv.journal_id.auth_ret_id:
                raise UserError(u'No ha configurado la autorización de retenciones en el diario.')

            withdrawing = self.env['account.retention'].create({
                'name': '/',
                'invoice_id': inv.id,
                'num_document': inv.invoice_number,
                'auth_id': inv.journal_id.auth_ret_id.id,
                'type': inv.type,
                'in_type': 'ret_in_invoice',
                'date': inv.date_invoice,
            })
            tids = [l.id for l in inv.tax_line_ids if l.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']]
            account_invoice_tax = self.env['account.invoice.tax'].browse(tids)
            account_invoice_tax.write({'retention_id': withdrawing.id, 'num_document': inv.invoice_number})

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
