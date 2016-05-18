# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class ProductCategory(osv.osv):
    _inherit = 'product.category'

    _columns = {
        'taxes_id': fields.many2many(
            'account.tax', 'categ_taxes_rel',
            'prod_id', 'tax_id', 'Customer Taxes',
            domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['sale', 'all'])]),  # noqa
        'supplier_taxes_id': fields.many2many(
            'account.tax',
            'categ_supplier_taxes_rel', 'prod_id', 'tax_id',
            'Supplier Taxes',
            domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['purchase', 'all'])]),  # noqa
    )
