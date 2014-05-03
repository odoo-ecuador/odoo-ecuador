# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2013 GnuThink Software All Rights Reserved
#    info@gnuthink.com
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

from osv import osv, fields
from tools import config
from tools.translate import _
from tools import ustr
import decimal_precision as dp
import netsvc


class ProductCategory(osv.Model):
    _inherit = 'product.category'

    _columns = dict(
        taxes_id = fields.many2many('account.tax', 'categ_taxes_rel',
                                    'prod_id', 'tax_id', 'Customer Taxes',
                                    domain=[('parent_id','=',False),('type_tax_use','in',['sale','all'])]),
        supplier_taxes_id = fields.many2many('account.tax',
                                             'categ_supplier_taxes_rel', 'prod_id', 'tax_id',
                                             'Supplier Taxes', domain=[('parent_id', '=', False),('type_tax_use','in',['purchase','all'])]),        
        )

    
class account_retention(osv.osv):
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = record.number
            res.append((record.id, name))
        return res        

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

    def _amount_total(self, cr, uid, ids, field_name, args, context):
        res = {}
        retentions = self.browse(cr, uid, ids, context)
        for ret in retentions:
            total = 0
            for tax in ret.tax_ids:
                total += tax.amount
            res[ret.id] = abs(total)
        return res

    def _get_period(self, cr, uid, ids, fields, args, context):
        res = {}
        period_obj = self.pool.get('account.period')
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = period_obj.find(cr, uid, obj.date)[0]
        return res

    STATES_VALUE = {'draft': [('readonly', False)]}

    _name = 'account.retention'
    _description = 'Withdrawing Documents'
    _order = 'date desc, number desc'

    _columns = {
        'name': fields.char('Número', size=64, readonly=True,
                            required=True,
                            states=STATES_VALUE),
        'number': fields.char('Número', size=64, readonly=True,
                              required=True),
        'manual': fields.boolean('Numeración Manual', readonly=True,
                                 states=STATES_VALUE),
        'num_document': fields.char('Num. Comprobante', size=50,
                                    readonly=True,
                                    states=STATES_VALUE),
        'auth_id': fields.many2one('account.authorisation', 'Autorizacion',
                                   readonly=True,
                                   states=STATES_VALUE,
                                   required=True,
                                   domain=[('in_type','=','interno')]),
        'type': fields.selection([('in_invoice','Factura'),
                                  ('liq_purchase','Liquidacion Compra')],
                                 string='Tipo Comprobante',
                                 readonly=True, states=STATES_VALUE),
        'in_type': fields.selection([('ret_in_invoice',
                                      'Retencion a Proveedor'),
                                     ('ret_out_invoice',
                                      'Retencion de Cliente')],
                                    string='Tipo', states=STATES_VALUE, readonly=True),
        'date': fields.date('Fecha Emision', readonly=True,
                            states={'draft': [('readonly', False)]}, required=True),
        'period_id': fields.many2one('account.period', 'Periodo', required=True),
        'tax_ids': fields.one2many('account.invoice.tax', 'retention_id',
                                   'Detalle de Impuestos', readonly=True,
                                   states=STATES_VALUE),
        'invoice_id': fields.many2one('account.invoice', string='Documento',
                                      required=False,
                                      readonly=True, states=STATES_VALUE,domain=[('state','=','open')]),
        'partner_id': fields.related('invoice_id', 'partner_id', type='many2one',
                                     relation='res.partner', string='Empresa',
                                     readonly=True),
        'move_id': fields.related('invoice_id', 'move_id', type='many2one',
                                  relation='account.move',
                                  string='Asiento Contable',
                                  readonly=True),
        'state': fields.selection([('draft','Borrador'),
                                   ('early','Anticipado'),
                                   ('done','Validado'),
                                   ('cancel','Anulado')],
                                  readonly=True, string='Estado'),
        'amount_total': fields.function( _amount_total, string='Total',
                                         method=True, store=True,
                                         digits_compute=dp.get_precision('Account')),
        'to_cancel': fields.boolean('Para anulación',readonly=True, states=STATES_VALUE),
        }

    _defaults = {
        'state': 'draft',
        'in_type': _get_in_type,
        'type': _get_type,
        'name': '/',
        'number': '/',
        'manual': True,
        'date': time.strftime('%Y-%m-%d'),
        }

    _sql_constraints = [('unique_number', 'unique(number)', 'El número de retención es único.')]

    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state in ['done']:
                raise osv.except_osv('Aviso','No se permite borrar retenciones validadas.')
        res = super(account_retention, self).unlink(cr, uid, ids, context)
        return res

    def onchange_invoice(self, cr, uid, ids, invoice_id):
        res = {'value': {'num_document': ''}}
        if not invoice_id:
            return res
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if not invoice.auth_inv_id:
            return res
        num_document = '%s%s%s'% (invoice.auth_inv_id.serie_entidad, invoice.auth_inv_id.serie_emision, invoice.reference.zfill(9))
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
        retentions = self.browse(cr, uid, ids)
        for ret in retentions:
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
            self.write(cr, uid, ret.id, {'state': 'done', 'name': ret_num, 'number': number, 'name':number})
            self.log(cr, uid, ret.id, _("La retención %s fue generada.") % number)
        return True

    def action_cancel(self, cr, uid, ids, *args):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo para cambiar de estado a cancelado
        el documento
        '''
        for ret in self.browse(cr, uid, ids):
            data = {'state': 'cancel'}
            if ret.to_cancel:
                if len(ret.name) == 9:
                    number = ret.auth_id.serie_entidad + ret.auth_id.serie_emision + ret.name
                    data.update({'number': number, 'name': number})
                else:
                    raise osv.except_osv('Error', 'El número debe ser de 9 dígitos.')
            self.write(cr, uid, ret.id, data)
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


class account_invoice_tax(osv.osv):

    _name = 'account.invoice.tax'
    _inherit = 'account.invoice.tax'
   
    _columns = {
        'fiscal_year' : fields.char('Ejercicio Fiscal', size = 4),
        'tax_group' : fields.selection([('vat','IVA Diferente de 0%'),
                                        ('vat0','IVA 0%'),
                                        ('novat','No objeto de IVA'),
                                        ('ret_vat_b', 'Retención de IVA (Bienes)'),
                                        ('ret_vat_srv', 'Retención de IVA (Servicios)'),
                                        ('ret_ir', 'Ret. Imp. Renta'),
                                        ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'), 
                                        ('imp_ad', 'Imps. Aduanas'),
                                        ('ice', 'ICE'),
                                        ('other','Other')], 'Grupo', required=True),        
        'percent' : fields.char('Porcentaje', size=20),
        'num_document': fields.char('Num. Comprobante', size=50),
        'retention_id': fields.many2one('account.retention', 'Retención', select=True),
        }

    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        for line in inv.invoice_line:
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, inv.partner_id)['taxes']:
                val={}
                tax_group = self.pool.get('account.tax').read(cr, uid, tax['id'],['tax_group', 'amount', 'description','porcentaje'])
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['tax_group'] = tax_group['tax_group']
                val['percent'] = tax_group['description']                
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line['quantity'])
                if tax_group['tax_group'] in ['ret_vat_b', 'ret_vat_srv']:
                    ret = float(str(tax_group['porcentaje'])) / 100
                    bi = tax['price_unit'] * line['quantity']
                    imp = (abs(tax['amount']) / (ret * bi)) * 100
                    val['base'] = (tax['price_unit'] * line['quantity']) * imp / 100
                else:
                    val['base'] = tax['price_unit'] * line['quantity']
                if inv.type in ('out_invoice','in_invoice','liq_purchase'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
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

    _defaults = dict(
        fiscal_year = time.strftime('%Y'),
    )    


class Invoice(osv.osv):
    
    _inherit = 'account.invoice'
    __logger = logging.getLogger(_inherit)

    def onchange_company_id(self, cr, uid, ids, company_id, part_id, type, invoice_line, currency_id):
        #TODO: add the missing context parameter when forward-porting in trunk so we can remove
        #      this hack!
        context = self.pool['res.users'].context_get(cr, uid)

        val = {}
        dom = {}
        obj_journal = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        inv_line_obj = self.pool.get('account.invoice.line')
        if company_id and part_id and type:
            acc_id = False
            partner_obj = self.pool.get('res.partner').browse(cr,uid,part_id)
            if partner_obj.property_account_payable and partner_obj.property_account_receivable:
                if partner_obj.property_account_payable.company_id.id != company_id and partner_obj.property_account_receivable.company_id.id != company_id:
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr, uid, [('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(part_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr, uid, [('name','=','property_account_payable'),('res_id','=','res.partner,'+str(part_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr, uid, [('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr, uid, [('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr, uid, rec_pro_id, ['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr, uid, pay_pro_id, ['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of account, you should create one from Settings\Configuration\Accounting menu.'))
                    if type in ('out_invoice', 'out_refund'):
                        acc_id = rec_res_id
                    else:
                        acc_id = pay_res_id
                    val= {'account_id': acc_id}
            if ids:
                if company_id:
                    inv_obj = self.browse(cr,uid,ids)
                    for line in inv_obj[0].invoice_line:
                        if line.account_id:
                            if line.account_id.company_id.id != company_id:
                                result_id = account_obj.search(cr, uid, [('name','=',line.account_id.name),('company_id','=',company_id)])
                                if not result_id:
                                    raise osv.except_osv(_('Configuration Error!'),
                                        _('Cannot find a chart of account, you should create one from Settings\Configuration\Accounting menu.'))
                                inv_line_obj.write(cr, uid, [line.id], {'account_id': result_id[-1]})
            else:
                if invoice_line:
                    for inv_line in invoice_line:
                        obj_l = account_obj.browse(cr, uid, inv_line[2]['account_id'])
                        if obj_l.company_id.id != company_id:
                            raise osv.except_osv(_('Configuration Error!'),
                                _('Invoice line account\'s company and invoice\'s company does not match.'))
                        else:
                            continue
        if company_id and type:
            journal_mapping = {
               'out_invoice': 'sale',
               'out_refund': 'sale_refund',
               'in_refund': 'purchase_refund',
               'in_invoice': 'purchase',
               'liq_purchase': 'purchase'
            }
            journal_type = journal_mapping[type]
            journal_ids = obj_journal.search(cr, uid, [('company_id','=',company_id), ('type', '=', journal_type)])
            if journal_ids:
                val['journal_id'] = journal_ids[0]
            ir_values_obj = self.pool.get('ir.values')
            res_journal_default = ir_values_obj.get(cr, uid, 'default', 'type=%s' % (type), ['account.invoice'])
            for r in res_journal_default:
                if r[1] == 'journal_id' and r[2] in journal_ids:
                    val['journal_id'] = r[2]
            if not val.get('journal_id', False):
                journal_type_map = dict(obj_journal._columns['type'].selection)
                journal_type_label = self.pool['ir.translation']._get_source(cr, uid, None, ('code','selection'),
                                                                             context.get('lang'),
                                                                             journal_type_map.get(journal_type))
                raise osv.except_osv(_('Configuration Error!'),
                                     _('Cannot find any account journal of %s type for this company.\n\nYou can create one in the menu: \nConfiguration\Journals\Journals.') % ('"%s"' % journal_type_label))
            dom = {'journal_id':  [('id', 'in', journal_ids)]}
        else:
            journal_ids = obj_journal.search(cr, uid, [])

        return {'value': val, 'domain': dom}    

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

    def _amount_all(self, cr, uid, ids, fields, args, context=None):
        """
        Compute all total values in invoice object
        params:
        @cr cursor to DB
        @uid user id logged
        @ids active object ids
        @fields used fields in function, severals if use multi arg
        """
        res = {}
        cur_obj = self.pool.get('res.currency')

        invoices = self.browse(cr, uid, ids, context=context)
        for invoice in invoices:
            cur = invoice.currency_id
            res[invoice.id] = {
                'amount_vat': 0.0,
                'amount_untaxed': 0.0, 
                'amount_tax': 0.0,
                'amount_tax_retention': 0.0,
                'amount_tax_ret_ir': 0.0,
                'taxed_ret_ir': 0.0, 
                'amount_tax_ret_vatb': 0.0,
                'amount_tax_ret_vatsrv': 0.00,
                'taxed_ret_vatb': 0.0,
                'taxed_ret_vatsrv': 0.00,
                'amount_vat_cero': 0.0,
                'amount_novat': 0.0, 
                'amount_noret_ir': 0.0,
                'amount_total': 0.0,
                'amount_pay': 0.0,
            }
            
            #Total General
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
            for line in invoice.tax_line:
                if line.tax_group == 'vat':
                    res[invoice.id]['amount_vat'] += line.base
                    res[invoice.id]['amount_tax'] += line.amount                    
                elif line.tax_group == 'vat0':
                    res[invoice.id]['amount_vat_cero'] += line.base
                elif line.tax_group == 'novat':
                    res[invoice.id]['amount_novat'] += line.base
                elif line.tax_group == 'no_ret_ir':
                    res[invoice.id]['amount_noret_ir'] += line.base
                elif line.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:
                    res[invoice.id]['amount_tax_retention'] += line.amount
                    if line.tax_group == 'ret_vat_b':#in ['ret_vat_b', 'ret_vat_srv']:
                        res[invoice.id]['amount_tax_ret_vatb'] += line.base
                        res[invoice.id]['taxed_ret_vatb'] += line.amount
                    elif line.tax_group == 'ret_vat_srv':
                        res[invoice.id]['amount_tax_ret_vatsrv'] += line.base
                        res[invoice.id]['taxed_ret_vatsrv'] += line.amount                        
                    elif line.tax_group == 'ret_ir':
                        res[invoice.id]['amount_tax_ret_ir'] += line.base
                        res[invoice.id]['taxed_ret_ir'] += line.amount
                elif line.tax_group == 'ice':
                    res[invoice.id]['amount_ice'] += line.amount

            # base vat not defined, amount_vat_cero by default
            if res[invoice.id]['amount_vat'] == 0 and res[invoice.id]['amount_vat_cero'] == 0:
                res[invoice.id]['amount_vat_cero'] = res[invoice.id]['amount_untaxed']

            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed'] \
                                            + res[invoice.id]['amount_tax_retention']
            res[invoice.id]['amount_pay']  = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed']

        return res

    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()        

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

    def _get_num_retentions(self, cr, uid, context=None):
        if context is None:
            context = {}
        numbers = self.pool.get('account.retention.cache')
        num_ids = numbers.search(cr, uid, [('active','=',True)])
        res = numbers.read(cr, uid, num_ids, ['name', 'id'])
        res = [(r['id'], r['name']) for r in res]
        return res

    def _get_num_to_use(self, cr, uid, ids, field_name, args, context):
        res = {}
        invoices = self.browse(cr, uid, ids, context)
        for inv in invoices:
            if inv.type in ['out_invoice', 'liq_purchase']:
                if inv.journal_id.auth_id and inv.journal_id.auth_id.sequence_id:
                    res[inv.id] = str(inv.journal_id.auth_id.sequence_id.number_next)
                elif inv.state in ['cancel', 'open', 'paid']:
                    return res
                else:
                    raise osv.except_osv('Error', 'No se ha configurado una autorización en el diario.')
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

    VAR_STORE = {
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            }

    PRECISION_DP = dp.get_precision('Account')    

    _columns = {
        'supplier_number': fields.function(_get_supplier_number, method=True, type='char', size=32,
                                           string='Factura de Proveedor', store=True),
        'amount_ice': fields.function(_amount_all, method=True, digits_compute=PRECISION_DP, string='ICE',
                                      store=VAR_STORE, multi='all'),
        'amount_vat': fields.function(_amount_all, method=True,
                                      digits_compute=PRECISION_DP, string='Base 12 %', 
                                      store=VAR_STORE,
                                      multi='all'),
        'amount_untaxed': fields.function(_amount_all, method=True,
                                          digits_compute=PRECISION_DP, string='Untaxed',
                                          store=VAR_STORE,
                                          multi='all'),
        'amount_tax': fields.function(_amount_all, method=True,
                                      digits_compute=PRECISION_DP, string='Tax',
                                      store=VAR_STORE,
                                      multi='all'),
        'amount_total': fields.function(_amount_all, method=True,
                                        digits_compute=PRECISION_DP, string='Total a Pagar',
                                        store=VAR_STORE,
                                        multi='all'), 
        'amount_pay': fields.function(_amount_all, method=True,
                                      digits_compute=PRECISION_DP, string='Total',
                                      store=VAR_STORE,
                                      multi='all'),
        'amount_noret_ir': fields.function(_amount_all, method=True,
                                           digits_compute=PRECISION_DP, string='Monto no sujeto a IR',
                                           store=VAR_STORE,
                                           multi='all'),
        'amount_tax_retention': fields.function(_amount_all, method=True,
                                                digits_compute=PRECISION_DP, string='Total Retencion',
                                                store=VAR_STORE,
                                                multi='all'),
        'amount_tax_ret_ir': fields.function( _amount_all, method=True,
                                              digits_compute=PRECISION_DP, string='Base IR',
                                              store=VAR_STORE,
                                              multi='all'),
        'taxed_ret_ir': fields.function( _amount_all, method=True,
                                         digits_compute=PRECISION_DP, string='Impuesto IR',
                                         store=VAR_STORE,
                                         multi='all'),
        'amount_tax_ret_vatb' : fields.function( _amount_all,
                                                 method=True,
                                                 digits_compute=PRECISION_DP,
                                                 string='Base Ret. IVA',
                                                 store=VAR_STORE,
                                                 multi='all'),
        'taxed_ret_vatb' : fields.function( _amount_all,
                                            method=True,
                                            digits_compute=PRECISION_DP,
                                            string='Retencion en IVA',
                                            store=VAR_STORE,
                                            multi='all'),
        'amount_tax_ret_vatsrv' : fields.function( _amount_all,
                                                   method=True,
                                                   digits_compute=PRECISION_DP, string='Base Ret. IVA',
                                                   store=VAR_STORE,
                                                   multi='all'),
        'taxed_ret_vatsrv' : fields.function( _amount_all, method=True,
                                              digits_compute=PRECISION_DP,
                                              string='Retencion en IVA',
                                              store=VAR_STORE,
                                              multi='all'),        
        'amount_vat_cero' : fields.function( _amount_all, method=True,
                                             digits_compute=PRECISION_DP, string='Base IVA 0%',
                                             store=VAR_STORE,
                                             multi='all'),
        'amount_novat' : fields.function( _amount_all, method=True,
                                          digits_compute=PRECISION_DP, string='Base No IVA',
                                          store=VAR_STORE,
                                          multi='all'),
        'create_retention_type': fields.selection([('normal','Automatico'),
                                                   ('manual', 'Manual'),
                                                   ('reserve','Num Reservado'),
                                                   ('no_retention', 'No Generar')],
                                                  string='Numerar Retención',
                                                  readonly=True,
                                                  help=HELP_RET_TEXT,
                                                  states = {'draft': [('readonly', False)]}),        
        
        'auth_inv_id' : fields.many2one('account.authorisation', 'Autorización SRI',
                                        help = 'Autorizacion del SRI para documento recibido',
                                        readonly=True,
                                        states={'draft': [('readonly', False)]}),
        'retention_id': fields.many2one('account.retention', store=True,
                                        string='Retención de Impuestos',
                                        readonly=True),
        'retention_ir': fields.function( _check_retention, store=False,
                                         string="Tiene Retención en IR",
                                         method=True, type='boolean',
                                         multi='ret'),
        'retention_vat': fields.function( _check_retention, store=True,
                                          string='Tiene Retencion en IVA',
                                          method=True, type='boolean',
                                          multi='ret'),
        'no_retention_ir': fields.function( _check_retention, store=True,
                                          string='No objeto de Retención',
                                          method=True, type='boolean',
                                          multi='ret'),        
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ('liq_purchase','Liquidacion de Compra')
            ],'Type', readonly=True, select=True, change_default=True),
        'retention_numbers': fields.selection(_get_num_retentions,
                                              readonly=True,
                                              string='Num. de Retención',
                                              help='Lista de Números de Retención reservados',
                                              states = {'draft': [('readonly', False)]}),
        'manual_ret_num': fields.integer('Num. Retención', readonly=True,
                                         states = {'draft': [('readonly', False)]}),
        'num_to_use': fields.function( _get_num_to_use,
                                       string='Núm a Usar',
                                       method=True,
                                       type='char',
                                       help='Num. de documento a usar'),
        'sustento_id': fields.many2one('account.ats.sustento',
                                       'Sustento del Comprobante'),        
        }

    _defaults = {
        'create_retention_type': 'manual',
        }

    # constraint stuff
    def check_in_reference(self, cr, uid, ids):
        '''
        cr: cursor de la base de datos
        uid: ID de usuario
        ids: lista ID del objeto instanciado

        Metodo que revisa la referencia a
        tener en cuenta en documentos que se recibe
        '''                                
        res = False
        for inv in self.browse(cr, uid, ids):
            if inv.partner_id.type_ced_ruc == 'pasaporte':
                return True
            elif inv.reference == '0' and inv.state == 'draft':
                return True
            elif inv.state == 'cancel':
                return True
            elif inv.create_retention_type == 'early' or inv.type in ['liq_purchase']:
                return True
            elif not inv.auth_inv_id:
                return True
            elif inv.auth_inv_id.is_electronic:
                return True
            elif inv.type in ['out_refund', 'in_refund']:
                return True
            elif inv.type == 'in_invoice' or (inv.type == 'out_invoice' and (inv.retention_vat or inv.retention_ir)):
                if inv.auth_inv_id.num_start <= int(inv.supplier_invoice_number) <= inv.auth_inv_id.num_end:
                    res = True
            elif inv.type == 'out_invoice':
                res = True
            return res

    def check_retention_number(self, cr, uid, ids):
        """
        Metodo que verifica el numero de retencion
        asignada a la factura cuando es manual la numeracion.
        """
        res = False
        auth_obj = self.pool.get('account.authorisation')
        for obj in self.browse(cr, uid, ids):
            if obj.type == 'out_refund':
                res = True
            elif obj.type == 'in_invoice' and (obj.retention_ir or obj.retention_vat):
                if not obj.journal_id.auth_ret_id:
                    raise osv.except_osv('Error', u'No se configuró retenciones.')
                if obj.create_retention_type == 'manual' \
                  and obj.manual_ret_num>0 and \
                  auth_obj.is_valid_number(cr, uid, obj.journal_id.auth_ret_id.id, obj.manual_ret_num):
                    res = True
                else:
                    raise osv.except_osv('Error', u'Error en el número de retención.')
            else:
                res = True
        return res

    _constraints = [
        (check_in_reference,
         ustr('El número de referencia no pertenece a la autorización seleccionada.'),
         [ustr('Factura Proveedor'), ustr('Autorización')]),
        ]

    _sql_constraints = [
        ('unique_inv_supplier', 'unique(reference,type,partner_id)', u'El numero de factura es unico.'),
    ]    

    def copy_data(self, cr, uid, id, default=None, context=None):
        res = super(Invoice, self).copy_data(cr, uid, id, default, context=context)
        res.update({'reference': '0',
                    'auth_inv_id': False,
                    'retention_id': False,
                    'retention_numbers': False})
        return res

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):    
        auth_obj = self.pool.get('account.authorisation')
        res1 = super(Invoice, self).onchange_partner_id(cr, uid, ids, type,
                                                        partner_id, date_invoice,
                                                        payment_term, partner_bank_id,
                                                        company_id)
        if res1['value'].has_key('reference_type'):
            res1['value'].pop('reference_type')
        res = auth_obj.search(cr, uid, [('partner_id','=',partner_id),('in_type','=','externo')], limit=1)
        if res:
            res1['value']['auth_inv_id'] = res[0]
        return res1

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


class AccountInvoiceLine(osv.osv):
    _inherit = 'account.invoice.line'

    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        for line in inv.invoice_line:
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)
            tax_code_found= False
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id,
                    (line.price_unit * (1.0 - (line['discount'] or 0.0) / 100.0)),
                    line.quantity, line.product_id,
                    inv.partner_id)['taxes']:

                if inv.type in ('out_invoice', 'in_invoice', 'liq_purchase'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = line.price_subtotal * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = line.price_subtotal * tax['ref_base_sign']

                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True

                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, tax_amount, context={'date': inv.date_invoice})
        return res

    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id, 'force_company': company_id})
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined!'),_("You must first select a partner!") )
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain':{'product_uom':[]}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain':{'product_uom':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

        if part.lang:
            context.update({'lang': part.lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)

        if type in ('out_invoice','out_refund'):
            a = res.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            a = res.property_account_expense.id
            if not a:
                a = res.categ_id.property_account_expense_categ.id
        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a

        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)

        if type in ('in_invoice', 'in_refund'):
            result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )
        else:
            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
        result['name'] = res.partner_ref

        result['uos_id'] = uom_id or res.uom_id.id
        if res.description:
            result['name'] += '\n'+res.description

        domain = {'uos_id':[('category_id','=',res.uom_id.category_id.id)]}

        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            if type in ('in_invoice', 'in_refund'):
                res_final['value']['price_unit'] = res.standard_price
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if result['uos_id'] and result['uos_id'] != res.uom_id.id:
            selected_uom = self.pool.get('product.uom').browse(cr, uid, result['uos_id'], context=context)
            new_price = self.pool.get('product.uom')._compute_price(cr, uid, res.uom_id.id, res_final['value']['price_unit'], result['uos_id'])
            res_final['value']['price_unit'] = new_price
        return res_final    


class AccountInvoiceRefund(osv.TransientModel):

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
            
