# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
try:
    from stdnum import ec
except ImportError as err:
    _logger.debug('Cannot import stdnum')


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def update_identifiers(self):
        res = self.search([('identifier', '=', False)])
        for e in res:
            e.write({'identifier': '9999999999'})

    @api.model_cr_context
    def init(self):
        super(ResPartner, self).init()
        self.update_identifiers()
        sql_index = """
        CREATE UNIQUE INDEX IF NOT EXISTS
        unique_company_partner_identifier_type on res_partner
        (company_id, type_identifier, identifier)
        WHERE type_identifier <> 'pasaporte'"""
        self._cr.execute(sql_index)

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
        res = False
        if self.type_identifier == 'cedula':
            res = ec.ci.is_valid(self.identifier)
        elif self.type_identifier == 'ruc':
            res = ec.ruc.is_valid(self.identifier)
        else:
            return True
        if not res:
            raise ValidationError('Error en el identificador.')

    @api.one
    @api.depends('identifier')
    def _compute_tipo_persona(self):
        if not self.identifier:
            self.tipo_persona = '0'
        elif int(self.identifier[2]) <= 6:
            self.tipo_persona = '6'
        elif int(self.identifier[2]) in [6, 9]:
            self.tipo_persona = '9'
        else:
            self.tipo_persona = '0'

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
        compute='_compute_tipo_persona',
        selection=[
            ('6', 'Persona Natural'),
            ('9', 'Persona Juridica'),
            ('0', 'Otro')
        ],
        string='Persona',
        store=True
    )
    is_company = fields.Boolean(default=True)

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
