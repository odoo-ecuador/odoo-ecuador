# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class AccountInvoice(osv.osv):

    _inherit = 'account.invoice'

    def action_number(self, cr, uid, ids, context=None):
        """
        Copiado el metodo del ERP
        CHECK: modificar para numeracion automatica en venta?
        """
        if context is None:
            context = {}
        # TODO: not correct fix but required a frech values before reading it.
        self.write(cr, uid, ids, {})

        for obj_inv in self.browse(cr, uid, ids, context=context):
            invtype = obj_inv.type
            number = obj_inv.number
            data_number = {'internal_number': number}

            if invtype in ['out_invoice', 'liq_purchase']:
                auth = obj_inv.journal_id.auth_id
                number = obj_inv.internal_number
                if not number:
                    tmp_number = self.pool.get('ir.sequence').get(cr, uid, auth.sequence_id.code)
                    number = '{0}{1}{2}'.format(auth.serie_entidad, auth.serie_emision, tmp_number)
                data_number.update({'number': number})

            move_id = obj_inv.move_id and obj_inv.move_id.id or False
            reference = obj_inv.reference or ''

            self.write(cr, uid, ids, data_number)

            if invtype in ('in_invoice', 'in_refund'):
                if not reference:
                    ref = self._convert_ref(cr, uid, number)
                else:
                    ref = reference
            else:
                ref = self._convert_ref(cr, uid, number)

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
        return True
