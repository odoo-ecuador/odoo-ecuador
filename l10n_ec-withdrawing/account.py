# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2010 GnuThink Software All Rights Reserved
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

__author__ = 'Cristian Salamea (cristian.salamea@gnuthink.com)'

import time
from datetime import datetime

from osv import osv, fields
from tools import ustr

class account_retention_cache(osv.osv):

    _name = 'account.retention.cache'

    def get_number(self, cr, uid, id):
        obj = self.browse(cr, uid, int(id))
        number = obj.name
        self.write(cr, uid, int(id), {'active': False})
        return number

    _columns = {
        'name': fields.char('Numero a Reservar', size=32, readonly=True),
        'active': fields.boolean('Activo', readonly=True),
        }

    _defaults = {
        'active': True,
        }


class AccountAuthorisation(osv.osv):

    _name = 'account.authorisation'
    _description = 'Authorisation for Accounting Documents'
    _order = 'expiration_date desc'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = '%s (%s-%s)' % (record.name, record.num_start, record.num_end)
            res.append((record.id, name))
        return res        
    
    def _check_active(self, cr, uid, ids, name, args, context):
        """
        Check the due_date to give the value active field
        """
        res = {}
        objs = self.browse(cr, uid, ids)
        now = datetime.strptime(time.strftime("%Y-%m-%d"),'%Y-%m-%d')
        for item in objs:
            due_date = datetime.strptime(item.expiration_date, '%Y-%m-%d')
            res[item.id] = now<due_date
        return res
  
    def _get_type(self, cursor, uid, context):
        return context.get('type', 'in_invoice')
    
    def _get_in_type(self, cursor, uid, context):
        return context.get('in_type', 'externo')

    def _get_partner(self, cursor, uid, context):
        if context.get('partner_id', False):
            return context.get('partner_id')
        else:
            user = self.pool.get('res.users').browse(cursor, uid, uid)
            return user.company_id.partner_id.id

    def create(self, cr, uid, values, context=None):
        partner_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.id
        if values.has_key('partner_id') and partner_id == values['partner_id']:
            ats_obj = self.pool.get('account.ats.doc')
            name_type = ats_obj.read(cr, uid, values['type_id'], ['name'])['name']
            code_obj = self.pool.get('ir.sequence.type')
            seq_obj = self.pool.get('ir.sequence')
            code_data = {
                'code': '%s.%s.%s' % (values['name'],values['serie_entidad'],values['serie_emision']),
                'name': name_type,
                }
            code_id = code_obj.create(cr, uid, code_data)
            seq_data = {'name': name_type,
                        'padding': 9,
                        'number_next': values['num_start']}
            seq_id = seq_obj.create(cr, uid, seq_data)
            values.update({'sequence_id': seq_id})
        return super(AccountAuthorisation, self).create(cr, uid, values, context)

    def unlink(self, cr, uid, ids, context=None):
        type_obj = self.pool.get('ir.sequence.type')
        for obj in self.browse(cr, uid, ids, context):
            aux = obj.sequence_id.code
            self.pool.get('ir.sequence').unlink(cr, uid, obj.sequence_id.id)
        return super(AccountAuthorisation, self).unlink(cr, uid, ids, context)

    _columns = {
        'name' : fields.char('Num. de Autorizacion', size=128, required=True),
        'serie_entidad' : fields.char('Serie Entidad', size=3, required=True),
        'serie_emision' : fields.char('Serie Emision', size=3, required=True),
        'num_start' : fields.integer('Desde', required=True),
        'num_end' : fields.integer('Hasta', required=True),
        'is_electronic': fields.boolean('Factura Electrónica'),
        'expiration_date' : fields.date('Vence', required=True),
        'active' : fields.function(_check_active, string='Activo',
                                   method=True, type='boolean'),
        'in_type': fields.selection([('interno', 'Internas'),
                                     ('externo', 'Externas')],
                                    string='Tipo Interno',
                                    readonly=True,
                                    change_default=True),
        'type_id': fields.many2one('account.ats.doc', 'Tipo de Comprobante', required=True),
        'partner_id' : fields.many2one('res.partner', 'Empresa', required=True),
        'sequence_id' : fields.many2one('ir.sequence', 'Secuencia',
                                        help='Secuencia Alfanumerica para el documento, se debe registrar cuando pertenece a la compañia'),
        }

    def set_authorisation(cr, uid, ids, context):
        return True

    _defaults = {
        'active': False,
        'in_type': _get_in_type,
        'partner_id': _get_partner,
        }

    _sql_constraints = [
        ('number_unique',
         'unique(name,partner_id,serie_entidad,serie_emision,type_id)',
         u'La relación de autorización, serie entidad, serie emisor y tipo, debe ser única.'),
        ]

    def is_valid_number(self, cr, uid, id, number):
        """
        Metodo que verifica si @number esta en el rango
        de [@num_start,@num_end]
        """
        obj = self.browse(cr, uid, id)
        if obj.num_start <= number <= obj.num_end:
            return True
        return False


