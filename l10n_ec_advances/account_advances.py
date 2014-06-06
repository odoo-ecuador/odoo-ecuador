# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2014 Cristian Salamea. All Rights Reserved
#    cristian@ayni.io
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

from time import strftime

from osv import osv, fields
import decimal_precision as dp
from tools.translate import _
import netsvc

class AccountVoucher(osv.osv):
    _inherit = 'account.voucher'

    def action_print_report(self, cr, uid, ids, context):
        if context is None:
            context = {}        
        report_name = context.get('report', 'report_account_advances')
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['voucher_id'] = ids
        voucher = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [voucher.move_id.id], 'model': 'account.move','form': data}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,                              
            }
     
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id and journal.default_credit_account_id
        if context.get('extra_type') and context.get('extra_type') in ['advances','advances_custom']:
            return {'value': {'account_id': account_id.id} }
        else:
            res = super(AccountVoucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context)
            return res
    
    _columns = dict(
        extra_type = fields.char('Tipo Anticipos', size=32),
        thirdparty_name = fields.char('A nombre de', size=64),
        thirdparty = fields.boolean('Girado a otra persona ?'),
        )

    def _get_ext(self, cr, uid, context):
        return context.get('extra_type','ninguno')

    _defaults = dict(
        extra_type = _get_ext
        )

