# -*- coding: utf-8 -*-

from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    taxes_id = fields.Many2many(
            'account.tax', 'categ_taxes_rel',
            'prod_id', 'tax_id', 'Customer Taxes',
            domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['sale', 'all'])])  # noqa
    supplier_taxes_id = fields.Many2many(
            'account.tax',
            'categ_supplier_taxes_rel', 'prod_id', 'tax_id',
            'Supplier Taxes',
            domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['purchase', 'all'])])  # noqa
