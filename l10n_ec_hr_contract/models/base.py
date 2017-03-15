# -*- coding: utf-8 -*-
# © 2016 Cristian Salamea <cristian.salamea@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class HrContractBranch(models.Model):
    _name = 'hr.contract.branch'

    code = fields.Char('Código', size=5, required=True)
    name = fields.Char('Rama', size=64, required=True)


class HrContractCommision(models.Model):
    _name = 'hr.contract.commision'

    code = fields.Char('Código', size=5, required=True)
    name = fields.Char('Comisión', size=64, required=True)


class HrContractCode(models.Model):
    _name = 'hr.contract.code'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, u'{0} {1}'.format(rec.code, rec.name)))
        return result

    code = fields.Char('Código IESS', size=32, required=True, index=True)
    name = fields.Char('Cargo', size=128, required=True)
    code_structure = fields.Selection(
        [
            ('B1', 'B1'),
            ('B2', 'B2'),
            ('B3', 'B3'),
            ('C1', 'C1'),
            ('C2', 'C2'),
            ('C3', 'C3'),
            ('D1', 'D1'),
            ('D2', 'D2'),
            ('E1', 'E1'),
            ('E2', 'E2'),
        ],
        'Estructura Ocupacional',
        required=True,
        default='E1'
    )
    rama_id = fields.Many2one('hr.contract.branch', 'Rama', required=True)
    commision_id = fields.Many2one(
        'hr.contract.commision',
        'Comisión',
        required=True
    )
