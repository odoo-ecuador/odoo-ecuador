# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2012 Gnuthink Software Co. Ltd. All Rights Reserved
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

from openerp.osv import osv, fields


class AccountMove(osv.osv):

    _inherit = 'account.move'

    def get_reconcile(self, cr, uid, id, type, context):
        if isinstance(id, list):
            return False
        move = self.browse(cr, uid, id, context)
        types = ['payable', 'receivable']
        if type:
            types = type
        res = []
        for line in move.line_id:
            if line.account_id.type in types:
                res.append(line.id)
        return res
    
AccountMove()


class WizardReconcile(osv.osv_memory):

    _name = 'wizard.reconcile.invoice'

    def _get_amount(self, cr, uid, context=None):
        MSG = 'En el estado actual del documento no puede realizar esta acción.'
        if context is None:
            context = {}
        obj_id = context.get('active_id')
        inv = self.pool.get('account.invoice').browse(cr, uid, obj_id)
        if inv.state != 'open':
            raise osv.except_osv('Error',
                                 MSG)
        return inv.residual

    def act_cancel(self, cr, uid, ids, context):
        return {'type':'ir.actions.act_window_close'}

    def act_reconcile(self, cr, uid, ids, context=None):
        TYPE = {'out_invoice': 'receivable',
                'in_invoice': 'payable'}
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        wiz = self.browse(cr, uid, ids)[0]
        obj_id = context.get('active_id')
        inv = self.pool.get('account.invoice').browse(cr, uid, obj_id)
        torec_inv = move_obj.get_reconcile(cr, uid, inv.move_id.id,
                                           [TYPE[inv.type]], context)
        torec_adv = move_obj.get_reconcile(cr, uid, wiz.advance_id.move_id.id,
                                           [TYPE[inv.type]], context)
        if len(torec_inv) == len(torec_adv):
            print torec_inv, torec_adv
            move_line_obj.reconcile(cr, uid, torec_inv+torec_adv)
        return {'type': 'ir.actions.act_window_close'}

    def onchange_advance(self, cr, uid, ids, advance_id):
        if advance_id:
            res = self.pool.get('account.advances').read(cr, uid, advance_id, ['amount'])
            return {'value': {'amount_advance': res['amount']}} 

    _columns = dict(
        advance_id = fields.many2one('account.advances',
                                     string='Egreso',
                                     required=True,
                                     domain=[('type','=','out_advance')]),
        amount_advance = fields.related('advance_id', 'amount',
                                        string='Monto Egreso', readonly=True),
        amount = fields.float('Monto Factura', required=True),
        write_off_id = fields.many2one('account.account', string='Desajuste',
                                       domain=[('type','<>','view')]),
        state = fields.selection((('choose', 'choose'),
                                    ('export', 'export')))
        )

    _defaults = dict(
        amount = _get_amount,
        state = 'choose'
        )

WizardReconcile()
