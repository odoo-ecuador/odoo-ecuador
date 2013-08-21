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
from tools.translate import _


class account_invoice(osv.osv):

    _inherit = 'account.invoice'

    def _number(self, cr, uid, ids, name, args, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, args):
            result[invoice.id] = invoice.invoice_number
        return result    

    _columns = {
        'invoice_number': fields.char('Numero de Factura', size=32, help="El numero de factura es unico"),
        'number': fields.function( _number, 'Numero', type='char', size=32, store=True, method=True),
        }

    def action_number(self, cr, uid, ids, context=None):
        obj_sequence = self.pool.get('ir.sequence')
        if context is None:
            context = {}
        #TODO: not correct fix but required a frech values before reading it.
        self.write(cr, uid, ids, {})

        for obj_inv in self.browse(cr, uid, ids, context=context):
            id = obj_inv.id
            invtype = obj_inv.type
            move_id = obj_inv.move_id and obj_inv.move_id.id or False
            reference = obj_inv.reference or ''

            if invtype in ('in_invoice', 'in_refund'):
                number = obj_inv.number
                name = obj_inv.move_id.name
                self.write(cr, uid, ids, {'internal_number': number, 'invoice_number': name})
                if not reference:
                    ref = self._convert_ref(cr, uid, number)
                else:
                    ref = reference
            else:
                if not obj_inv.journal_id.auth_id:
                    raise osv.except_osv('Error', 'No se ha definido una autorizacion en el diario')
                entidad = obj_inv.journal_id.auth_id.serie_entidad
                emision = obj_inv.journal_id.auth_id.serie_emision
                numero = obj_sequence.get_id(cr, uid, obj_inv.journal_id.auth_id.sequence_id.id)
                new_name = "%s-%s-%s" % (entidad, emision, numero)
                self.write(cr, uid, ids, {'invoice_number': new_name})
                ref = self._convert_ref(cr, uid, new_name)

            cr.execute('UPDATE account_move SET ref=%s ' \
                    'WHERE id=%s AND (ref is null OR ref = \'\')',
                    (ref, move_id))
            cr.execute('UPDATE account_move_line SET ref=%s ' \
                    'WHERE move_id=%s AND (ref is null OR ref = \'\')',
                    (ref, move_id))
            cr.execute('UPDATE account_analytic_line SET ref=%s ' \
                    'FROM account_move_line ' \
                    'WHERE account_move_line.move_id = %s ' \
                        'AND account_analytic_line.move_id = account_move_line.id',
                        (ref, move_id))

            for inv_id, name in self.name_get(cr, uid, [id]):
                ctx = context.copy()
                if obj_inv.type in ('out_invoice', 'out_refund'):
                    ctx = self.get_log_context(cr, uid, context=ctx)
                message = _('Invoice ') + " '" + name + "' "+ _("is validated.")
                self.log(cr, uid, inv_id, message, context=ctx)
            self.pool.get('account.invoice.line').asset_create(cr, uid, obj_inv.invoice_line)
        return True

account_invoice()
