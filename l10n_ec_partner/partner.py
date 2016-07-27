# -*- coding: utf-8 -*-

from openerp import models, fields
from openerp.exceptions import Warning as UserError

from stdnum import ec


class ResPartner(models.Model):

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

    def _check_ced_ruc(self, cr, uid, ids):
        for partner in self.browse(cr, uid, ids):
            if partner.type_ced_ruc == 'cedula':
                return ec.ci.is_valid(partner.ced_ruc)
            elif partner.type_ced_ruc == 'ruc':
                return ec.ruc.is_valid(partner.ced_ruc)
            else:
                return True

    ced_ruc = fields.Char(
        'Cedula/ RUC',
        size=13,
        required=True,
        default='99999',
        help='Identificación o Registro Unico de Contribuyentes')
    type_ced_ruc = fields.Selection(
        [
            ('cedula', 'CEDULA'),
            ('ruc', 'RUC'),
            ('pasaporte', 'PASAPORTE')
            ],
        'Tipo ID',
        required=True,
        default='pasaporte'
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
