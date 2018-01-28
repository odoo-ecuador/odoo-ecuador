# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    #Limpia provincia y ciudad al pulsar campo pais
    @api.onchange('country_id')
    def push_country(self):
        return{'value':{'state_id':'','canton_id':'','parish_id':''}}

    @api.onchange('state_id')
    def push_state(self):
        return{'value':{'canton_id':'','parish_id':''}}
 
    @api.onchange('canton_id')
    def push_canton(self):
        return{'value':{'parish_id':''}}

    @api.multi
    @api.onchange("canton_id")
    def _onchange_canton_id(self):
        for r in self:
            if r.canton_id:
                r.city = r.canton_id.name or ''
                
#             if r.canton_id and not r.city:
#                 r.city = r.canton_id.name.capitalize() or ''
    canton_id = fields.Many2one(
        comodel_name='l10n_ec_ote.canton', 
        ondelete='restrict', 
        string='Canton', 
    )
    parish_id = fields.Many2one(
        comodel_name='l10n_ec_ote.parish', 
        ondelete='restrict', 
        string='Parish', 
    )
    