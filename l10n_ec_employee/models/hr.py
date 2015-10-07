# -*- coding: utf-8 -*-

import time

from openerp.osv import osv, fields, orm


class HrEmployee(orm.Model):
    _inherit = 'hr.employee'
    _order = 'last_name ASC'

    def onchange_identificador(self, cr, uid, ids, identificador):
        pass

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for rec in self.browse(cr, uid, ids):
            texto = u'{0} {1}'.format(rec.last_name, rec.name)
            res.append((rec.id, texto))
        return res

    _columns = dict(
        last_name = fields.char('Apellidos', required=True, size=64),        
    )
