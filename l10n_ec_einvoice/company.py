# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Company(models.Model):

    _inherit = 'res.company'

    electronic_signature = fields.Char(
        'Firma Electrónica',
        size=128,
    )
    password_electronic_signature = fields.Char(
        'Clave Firma Electrónica',
        size=255,
    )
    emission_code = fields.Selection(
        [
            ('1', 'Normal'),
            ('2', 'Indisponibilidad')
        ],
        string='Tipo de Emisión',
        required=True,
        default=1
    )
    env_service = fields.Selection(
        [
            ('1', 'Pruebas'),
            ('2', 'Producción')
        ],
        string='Tipo de Ambiente',
        required=True,
        default=1
    )
    contingency_key_ids = fields.One2many(
        'res.company.contingency.key',
        'company_id',
        'Claves de Contingencia',
        help='Claves de contingencia relacionadas con esta empresa.'
    )


class CompanyContingencyKey(models.Model):

    _name = 'res.company.contingency.key'
    _description = 'Claves de Contingencia'

    @api.model
    def _get_company(self):  # , cr, uid, context):
        if self._context.get('company_id', False):
            return self._context.get('company_id')
        else:
            return self.env.user.company_id.id

    key = fields.Char('Clave', size=37, required=True)
    used = fields.Boolean('¿Utilizada?', readonly=True)
    company_id = fields.Many2one(
        'res.company',
        'Empresa',
        required=True,
        default=_get_company
    )

    _sql_constraints = [
        (
            'key_unique',
            'unique(key)',
            u'Clave de contingencia asignada debe ser única.'
        )
    ]