class account_journal(osv.osv):

    _name = 'account.journal'
    _inherit = 'account.journal'

    _columns = {
        'auth_id': fields.many2one('account.authorisation', help='Autorización utilizada para Facturas de Venta y Liquidaciones de Compra',
                                   string='Autorización', domain="[('in_type','=','interno')]"),
        'auth_ret_id': fields.many2one('account.authorisation', domain="[('in_type','=','interno')]",
                                       string='Autorización de Ret.',
                                       help='Autorizacion utilizada para documentos de retención en Facturas de Proveedor y Liquidaciones de Compra')
        }


class account_tax(osv.osv):
    
    _name = 'account.tax'
    _inherit = 'account.tax'
    _order = 'tax_group desc'

    def _unit_compute(self, cr, uid, taxes, price_unit, product=None, partner=None, quantity=0):
        taxes = self._applicable(cr, uid, taxes, price_unit ,product, partner)
        res = []
        cur_price_unit=price_unit
        for tax in taxes:
            # we compute the amount for the current tax object and append it to the result
            data = {'id':tax.id,
                    'name':tax.description and tax.description + " - " + tax.name or tax.name,
                    'account_collected_id':tax.account_collected_id.id,
                    'account_paid_id':tax.account_paid_id.id,
                    'account_analytic_collected_id': tax.account_analytic_collected_id.id,
                    'account_analytic_paid_id': tax.account_analytic_paid_id.id,
                    'base_code_id': tax.base_code_id.id,
                    'ref_base_code_id': tax.ref_base_code_id.id,
                    'sequence': tax.sequence,
                    'base_sign': tax.base_sign,
                    'tax_sign': tax.tax_sign,
                    'ref_base_sign': tax.ref_base_sign,
                    'ref_tax_sign': tax.ref_tax_sign,
                    'price_unit': cur_price_unit,
                    'tax_code_id': tax.tax_code_id.id,
                    'ref_tax_code_id': tax.ref_tax_code_id.id,
                    'tax_group': tax.tax_group,
            }
            res.append(data)
            if tax.type=='percent':
                amount = cur_price_unit * tax.amount
                data['amount'] = amount

            elif tax.type=='fixed':
                data['amount'] = tax.amount
                data['tax_amount']=quantity
               # data['amount'] = quantity
            elif tax.type=='code':
                localdict = {'price_unit':cur_price_unit, 'product':product, 'partner':partner}
                exec tax.python_compute in localdict
                amount = localdict['result']
                data['amount'] = amount
            elif tax.type=='balance':
                data['amount'] = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)
                data['balance'] = cur_price_unit

            amount2 = data.get('amount', 0.0)
            if tax.child_ids:
                if tax.child_depend:
                    latest = res.pop()
                amount = amount2
                child_tax = self._unit_compute(cr, uid, tax.child_ids, amount, product, partner, quantity)
                res.extend(child_tax)
                if tax.child_depend:
                    for r in res:
                        for name in ('base','ref_base'):
                            if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
                                r[name+'_code_id'] = latest[name+'_code_id']
                                r[name+'_sign'] = latest[name+'_sign']
                                r['price_unit'] = latest['price_unit']
                                latest[name+'_code_id'] = False
                        for name in ('tax','ref_tax'):
                            if latest[name+'_code_id'] and latest[name+'_sign'] and not r[name+'_code_id']:
                                r[name+'_code_id'] = latest[name+'_code_id']
                                r[name+'_sign'] = latest[name+'_sign']
                                r['amount'] = data['amount']
                                latest[name+'_code_id'] = False
            if tax.include_base_amount:
                cur_price_unit+=amount2
        return res

    def _unit_compute_inv(self, cr, uid, taxes, price_unit, product=None, partner=None):
        taxes = self._applicable(cr, uid, taxes, price_unit,  product, partner)
        res = []
        taxes.reverse()
        cur_price_unit = price_unit

        tax_parent_tot = 0.0
        for tax in taxes:
            if (tax.type=='percent') and not tax.include_base_amount:
                tax_parent_tot += tax.amount

        for tax in taxes:
            if (tax.type=='fixed') and not tax.include_base_amount:
                cur_price_unit -= tax.amount

        for tax in taxes:
            if tax.type=='percent':
                if tax.include_base_amount:
                    amount = cur_price_unit - (cur_price_unit / (1 + tax.amount))
                else:
                    amount = (cur_price_unit / (1 + tax_parent_tot)) * tax.amount

            elif tax.type=='fixed':
                amount = tax.amount

            elif tax.type=='code':
                localdict = {'price_unit':cur_price_unit, 'product':product, 'partner':partner}
                exec tax.python_compute_inv in localdict
                amount = localdict['result']
            elif tax.type=='balance':
                amount = cur_price_unit - reduce(lambda x,y: y.get('amount',0.0)+x, res, 0.0)

            if tax.include_base_amount:
                cur_price_unit -= amount
                todo = 0
            else:
                todo = 1
            res.append({
                'id': tax.id,
                'todo': todo,
                'name': tax.name,
                'amount': amount,
                'account_collected_id': tax.account_collected_id.id,
                'account_paid_id': tax.account_paid_id.id,
                'account_analytic_collected_id': tax.account_analytic_collected_id.id,
                'account_analytic_paid_id': tax.account_analytic_paid_id.id,
                'base_code_id': tax.base_code_id.id,
                'ref_base_code_id': tax.ref_base_code_id.id,
                'sequence': tax.sequence,
                'base_sign': tax.base_sign,
                'tax_sign': tax.tax_sign,
                'ref_base_sign': tax.ref_base_sign,
                'ref_tax_sign': tax.ref_tax_sign,
                'price_unit': cur_price_unit,
                'tax_code_id': tax.tax_code_id.id,
                'ref_tax_code_id': tax.ref_tax_code_id.id,
                'tax_group': tax.tax_group
            })
            if tax.child_ids:
                if tax.child_depend:
                    del res[-1]
                    amount = price_unit

            parent_tax = self._unit_compute_inv(cr, uid, tax.child_ids, amount, product, partner)
            res.extend(parent_tax)

        total = 0.0
        for r in res:
            if r['todo']:
                total += r['amount']
        for r in res:
            r['price_unit'] -= total
            r['todo'] = 0
        return res

    _columns = {
        'sec_name': fields.char('Descripción Corta', size=128),
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
        }

    _defaults = {
        'tax_group': 'vat',
        }

