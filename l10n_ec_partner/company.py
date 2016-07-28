# -*- coding: utf-8 -*-

from openerp import models, fields


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    tradename = fields.Char('Nombre Comercial', size=300)
