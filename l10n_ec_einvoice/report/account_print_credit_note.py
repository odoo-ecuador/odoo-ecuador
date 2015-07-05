# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw

class account_credit_note(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_credit_note, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_number_invoice': self.get_number_invoice,
            'get_date_invoice': self.get_date_invoice,
            'get_amount_invoice': self.get_amount_invoice,
        })
        
    def get_number_invoice(self, object):
        invoice_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('number','=',object.name)])
        return self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_ids)[0].supplier_invoice_number
                                  
    def get_date_invoice(self, object):
        invoice_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('number','=',object.name)])
        return self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_ids)[0].date_invoice

    def get_amount_invoice(self, object):
        invoice_ids = self.pool.get('account.invoice').search(self.cr, self.uid, [('number','=',object.name)])
        return self.pool.get('account.invoice').browse(self.cr, self.uid, invoice_ids, context = self.context).amount_pay
        
report_sxw.report_sxw(
    'report.account.credit_note',
    'account.invoice',
    'addons/l10n_ec_e-invoice/report/account_print_credit_note.rml',
    parser=account_credit_note
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
