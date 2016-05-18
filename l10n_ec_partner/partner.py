# -*- coding: utf-8 -*-

from openerp import models, fields
from openerp.exceptions import Warning as UserError

"""
Partners para Ecuador
"""

class ResPartner(models.Model):

    _name = 'res.partner'
    _inherit = 'res.partner'

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):  # noqa
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            ids = self.search(cr, uid, [('ced_ruc', operator, name)] + args, limit=limit, context=context)  # noqa
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)  # noqa
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def _check_cedula(self, identificador):
        if len(identificador) == 13 and not identificador[10:13] == '001':
            return False
        else:
            if len(identificador) < 10:
                return False
        coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        cedula = identificador[:9]
        suma = 0
        for c in cedula:
            val = int(c) * coef.pop()
            suma += val > 9 and val-9 or val
        result = 10 - ((suma % 10) != 0 and suma % 10 or 10)
        if result == int(identificador[9:10]):
            return True
        else:
            return False

    def _check_ruc(self, partner):
        ruc = partner.ced_ruc
        if not len(ruc) == 13:
            return False
        if ruc[2:3] == '9':
            coef = [4, 3, 2, 7, 6, 5, 4, 3, 2, 0]
            coef.reverse()
            verificador = int(ruc[9:10])
        elif ruc[2:3] == '6':
            coef = [3, 2, 7, 6, 5, 4, 3, 2, 0, 0]
            coef.reverse()
            verificador = int(ruc[8:9])
        else:
            raise UserError('Error', 'Cambie el tipo de persona')
        suma = 0
        for c in ruc[:10]:
            suma += int(c) * coef.pop()
        result = 11 - (suma > 0 and suma % 11 or 11)
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
            elif partner.type_ced_ruc == 'ruc':
                if not len(partner.ced_ruc) == 13:
                    return False
                if partner.tipo_persona == '9':
                    return self._check_ruc(partner)
                else:
                    return self._check_cedula(partner.ced_ruc)
            elif partner.type_ced_ruc == 'cedula':
                if not len(partner.ced_ruc) == 10:
                    return False
                else:
                    return self._check_cedula(partner.ced_ruc)

    ced_ruc = fields.Char(
        'Cedula/ RUC',
        size=13,
        required=True,
        help='Identificación o Registro Unico de Contribuyentes')
    type_ced_ruc = fields.Selection(
        [
            ('cedula', 'CEDULA'),
            ('ruc', 'RUC'),
            ('pasaporte', 'PASAPORTE')
            ],
        'Tipo ID',
        required=True
    )
    tipo_persona = fields.Selection(
        [
            ('6', 'Persona Natural'),
            ('9', 'Persona Juridica')
        ],
        string='Persona',
        required=True,
        default='9'
    )
    is_company = fields.Boolean(default=True)

    _constraints = [
        (_check_ced_ruc, 'Error en su Cedula/RUC/Pasaporte', ['ced_ruc'])
        ]

    _sql_constraints = [
        ('partner_unique',
         'unique(ced_ruc,type_ced_ruc,tipo_persona,company_id)',
         u'El identificador es único.'),
        ]

    def validate_from_sri(self):
        """
        TODO
        """
        SRI_LINK = "https://declaraciones.sri.gob.ec/facturacion-internet/consultas/publico/ruc-datos1.jspa"  # noqa
        texto = '0103893954'  # noqa


class ResCompany(models.Model):
    _inherit = 'res.company'

    ruc_contador = fields.Char('Ruc del Contador', size=13)
    cedula_rl = fields.Char('Cédula Representante Legal', size=10)