account_tax()


class Partner(osv.Model):
    
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Formulario de Partner para Ecuador'

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('ced_ruc', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def _check_cedula(self, identificador):
        if len(identificador) == 13 and not identificador[10:13] == '001':
            return False
        else:
            if len(identificador) < 10:
                return False
        coef = [2,1,2,1,2,1,2,1,2]
        cedula = identificador[:9]
        suma = 0
        for c in cedula:
            val = int(c) * coef.pop()
            suma += val > 9 and val-9 or val
        result = 10 - ((suma % 10)!=0 and suma%10 or 10)
        if result == int(identificador[9:10]):
            return True
        else:
            return False

    def _check_ruc(self, partner):
        ruc = partner.ced_ruc
        if not len(ruc) == 13:
            return False
        if ruc[2:3] == '9':
            coef = [4,3,2,7,6,5,4,3,2,0]
            coef.reverse()
            verificador = int(ruc[9:10])
        elif ruc[2:3] == '6':
            coef = [3,2,7,6,5,4,3,2,0,0]
            coef.reverse()
            verificador = int(ruc[8:9])
        else:
            raise osv.except_osv('Error', 'Cambie el tipo de persona')
        suma = 0
        for c in ruc[:10]:
            suma += int(c) * coef.pop()
        result = 11 - (suma>0 and suma % 11 or 11)
        if result == verificador:
            return True
        else:
            return False

    def _check_ced_ruc(self, cr, uid, ids):
        partners = self.browse(cr, uid, ids)
        for partner in partners:
            if not partner.ced_ruc:
                return True
            if partner.type_ced_ruc == 'pasaporte':
                return True
            if partner.tipo_persona == '9':
                return self._check_ruc(partner)
            else:
                return self._check_cedula(partner.ced_ruc)

    _columns = {
        'ced_ruc': fields.char('Cedula/ RUC', size=13, required=True, help='Idenficacion o Registro Unico de Contribuyentes'),
        'type_ced_ruc': fields.selection([('cedula','Cedula'),('ruc','RUC'),('pasaporte','Pasaporte')], 'Tipo ID', required=True),
        'tipo_persona': fields.selection([('6','Persona Natural'),('9','Persona Juridica')], 'Persona', required=True),
        'authorisation_ids': fields.one2many('account.authorisation', 'partner_id', 'Autorizaciones'),
        }

    _defaults = {
        'tipo_persona': '9',
        }

    _constraints = [
        (_check_ced_ruc, 'Error en su Cedula/RUC/Pasaporte', ['cedu_ruc'])
        ]

    _sql_constraints = [
        ('partner_unique', 'unique(ced_ruc,type_ced_ruc,tipo_persona, company_id)',  ustr('El identificador es único.')),
        ]

Partner()


class ResCompany(osv.Model):
    _inherit = 'res.company'

    _columns = {
        'ruc_contador': fields.char('Ruc del Contador', size=13),
        'cedula_rl': fields.char('Cédula Representante Legal', size=10),
        }

