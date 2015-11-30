# -*- coding: utf-8 -*-

import time

from openerp.osv import osv, fields, orm


class HrEmployee(orm.Model):
    _inherit = 'hr.employee'
    _order = 'lastname ASC'

    def onchange_identificador(self, cr, uid, ids, identificador):
        pass

    def _auto_init(self, cr, context=None):
        """pre-create and fill column lastname so that the constraint
        setting will not fail"""
        self._field_create(cr, context=context)
        column_data = self._select_column_data(cr)
        if 'lastname' not in column_data:
            field = self._columns['lastname']
            cr.execute('ALTER TABLE "%s" ADD COLUMN "lastname" %s' %
                       (self._table,
                        orm.pg_varchar(field.size)))
            cr.execute('UPDATE hr_employee '
                       'SET lastname = name_related '
                       'WHERE name_related IS NOT NULL')
        return super(HrEmployee, self)._auto_init(cr, context=context)

    def create(self, cursor, uid, vals, context=None):
        firstname = vals.get('firstname')
        lastname = vals.get('lastname')
        if firstname or lastname:
            names = (lastname, firstname)
            vals['name'] = " ".join(s for s in names if s)
        else:
            vals['lastname'] = vals['name']
        return super(HrEmployee, self).create(
            cursor, uid, vals, context=context)    

    _columns = dict(
        firstname = fields.char('Nombres', size=64),
        lastname = fields.char('Apellidos', required=True, size=64),        
    )


class HrFamily(orm.Model):
    _name = 'hr.family'

    _columns = dict(
        name = fields.char()
    )
