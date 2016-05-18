# -*- coding: utf-8 -*-
# © <2016> <Alcides Rivera VIRTUALSAMI CIA LTDA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import fields, osv


class CountryCity(osv.osv):
    _name = 'res.country.city'
    _description = "City model"

    _columns = {
        'country_id': fields.many2one(
            'res.country', 'Country',
            required=True
        ),
        'state_id': fields.many2one(
            'res.country.state', 'State',
            domain="[('country_id','=',country_id)]",
            required=True
        ),
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=4, required=True),
    }
