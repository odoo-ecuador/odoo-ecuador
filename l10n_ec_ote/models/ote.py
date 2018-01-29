# -*- coding: utf-8 -*-
from odoo import models, fields


class Canton(models.Model):
    _name = 'l10n_ec_ote.canton'
    _description = 'Cantones de una provincia'

    state_id = fields.Many2one(
        comodel_name='res.country.state', 
        ondelete='restrict', 
        string='State', 
    )
    name = fields.Char(string='Canton', )
    code = fields.Char(string='Code', )


class Parish(models.Model):
    _name = 'l10n_ec_ote.parish'
    _description = 'Parroquias de un canton'
    
    canton_id = fields.Many2one(
        comodel_name='l10n_ec_ote.canton', 
        ondelete='restrict', 
        string='Canton', 
    )
    name = fields.Char(string='Parish', )
    code = fields.Char(string='Code', )
