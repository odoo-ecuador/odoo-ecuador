# -*- coding: utf-8 -*-

import time
import logging

from osv import osv, fields


class ProductCategory(osv.osv):
    _inherit = 'product.category'

    _columns = dict(
        taxes_id = fields.many2many('account.tax', 'categ_taxes_rel',
                                    'prod_id', 'tax_id', 'Customer Taxes',
                                    domain=[('parent_id','=',False),('type_tax_use','in',['sale','all'])]),
        supplier_taxes_id = fields.many2many('account.tax',
                                             'categ_supplier_taxes_rel', 'prod_id', 'tax_id',
                                             'Supplier Taxes', domain=[('parent_id', '=', False),('type_tax_use','in',['purchase','all'])]),        
        )


