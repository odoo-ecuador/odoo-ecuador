# -*- coding: utf-8 -*-

import time

from openerp.osv import osv, fields, orm


class HrEmployee(orm.Model):
    _inherit = 'hr.employee'

    def onchange_identificador(self, cr, uid, ids, identificador):
        pass

    _columns = dict(
        last_name = fields.char('Apellidos', required=True, size=64),        
    )
