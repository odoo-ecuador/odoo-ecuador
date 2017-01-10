# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    default_partner_id = fields.Many2one('res.partner', 'Default Partner')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    def action_pos_order_invoice(self):
        super(PosOrder, self).action_pos_order_invoice()
        for order in self:
            order.invoice_id and order.invoice_id.action_invoice_open()
