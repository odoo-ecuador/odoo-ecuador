# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2009 GnuThink Software All Rights Reserved
#    info@gnuthink.com
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class wizard_book_retention(osv.osv_memory):

    _name = 'wizard.book.retention'

    def _load_sequence(self, cr, uid, context):
        j_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','purchase')])
        journals = self.pool.get('account.journal').browse(cr, uid, j_ids)
        res = []
        for j in journals:
            if j.auth_ret_id:
                res.append((j.auth_ret_id.sequence_id.id, j.auth_ret_id.sequence_id.name))
        return res

    def _get_number(self, cr, uid, context=None):
        if context is None:
            context = {}
        return 0

    def act_cancel(self, cr, user_id, ids, context):
        return {'type':'ir.actions.act_window_close'}

    def act_book_number(self, cr, uid, ids, context):
        obj = self.browse(cr, uid, ids, context)[0]
        self.pool.get('ir.sequence').write(cr, uid, [obj.sequence], {'number_next': obj.book_number+1})
        self.pool.get('account.retention.cache').create(cr, uid, {'name': obj.book_number})
        return self.write(cr, uid, [obj.id], {'state': 'export'})

    _columns = {
        'sequence': fields.selection( _load_sequence,
                                         'Secuencia de Retenciones'),
        'book_number': fields.integer('Numero a Reservar'),
        'state' : fields.selection((('choose', 'choose'),
                                    ('export', 'export'))),
        }

    _defaults = {
        'state' : 'choose',
        'book_number': _get_number
    }

    def onchange_sequence(self, cr, uid, ids, sequence):
        if sequence:
            ir_s = self.pool.get('ir.sequence').browse(cr, uid, sequence)
            return {'value': {'book_number':ir_s.number_next}}
        else:
            return {}

wizard_book_retention()
