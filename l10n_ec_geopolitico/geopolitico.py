# -*- coding: utf-8 -*-

from openerp import models, fields

class Canton(models.Model):
    _name = 'l10n_ec_geopolitico.canton'
    state_id = fields.Many2one('res.country.state', ondelete='restrict', string="Provincia")
    name = fields.Char(string="Cantón")
    code = fields.Char(string="Código")

class Parroquia(models.Model):
    _name = 'l10n_ec_geopolitico.parroquia'
    canton_id = fields.Many2one('l10n_ec_geopolitico.canton', ondelete='restrict', string="Cantón")
    name = fields.Char(string="Parroquia")
    code = fields.Char(string="Código")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
