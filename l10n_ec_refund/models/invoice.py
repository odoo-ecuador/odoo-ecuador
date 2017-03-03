# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):  # noqa
        vals = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date, description, journal_id)  # noqa
        vals.update({'origin': invoice.invoice_number})
        return vals


class AccountInvoiceRefund(models.TransientModel):

    _inherit = 'account.invoice.refund'

    @api.model
    def _get_reason(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if not active_id:
            return ''
        inv = self.env['account.invoice'].browse(active_id)
        return inv.invoice_number

    description = fields.Char(default=_get_reason)
