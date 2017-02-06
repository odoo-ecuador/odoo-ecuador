# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import (
    api,
    models,
    _
)
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.model
    def _prepare_picking(self):
        # TODO: picking_type_id, location_id
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)  # noqa
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)  # noqa
        return {
            'picking_type_id': picking_type.id,
            'partner_id': self.partner_id.id,
            'date': self.date_invoice,
            'origin': self.reference,
            'location_dest_id': picking_type.default_location_dest_id.id,
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }

    @api.multi
    def create_picking(self):
        StockPicking = self.env['stock.picking']
        for inv in self:
            if any([ptype in ['product', 'consu'] for ptype in inv.invoice_line_ids.mapped('product_id.type')]):  # noqa
                res = inv._prepare_picking()
                picking = StockPicking.create(res)
                moves = inv.invoice_line_ids._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel')).action_confirm()  # noqa
                moves.force_assign()
                picking.do_transfer()
        return True

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open,
        # so we remove those already open
        # redefined to create withholding and numbering
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):  # noqa
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))  # noqa
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        to_open_invoices.action_number()
        to_open_invoices.action_withholding_create()
        to_open_invoices.create_picking()
        return to_open_invoices.invoice_validate()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _get_stock_move_price_unit(self):
        self.ensure_one()
        line = self[0]
        invoice = line.invoice_id
        price_unit = line.price_unit
        if line.invoice_line_tax_ids:
            price_unit = line.invoice_line_tax_ids.with_context(round=False).compute_all(price_unit, currency=invoice.currency_id, quantity=1.0)['total_excluded']  # noqa
        if line.uom_id.id != line.product_id.uom_id.id:
            price_unit *= line.uom_id.factor / line.product_id.uom_id.factor  # noqa
        if invoice.currency_id != invoice.company_id.currency_id:
            price_unit = invoice.currency_id.compute(price_unit, order.company_id.currency_id, round=False)  # noqa
        return price_unit

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            if line.product_id.type not in ['product', 'consu']:
                continue
            qty = 0.0
            price_unit = line._get_stock_move_price_unit()
            template = {
                'name': line.name or '',
                'product_id': line.product_id.id,
                'product_uom': line.uom_id.id,
                'date': line.invoice_id.date_invoice,
                'date_expected': line.invoice_id.date_invoice,
                'location_id': line.invoice_id.partner_id.property_stock_supplier.id,  # noqa
                'location_dest_id': picking.picking_type_id.default_location_dest_id.id,  # noqa
                'picking_id': picking.id,
                'partner_id': line.invoice_id.partner_id.id,
                'move_dest_id': False,
                'state': 'draft',
                'company_id': line.invoice_id.company_id.id,
                'price_unit': price_unit,
                'picking_type_id': picking.picking_type_id.id,
                'procurement_id': False,
                'origin': line.invoice_id.invoice_number,
                'route_ids': picking.picking_type_id.warehouse_id and [(6, 0, [x.id for x in picking.picking_type_id.warehouse_id.route_ids])] or [],  # noqa
                'warehouse_id': picking.picking_type_id.warehouse_id.id,
            }
            # Fullfill all related procurements with this po line
            diff_quantity = line.quantity - qty
            if float_compare(diff_quantity, 0.0, precision_rounding=line.uom_id.rounding) > 0:  # noqa
                template['product_uom_qty'] = diff_quantity
                done += moves.create(template)
        return done
