# -*- coding: utf-8 -*-

from openerp.osv import fields, osv


class Company(osv.osv):
    _name = "res.company"
    _inherit = "res.company"

    _columns = {
        'tradename': fields.char('Nombre Comercial', size=300),
    }
