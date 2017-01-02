# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)
try:
    from stdnum import ec
except ImportError as err:
    _logger.debug('Cannot import stdnum')


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    @api.depends('identifier', 'name')
    def name_get(self):
        data = []
        for partner in self:
            display_val = u'{0} {1}'.format(
                partner.identifier or '*',
                partner.name
            )
            data.append((partner.id, display_val))
        return data

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if not args:
            args = []
        if name:
            partners = self.search([('identifier', operator, name)] + args, limit=limit)  # noqa
            if not partners:
                partners = self.search([('name', operator, name)] + args, limit=limit)  # noqa
        else:
            partners = self.search(args, limit=limit)
        return partners.name_get()

    @api.one
    @api.constrains('identifier')
    def _check_identifier(self):
        if self.type_identifier == 'cedula':
            return ec.ci.is_valid(self.identifier)
        elif self.type_identifier == 'ruc':
            return ec.ruc.is_valid(self.identifier)
        else:
            return True

    identifier = fields.Char(
        'Cedula/ RUC',
        size=13,
        required=True,
        help='Identificación o Registro Unico de Contribuyentes')
    type_identifier = fields.Selection(
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
    company_type = fields.Selection(default='company')

    _sql_constraints = [
        ('partner_unique',
         'unique(identifier,type_identifier,tipo_persona,company_id)',
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

    accountant_id = fields.Many2one('res.partner', 'Contador')
    sri_id = fields.Many2one('res.partner', 'Servicio de Rentas Internas')
    cedula_rl = fields.Char('Cédula Representante Legal', size=10)
