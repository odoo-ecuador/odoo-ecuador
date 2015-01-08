# -*- coding: utf-8 -*-

__author__ = 'Cristian Salamea (cristian.salamea@gmail.com)'

import time
from datetime import datetime

from openerp.osv import osv, orm, fields


class Partner(osv.osv):

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
        'ced_ruc': fields.char('Cedula/ RUC',
                               size=13,
                               required=True,
                               help='Idenficacion o Registro Unico de Contribuyentes'),
        'type_ced_ruc': fields.selection([
            ('cedula','Cedula'),
            ('ruc','RUC'),
            ('pasaporte','Pasaporte')
            ],
            'Tipo ID',
            required=True),
        'tipo_persona': fields.selection(
            [('6','Persona Natural'),
            ('9','Persona Juridica')],
            string='Persona',
            required=True
            ),
        }

    _defaults = {
        'tipo_persona': '9',
        'is_company': True
        }

    _constraints = [
        (_check_ced_ruc, 'Error en su Cedula/RUC/Pasaporte', ['cedu_ruc'])
        ]

    _sql_constraints = [
        ('partner_unique',
         'unique(ced_ruc,type_ced_ruc,tipo_persona,company_id)',
         u'El identificador es único.'),
        ]


class ResCompany(osv.Model):
    _inherit = 'res.company'

    _columns = {
        'ruc_contador': fields.char('Ruc del Contador', size=13),
        'cedula_rl': fields.char('Cédula Representante Legal', size=10),
        }
