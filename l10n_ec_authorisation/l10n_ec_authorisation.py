# -*- coding: utf-8 -*-

import time
from datetime import datetime

from osv import osv, fields


class AccountAtsDoc(osv.osv):
    _name = 'account.ats.doc'
    _description = 'Tipos Comprobantes Autorizados'

    _columns = dict(
        code = fields.char('Código', size=2, required=True),
        name = fields.char('Tipo Comprobante', size=64, required=True),
        )


class AccountAtsSustento(osv.osv):
    _name = 'account.ats.sustento'
    _description = 'Sustento del Comprobante'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = '%s - %s' % (record.code, record.type)
            res.append((record.id, name))
        return res

    _rec_name = 'type'
    
    _columns = dict(
        code = fields.char('Código', size=2, required=True),
        type = fields.char('Tipo de Sustento', size=64, required=True),
        )


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
            name = '%s (%s-%s)' % (record.type_id.name, record.num_start, record.num_end)
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


class ResParter(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'authorisation_ids': fields.one2many('account.authorisation', 'partner_id', 'Autorizaciones'),        
    }


class AccountJournal(osv.osv):

    _inherit = 'account.journal'

    _columns = {
        'auth_id': fields.many2one('account.authorisation',
                                   help='Autorización utilizada para Facturas y Liquidaciones de Compra',
                                   string='Autorización',
                                   domain="[('in_type','=','interno')]"),
        'auth_ret_id': fields.many2one('account.authorisation',
                                       domain=[('in_type','=','interno')],
                                       string='Autorización de Ret.',
                                       help='Autorizacion utilizada para Retenciones, facturas y liquidaciones')
        }


