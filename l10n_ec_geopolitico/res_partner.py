# -*- coding: utf-8 -*-

from openerp import models, fields

class res_partner(models.Model):
    _inherit = 'res.partner'

    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict', default="base.ec")
    canton_id = fields.Many2one('l10n_ec_geopolitico.canton', ondelete='restrict', string="Cantón")
    parroquia_id = fields.Many2one('l10n_ec_geopolitico.parroquia', ondelete='restrict', string="Parroquia")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
