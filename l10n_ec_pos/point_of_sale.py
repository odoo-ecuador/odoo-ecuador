# -*- coding: utf-8 -*-
##############################################################################
#
#    Point of Sale - Ecuador
#    Copyright (C) 2017-Today Alcides Rivera <alcides@virtualsami.com.ec>
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

import time
import logging
import openerp.addons.decimal_precision as dp

from openerp.osv import osv, fields
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
	
class pos_order(osv.osv):
    _inherit = 'pos.order'
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        account_tax_obj = self.pool['account.tax']
        taxes_ids = [tax for tax in line.product_id.taxes_id if tax.company_id.id == line.order_id.company_id.id]
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        taxes = account_tax_obj.compute_all(cr, uid, taxes_ids, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
        val = 0.0
        for c in taxes:
            if 'vat' == c.get('tax_group'):
                val += c.get('amount', 0.0)
        return val

    def _amount_line_base(self, cr, uid, line, tax_group, context=None):
        account_tax_obj = self.pool['account.tax']
        taxes_ids = [tax for tax in line.product_id.taxes_id if tax.company_id.id == line.order_id.company_id.id]
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        taxes = account_tax_obj.compute_all(cr, uid, taxes_ids, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
        val = 0.0
        for c in taxes:
            if tax_group == c.get('tax_group'):
                val += price
        return val

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_vat': 0.0,
                'amount_vat_cero': 0.0,
                'amount_novat': 0.0,
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'amount_paid': 0.0,
                'amount_return':0.0,
            }
            val1 = val2 = vat = vat0 = novat = 0.0
            cur = order.pricelist_id.currency_id
            for payment in order.statement_ids:
                res[order.id]['amount_paid'] +=  payment.amount
                res[order.id]['amount_return'] += (payment.amount < 0 and payment.amount or 0)
            for line in order.lines:
                val1 += self._amount_line_tax(cr, uid, line, context=context)
                val2 += line.price_subtotal
                vat += self._amount_line_base(cr, uid, line, 'vat', context=context)
                vat0 += self._amount_line_base(cr, uid, line, 'vat0', context=context)
                novat += self._amount_line_base(cr, uid, line, 'novat', context=context)
            res[order.id]['amount_vat'] = cur_obj.round(cr, uid, cur, vat)
            res[order.id]['amount_vat_cero'] = cur_obj.round(cr, uid, cur, vat0)
            res[order.id]['amount_novat'] = cur_obj.round(cr, uid, cur, novat)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val1)
            amount_untaxed = cur_obj.round(cr, uid, cur, val2)
            res[order.id]['amount_total'] = res[order.id]['amount_tax'] + amount_untaxed
        return res

    _columns = {
        'amount_vat': fields.function(_amount_all, string='Base IVA', digits_compute=dp.get_precision('Account'), multi='all'),
        'amount_vat_cero': fields.function(_amount_all, string='Base Cero', digits_compute=dp.get_precision('Account'), multi='all'),
        'amount_novat': fields.function(_amount_all, string='Base No IVA', digits_compute=dp.get_precision('Account'), multi='all'),
        'amount_tax': fields.function(_amount_all, string='Taxes', digits_compute=dp.get_precision('Account'), multi='all'),
        'amount_total': fields.function(_amount_all, string='Total', digits_compute=dp.get_precision('Account'),  multi='all'),
        'amount_paid': fields.function(_amount_all, string='Paid', states={'draft': [('readonly', False)]}, readonly=True, digits_compute=dp.get_precision('Account'), multi='all'),
        'amount_return': fields.function(_amount_all, 'Returned', digits_compute=dp.get_precision('Account'), multi='all'),
    }

