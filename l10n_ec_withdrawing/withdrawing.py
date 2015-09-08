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

import time
import logging

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Supplier Invoice
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Supplier Refund
}

class AccountWithdrawing(models.Model):

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.name
            res.append((record.id, name))
        return res

    @api.one
    @api.depends('tax_ids.amount')
    def _amount_total(self):
        total = 0
        self.amount_total = sum(tax.amount for tax in ret.tax_ids)

    def _get_period(self, cr, uid, ids, fields, args, context):
        res = {}
        period_obj = self.pool.get('account.period')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = period_obj.find(cr, uid, obj.date)[0]
        return res

    STATES_VALUE = {'draft': [('readonly', False)]}

    _name = 'account.retention'
    _description = 'Withdrawing Documents'
    _order = 'date desc, name desc'

    name = fields.Char(
        'Número',
        size=64,
        readonly=True,
        required=True,
        states=STATES_VALUE
        )
    manual = fields.Boolean(
        'Numeración Manual',
        readonly=True,
        states=STATES_VALUE
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
        states=STATES_VALUE,
        readonly=True
        )
    in_type = fields.Selection(
        [('ret_in_invoice', u'Retención a Proveedor'),
        ('ret_out_invoice', u'Retención de Cliente')],
        string='Tipo',
        states=STATES_VALUE,
        readonly=True
        )
    date = fields.Date(
        'Fecha Emision',
        readonly=True,
        states={'draft': [('readonly', False)]}, required=True)
    period_id = fields.Many2one(
        'account.period',
        'Periodo',
        required=True
        )
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
        readonly=True 
	)
    move_id = fields.Many2one(
        related='invoice_id.move_id',
        string='Asiento Contable',
        readonly=True
        )
    state = fields.Selection(
        [('draft','Borrador'),
        ('early','Anticipado'),
        ('done','Validado'),
        ('cancel','Anulado')],
        readonly=True,
        string='Estado'
        )
    amount_total = fields.Float(
        compute='_amount_total',
        string='Total',
        store=True,
        digits_compute=dp.get_precision('Account')
        )
    to_cancel = fields.Boolean(
        'Para anulación',
        readonly=True,
        states=STATES_VALUE
        )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        change_default=True,
        readonly=True,
        states={'draft':[('readonly',False)]}
        )

    def _get_period(self, cr, uid, context=None):
        res = self.pool.get('account.period').find(cr, uid, context=context)
        return res and res[0] or False

    def _get_type(self, cr, uid, context):
        if context.has_key('type') and \
        context['type'] in ['in_invoice', 'out_invoice']:
            return 'in_invoice'
        else:
            return 'liq_purchase'

    def _get_in_type(self, cr, uid, context):
        if context.has_key('type') and \
        context['type'] in ['in_invoice', 'liq_purchase']:
            return 'ret_in_invoice'
        else:
            return 'ret_in_invoice'        

    _defaults = {
        'state': 'draft',
        'in_type': _get_in_type,
        'type': _get_type,
        'name': '/',
        'manual': True,
        'date': time.strftime('%Y-%m-%d'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
        'period_id': _get_period
        }

    _sql_constraints = [('unique_number_name', 'unique(name)', u'El número de retención es único.')]

    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state in ['done']:
                raise osv.except_osv('Aviso','No se permite borrar retenciones validadas.')
        res = super(AccountWithdrawing, self).unlink(cr, uid, ids, context)
        return res

    @api.multi
    def onchange_invoice(self, invoice):
        res = {'value': {'num_document': ''}}
        if not invoice:
            return res
        if not invoice.auth_inv_id:
            return res
        num_document = invoice.supplier_number
        res['value']['num_document'] = num_document
        res['value']['type'] = invoice.type
        return res

    def button_validate(self, cr, uid, ids, context=None):
        """
        Botón de validación de Retención que se usa cuando
        se creó una retención manual, esta se relacionará
        con la factura seleccionada.
        """
        invoice_obj = self.pool.get('account.invoice')
        if context is None:
            context = {}
        for ret in self.browse(cr, uid, ids, context):
            if ret.manual:
                self.action_validate(cr, uid, [ret.id], ret.name)
                invoice_obj.write(cr, uid, ret.invoice_id.id, {'retention_id': ret.id})
            else:
                self.action_validate(cr, uid, [ret.id])
        return True

    def action_validate(self, cr, uid, ids, number=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado
        number: Numero posible para usar en el documento

        Metodo que valida el documento, su principal
        accion es numerar el documento segun el parametro number
        '''
        seq_obj = self.pool.get('ir.sequence')
        for ret in self.browse(cr, uid, ids):
            if ret.to_cancel:
                raise osv.except_osv('Alerta', 'El documento fue marcado para anular.')
            seq_id = ret.invoice_id.journal_id.auth_ret_id.sequence_id.id
            seq = seq_obj.browse(cr, uid, seq_id)
            ret_num = number
            if number is None:
                ret_number = seq_obj.get(cr, uid, seq.code)
            else:
                padding = seq.padding
                ret_number = str(number).zfill(padding)
            self._amount_total(cr, uid, [ret.id], [], {}, {})                
            number = ret.auth_id.serie_entidad + ret.auth_id.serie_emision + ret_number
            self.write(cr, uid, ret.id, {'state': 'done', 'name':number})
            self.log(cr, uid, ret.id, _("La retención %s fue generada.") % number)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para cambiar de estado a cancelado
        el documento
        '''
        auth_obj = self.pool.get('account.authorisation')
        for ret in self.browse(cr, uid, ids):
            data = {'state': 'cancel'}
            if ret.to_cancel:
                if len(ret.name) == 9 and auth_obj.is_valid_number(cr, uid, ret.auth_id.id, int(ret.name)):
                    number = ret.auth_id.serie_entidad + ret.auth_id.serie_emision + ret.name
                    data.update({'name': number})
                else:
                    raise osv.except_osv('Error', u'El número no es de 9 dígitos y/o no pertenece a la autorización seleccionada.')
            self.write(cr, uid, ret.id, data)
        return True

    def action_draft(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            name = obj.name[6:]
            self.write(cr, uid, ids, {'state': 'draft', 'name': name}, context)
        return True

    def action_early(self, cr, uid, ids, *args):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para cambiar de estado a cancelado
        el documento
        '''        
        self.write(cr, uid, ids, {'state': 'early'})
        return True        


class AccountInvoiceTax(models.Model):

    _inherit = 'account.invoice.tax'

    fiscal_year = fields.Char('Ejercicio Fiscal', size = 4)
    tax_group = fields.Selection([('vat','IVA Diferente de 0%'),
                                        ('vat0','IVA 0%'),
                                        ('novat','No objeto de IVA'),
                                        ('ret_vat_b', 'Retención de IVA (Bienes)'),
                                        ('ret_vat_srv', 'Retención de IVA (Servicios)'),
                                        ('ret_ir', 'Ret. Imp. Renta'),
                                        ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'), 
                                        ('imp_ad', 'Imps. Aduanas'),
                                        ('ice', 'ICE'),
                                        ('other','Other')], 'Grupo', required=True)
    percent = fields.Char('Porcentaje', size=20)
    num_document = fields.Char('Num. Comprobante', size=50)
    retention_id = fields.Many2one('account.retention', 'Retención', select=True)

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
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
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                    'tax_group': tax['tax_group'],
                    'percent': tax['porcentaje'],
				}
                # Hack to EC
                if tax['tax_group'] in ['ret_vat_b', 'ret_vat_srv']:
                    ret = float(str(tax['porcentaje'])) / 100
                    bi = tax['price_unit'] * line['quantity']
                    imp = (abs(tax['amount']) / (ret * bi)) * 100
                    val['base'] = (tax['price_unit'] * line['quantity']) * imp / 100
                else:
                    val['base'] = tax['price_unit'] * line['quantity']

                if inv.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or fields.date.context_today(self, cr, uid, context=context)}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or fields.date.context_today(self, cr, uid, context=context)}, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or fields.date.context_today(self, cr, uid, context=context)}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or fields.date.context_today(self, cr, uid, context=context)}, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped

    _defaults = {
        'fiscal_year': time.strftime('%Y'),
    }


class Invoice(models.Model):
    
    _inherit = 'account.invoice'
    __logger = logging.getLogger(_inherit)

    @api.multi
    def onchange_company_id(self, company_id, part_id, type, invoice_line, currency_id):
        # TODO: add the missing context parameter when forward-porting in trunk
        # so we can remove this hack!
        self = self.with_context(self.env['res.users'].context_get())

        values = {}
        domain = {}

        if company_id and part_id and type:
            acc_id = False
            p = self.env['res.partner'].browse(part_id)
            if p.property_account_payable and p.property_account_receivable and \
                    p.property_account_payable.company_id.id != company_id and \
                    p.property_account_receivable.company_id.id != company_id:
                prop = self.env['ir.property']
                rec_dom = [('name', '=', 'property_account_receivable'), ('company_id', '=', company_id)]
                pay_dom = [('name', '=', 'property_account_payable'), ('company_id', '=', company_id)]
                res_dom = [('res_id', '=', 'res.partner,%s' % part_id)]
                rec_prop = prop.search(rec_dom + res_dom) or prop.search(rec_dom)
                pay_prop = prop.search(pay_dom + res_dom) or prop.search(pay_dom)
                rec_account = rec_prop.get_by_record(rec_prop)
                pay_account = pay_prop.get_by_record(pay_prop)				
                if not rec_account and not pay_account:
                    action = self.env.ref('account.action_account_config')
                    msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                    raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

                if type in ('out_invoice', 'out_refund'):
                    acc_id = rec_account.id
                else:
                    acc_id = pay_account.id
                values = {'account_id': acc_id}
				
            if self:
                if company_id:
                    for line in self.invoice_line:
                        if not line.account_id:
                            continue
                        if line.account_id.company_id.id == company_id:
                            continue
                        accounts = self.env['account.account'].search([('name', '=', line.account_id.name), ('company_id', '=', company_id)])
                        if not accounts:
                            action = self.env.ref('account.action_account_config')
                            msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                            raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
                        line.write({'account_id': accounts[-1].id})
            else:
                for line_cmd in invoice_line or []:
                    if len(line_cmd) >= 3 and isinstance(line_cmd[2], dict):
                        line = self.env['account.account'].browse(line_cmd[2]['account_id'])
                        if line.company_id.id != company_id:
                            raise except_orm(
                                _('Configuration Error!'),
                                _("Invoice line account's company and invoice's company does not match.")
                            )

        if company_id and type:
            journal_type = TYPE2JOURNAL[type]			
            journals = self.env['account.journal'].search([('type', '=', journal_type), ('company_id', '=', company_id)])
            if journals:
                values['journal_id'] = journals[0].id
            journal_defaults = self.env['ir.values'].get_defaults_dict('account.invoice', 'type=%s' % type)
            if 'journal_id' in journal_defaults:
                values['journal_id'] = journal_defaults['journal_id']
            if not values.get('journal_id'):
                field_desc = journals.fields_get(['type'])
                type_label = next(t for t, label in field_desc['type']['selection'] if t == journal_type)
                journal_type_map = dict(obj_journal._columns['type'].selection)
                journal_type_label = self.pool['ir.translation']._get_source(cr, uid, None, ('code','selection'),
                                                                             context.get('lang'),
                                                                             journal_type_map.get(journal_type))
                raise osv.except_osv(_('Configuration Error!'),
                                     _('Cannot find any account journal of %s type for this company.\n\nYou can create one in the menu: \nConfiguration\Journals\Journals.') % ('"%s"' % journal_type_label))
            domain = {'journal_id':  [('id', 'in', journals.ids)]}

        return {'value': values, 'domain': domain}

    def onchange_sustento(self, cr, uid, ids, sustento_id):
        res = {'value': {}}
        if not sustento_id:
            return res
        sustento = self.pool.get('account.ats.sustento').browse(cr, uid, sustento_id)
        res['value']['name'] = sustento.type
        return res

    def print_invoice(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de liquidacion de compra
        '''        
        if not context:
            context = {}
        invoice = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [invoice.id], 'model': 'account.invoice'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'invoice_report',
            'model': 'account.invoice',
            'datas': datas,
            'nodestroy': True,                        
            }

    def print_move(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir comprobante contable
        '''        
        if not context:
            context = {}
        invoice = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [invoice.move_id.id], 'model': 'account.move'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,                        
            }

    def print_liq_purchase(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de liquidacion de compra
        '''        
        if not context:
            context = {}
        invoice = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [invoice.id], 'model': 'account.invoice'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_liq_purchase',
            'model': 'account.invoice',
            'datas': datas,
            'nodestroy': True,                        
            }

    def print_retention(self, cr, uid, ids, context=None):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para imprimir reporte de retencion
        '''                
        if not context:
            context = {}
        invoice = self.browse(cr, uid, ids, context)[0]
        datas = {'ids' : [invoice.retention_id.id],
                 'model': 'account.retention'}
        if invoice.retention_id:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.retention',
                'model': 'account.retention',
                'datas': datas,
                'nodestroy': True,            
                }
        else:
            raise except_osv('Aviso', 'No tiene retención')

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        for line in self.tax_line:
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
                if line.tax_group == 'ret_vat_b':#in ['ret_vat_b', 'ret_vat_srv']:
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
        # base vat not defined, amount_vat_cero by default
        if self.amount_vat == 0 and self.amount_vat_cero == 0:
            self.amount_vat_cero = self.amount_untaxed
        self.amount_total = self.amount_untaxed + self.amount_tax + self.amount_tax_retention
        self.amount_pay = self.amount_tax + self.amount_untaxed

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        types = {
                'out_invoice': _('Invoice'),
                'in_invoice': _('Supplier Invoice'),
                'out_refund': _('Refund'),
                'in_refund': _('Supplier Refund'),
                'liq_purchase': _('Liquid. de Compra')
                }
        return [(r['id'], '%s %s' % (r['number'] or types[r['type']], r['name'] or '')) for r in self.read(cr, uid, ids, ['type', 'number', 'name'], context, load='_classic_write')]    

    def _check_retention(self, cr, uid, ids, field_name, context, args):
        res = {}
        for inv in self.browse(cr, uid, ids, context):
            res[inv.id] = {
                'retention_ir': False,
                'retention_vat': False,
                'no_retention_ir': False,
                }
            for tax in inv.tax_line:
                if tax.tax_group in ['ret_vat_b', 'ret_vat_srv']:
                    res[inv.id]['retention_vat'] = True
                elif tax.tax_group == 'ret_ir':
                    res[inv.id]['retention_ir'] = True
                elif tax.tax_group == 'no_ret_ir':
                    res[inv.id]['no_retention_ir'] = True
        return res

    def _get_supplier_number(self, cr, uid, ids, fields, args, context):
        res = {}
        for inv in self.browse(cr, uid, ids, context):
            number = '/'
            if inv.type == 'in_invoice' and inv.auth_inv_id:
                n = inv.supplier_invoice_number and inv.supplier_invoice_number.zfill(9) or '*'
                number = ''.join([inv.auth_inv_id.serie_entidad,inv.auth_inv_id.serie_emision,n])
            res[inv.id] = number
        return res

    HELP_RET_TEXT = '''Automatico: El sistema identificara los impuestos y creara la retencion automaticamente, \
    Manual: El usuario ingresara el numero de retencion \
    Agrupar: Podra usar la opcion para agrupar facturas del sistema en una sola retencion.'''

    PRECISION_DP = dp.get_precision('Account')    

    supplier_number = fields.Char(compute='_get_supplier_number', method=True, size=32,
                                           string='Factura de Proveedor', store=True)
    amount_ice = fields.Float(compute='_compute_amount', method=True, digits_compute=PRECISION_DP, string='ICE',
                                      store=True)
    amount_vat = fields.Float(compute='_compute_amount', method=True,
                                      digits_compute=PRECISION_DP, string='Base 12 %', 
                                      store=True)
    amount_untaxed = fields.Float(compute='_compute_amount', method=True,
                                          digits_compute=PRECISION_DP, string='Untaxed',
                                          store=True)
    amount_tax = fields.Float(compute='_compute_amount', method=True,
                                      digits_compute=PRECISION_DP, string='Tax',
                                      store=True)
    amount_total = fields.Float(compute='_compute_amount', method=True,
                                        digits_compute=PRECISION_DP, string='Total a Pagar',
                                        store=True)
    amount_pay = fields.Float(compute='_compute_amount', method=True,
                                      digits_compute=PRECISION_DP, string='Total',
                                      store=True)
    amount_noret_ir = fields.Float(compute='_compute_amount', method=True,
                                           digits_compute=PRECISION_DP, string='Monto no sujeto a IR',
                                           store=True)
    amount_tax_retention = fields.Float(compute='_compute_amount', method=True,
                                                digits_compute=PRECISION_DP, string='Total Retencion',
                                                store=True)
    amount_tax_ret_ir = fields.Float(compute='_compute_amount', method=True,
                                              digits_compute=PRECISION_DP, string='Base IR',
                                              store=True)
    taxed_ret_ir = fields.Float(compute='_compute_amount', method=True,
                                         digits_compute=PRECISION_DP, string='Impuesto IR',
                                         store=True)
    amount_tax_ret_vatb = fields.Float(compute='_compute_amount',
                                                 method=True,
                                                 digits_compute=PRECISION_DP,
                                                 string='Base Ret. IVA',
                                                 store=True)
    taxed_ret_vatb = fields.Float(compute='_compute_amount',
                                            method=True,
                                            digits_compute=PRECISION_DP,
                                            string='Retencion en IVA',
                                            store=True)
    amount_tax_ret_vatsrv = fields.Float(compute='_compute_amount',
                                                   method=True,
                                                   digits_compute=PRECISION_DP, string='Base Ret. IVA',
                                                   store=True)
    taxed_ret_vatsrv = fields.Float(compute='_compute_amount', method=True,
                                              digits_compute=PRECISION_DP,
                                              string='Retencion en IVA',
                                              store=True)    
    amount_vat_cero = fields.Float(compute='_compute_amount', method=True,
                                             digits_compute=PRECISION_DP, string='Base IVA 0%',
                                             store=True)
    amount_novat = fields.Float(compute='_compute_amount', method=True,
                                          digits_compute=PRECISION_DP, string='Base No IVA',
                                          store=True)
    create_retention_type = fields.Selection([('normal','Automatico'),
                                                   ('manual', 'Manual'),
                                                   ('reserve','Num Reservado'),
                                                   ('no_retention', 'No Generar')],
                                                  string='Numerar Retención',
                                                  readonly=True,
                                                  help=HELP_RET_TEXT,
                                                  states = {'draft': [('readonly', False)]})
    auth_inv_id = fields.Many2one('account.authorisation', 'Autorización SRI',
                                        help = 'Autorizacion del SRI para documento recibido',
                                        readonly=True,
                                        states={'draft': [('readonly', False)]})
    retention_id = fields.Many2one('account.retention', store=True,
                                        string='Retención de Impuestos',
                                        readonly=True)
    retention_ir = fields.Boolean(compute='_check_retention', store=True,
                                         string="Tiene Retención en IR",
                                         method=True, type='boolean',
                                         multi='ret')
    retention_vat = fields.Boolean(compute='_check_retention', store=True,
                                          string='Tiene Retencion en IVA',
                                          method=True, type='boolean',
                                          multi='ret')
    no_retention_ir = fields.Boolean(compute='_check_retention', store=True,
                                          string='No objeto de Retención',
                                          method=True, type='boolean',
                                          multi='ret')        
    type = fields.Selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ('liq_purchase','Liquidacion de Compra')
            ],'Type', readonly=True, select=True, change_default=True)
    manual_ret_num = fields.Integer('Num. Retención', readonly=True,
                                         states = {'draft': [('readonly', False)]})
    sustento_id = fields.Many2one('account.ats.sustento',
                                       'Sustento del Comprobante')

    _defaults = {
        'create_retention_type': 'manual',
        }

    def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
        """
        Metodo redefinido para cargar la autorizacion de facturas de venta
        """
        result = {}
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
            company_id = journal.company_id.id

            if context.get('type') == 'out_invoice' and not journal.auth_id:
                return {
                    'warning': {
                        'title': 'Error',
                        'message': u'No se ha configurado una autorización en este diario.'
                        }
                    }
            result = {'value': {
                    'currency_id': currency_id,
                    'company_id': company_id,
                    'auth_inv_id': journal.auth_id.id
                    }
                }
        return result        

    def _check_invoice_number(self, cr, uid, ids):
        """
        Metodo de validacion de numero de factura y numero de
        retencion
        
        numero de factura: suppplier_invoice_number
        numero de retencion: manual_ret_num
        """
        auth_obj = self.pool.get('account.authorisation')
        INV_MIN_LIMIT = 9  # CHECK: mover a compañia ?
        INV_MAX_LIMIT = 15
        LIMITS = [
            INV_MIN_LIMIT,
            INV_MAX_LIMIT
            ]

        for obj in self.browse(cr, uid, ids):
            if obj.state in ['open', 'paid', 'cancel']:
                return True
            if obj.type == 'out_invoice':
                return True
            if not len(obj.supplier_invoice_number) in LIMITS:
                raise osv.except_osv('Error', u'Son %s dígitos en el núm. de Factura.' % INVOICE_LENGTH_LIMIT)

            auth = obj.auth_inv_id

            inv_number = obj.supplier_invoice_number

            if len(obj.supplier_invoice_number) == INV_MAX_LIMIT:
                inv_number = obj.supplier_invoice_number[6:15]
            
            if not auth:
                raise osv.except_osv('Error', u'No se ha configurado una autorización de documentos, revisar Partner y Diario Contable.')

            if not auth_obj.is_valid_number(cr, uid, auth.id, int(inv_number)):
                raise osv.except_osv('Error', u'Número de factura fuera de rango.')

            # validacion de numero de retencion para facturas de proveedor
            if obj.type == 'in_invoice':
                if not obj.journal_id.auth_ret_id:
                    raise except_osv('Error', u'No ha cofigurado una autorización de retenciones.')

                if not auth_obj.is_valid_number(cr, uid, obj.journal_id.auth_ret_id.id, int(obj.manual_ret_num)):
                    raise osv.except_osv('Error', u'El número de retención no es válido.')
        return True

    _constraints = [
        (_check_invoice_number,
        u'Número fuera de rango de autorización activa.', ['Número Factura']),
    ]

    _sql_constraints = [
        ('unique_inv_supplier', 'unique(supplier_invoice_number,type,partner_id)', u'El número de factura es único.'),
    ]    

    def copy_data(self, cr, uid, id, default=None, context=None):
        res = super(Invoice, self).copy_data(cr, uid, id, default, context=context)
        res.update({'reference': False,
                    'auth_inv_id': False,
                    'retention_id': False,
                    'supplier_invoice_number': False,
                    'manual_ret_num': False,
                    'retention_numbers': False})
        return res

    @api.multi
    def onchange_partner_id(self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):   
        res1 = super(Invoice, self).onchange_partner_id(type, partner_id, date_invoice,
                                                        payment_term, partner_bank_id, company_id)
        if res1['value'].has_key('reference_type'):
            res1['value'].pop('reference_type')
        res = self.env['account.authorisation'].search([('partner_id','=',partner_id), ('in_type','=','externo')], limit=1)
        if res:
            res1['value']['auth_inv_id'] = res[0]
        return res1

    @api.multi
    def action_cancel_draft(self, cr, uid, ids, context):
        retention_obj = self.pool.get('account.retention')
        for inv in self.browse(cr, uid, ids, context):
            if inv.retention_id:
                retention_obj.unlink(cr, uid, [inv.retention_id.id], context)
        super(Invoice, self).action_cancel_draft(cr, uid, ids, context)
        return True    

    def action_retention_create(self, cr, uid, ids, *args):
        '''
        @cr: DB cursor
        @uid: active ID user
        @ids: active IDs objects

        Este metodo genera el documento de retencion en varios escenarios
        considera casos de:
        * Generar retencion automaticamente
        * Generar retencion de reemplazo
        * Cancelar retencion generada
        '''
        context = args and args[0] or {}
        invoices = self.browse(cr, uid, ids)
        ret_obj = self.pool.get('account.retention')
        invtax_obj = self.pool.get('account.invoice.tax')
        ret_cache_obj = self.pool.get('account.retention.cache')
        ir_seq_obj = self.pool.get('ir.sequence')
        for inv in invoices:
            num_ret = False
            if inv.create_retention_type == 'no_retention':
                continue
            if inv.retention_id and not inv.retention_vat and not inv.retention_ir:
                num_next = inv.journal_id.auth_ret_id.sequence_id.number_next
                seq = inv.journal_id.auth_ret_id.sequence_id
                if num_next - 1 == int(inv.retention_id.name):
                    ir_seq_obj.write(cr, uid, seq.id, {'number_next': num_next-1})
                else:
                    ret_cache_obj.create(cr, uid, {'name': inv.retention_id.name})
            if inv.type in ['in_invoice', 'liq_purchase'] and (inv.retention_ir or inv.retention_vat):
                if inv.journal_id.auth_ret_id.sequence_id:
                    ret_data = {'name':'/',
                                'number': '/',
                                'invoice_id': inv.id,
                                'num_document': inv.supplier_number,
                                'auth_id': inv.journal_id.auth_ret_id.id,
                                'type': inv.type,
                                'in_type': 'ret_in_invoice',
                                'date': inv.date_invoice,
                                'period_id': inv.period_id.id
                                }
                    ret_id = ret_obj.create(cr, uid, ret_data)
                    for line in inv.tax_line:
                        if line.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:
                            num = inv.supplier_number
                            invtax_obj.write(cr, uid, line.id, {'retention_id': ret_id, 'num_document': num})
                    if num_ret:
                        ret_obj.action_validate(cr, uid, [ret_id], num_ret)
                    elif inv.create_retention_type == 'normal':
                        ret_obj.action_validate(cr, uid, [ret_id])
                    elif inv.create_retention_type == 'manual':
                        if inv.manual_ret_num == 0:
                            raise osv.except_osv('Error', 'El número de retención es incorrecto.')
                        ret_obj.action_validate(cr, uid, [ret_id], inv.manual_ret_num)
                    elif inv.create_retention_type == 'reserve':
                        if inv.retention_numbers:
                            ret_num = ret_cache_obj.get_number(cr, uid, inv.retention_numbers)
                            ret_obj.action_validate(cr, uid, [ret_id], ret_num)
                        else:
                            raise osv.except_osv('Error', 'Corrija el método de numeración de la retención')
                    self.write(cr, uid, [inv.id], {'retention_id': ret_id})
                else:
                    raise osv.except_osv('Error de Configuracion',
                                         'No se ha configurado una secuencia para las retenciones en Compra')
        self._log_event(cr, uid, ids)
        return True

    def recreate_retention(self, cr, uid, ids, context=None):
        '''
        Metodo que implementa la recreacion de la retención
        TODO: recibir el numero de retención del campo manual
        '''
        if context is None:
            context = {}
        context.update({'recreate_retention': True})
        for inv in self.browse(cr, uid, ids, context):
            self.action_retention_cancel(cr, uid, [inv.id], context)
            self.action_retention_create(cr, uid, [inv.id], context)
        return True

    def action_retention_cancel(self, cr, uid, ids, *args):
        invoices = self.browse(cr, uid, ids)
        ret_obj = self.pool.get('account.retention')
        for inv in invoices:
            if inv.retention_id:
                ret_obj.action_cancel(cr, uid, [inv.retention_id.id])
        return True


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def move_line_get(self, invoice_id):
        inv = self.env['account.invoice'].browse(invoice_id)
        currency = inv.currency_id.with_context(date=inv.date_invoice)
        company_currency = inv.company_id.currency_id
		
        res = []
        for line in inv.invoice_line:
            mres = self.move_line_get_item(line)
            mres['invl_id'] = line.id
            res.append(mres)
            tax_code_found= False
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, inv.partner_id)['taxes']
            for tax in taxes:
                if inv.type in ('out_invoice', 'in_invoice', 'liq_purchase'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = tax['price_unit'] * line.quantity * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = tax['price_unit'] * line.quantity * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(dict(mres))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = currency.compute(tax_amount, company_currency)
        return res

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        context = self._context
        company_id = company_id if company_id is not None else context.get('company_id', False)
        self = self.with_context(company_id=company_id, force_company=company_id)
		
        if not partner_id:
			raise except_orm(_('No Partner Defined!'), _("You must first select a partner!"))
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
        if type in ('out_invoice', 'out_refund'):
            account = product.property_account_income or product.categ_id.property_account_income_categ
        else:
            account = product.property_account_expense or product.categ_id.property_account_expense_categ
        account = fpos.map_account(account)
        if account:
            result['account_id'] = account

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
            values['price_unit'] = product.lst_price

        values['uos_id'] = product.uom_id.id
        if uom_id:
            uom = self.env['product.uom'].browse(uom_id)
            if product.uom_id.category_id.id == uom.category_id.id:
                values['uos_id'] = uom_id

        domain = {'uos_id': [('category_id', '=', product.uom_id.category_id.id)]}

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


class AccountInvoiceRefund(models.Model):

    _inherit = 'account.invoice.refund'

    def _get_description(self, cr, uid, context=None):
        number = '/'
        if not context.get('active_id'):
            return number
        invoice = self.pool.get('account.invoice').browse(cr, uid, context.get('active_id'))
        if invoice.type == 'out_invoice':
            number = invoice.number
        else:
            number = invoice.supplier_number
        return number

    _defaults = {
        'description': _get_description,
        }
            
