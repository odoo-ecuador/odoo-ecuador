# -*- coding: utf-8 -*-
# © <2016> <Alcides Rivera VIRTUALSAMI CIA LTDA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields

class CountryCity(models.Model):
  
    _name = 'res.country.city'
    _description = "City model"
    
    country_id = fields.Many2one(
        'res.country', 'Country',
        required=True
        )
    state_id = fields.Many2one(
        'res.country.state', 'State',
        domain="[('country_id','=',country_id)]",
        required=True
        )
    name = fields.Char(
        'Name', 
        size=64, 
        required=True
        )
    code = fields.Char(
        'Code', 
        size=4, 
        required=True
        )

