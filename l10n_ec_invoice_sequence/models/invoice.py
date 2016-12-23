# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import (
    api,
    fields,
    models
)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.one
    @api.depends(
        'state',
        'reference'
    )
    def _get_invoice_number(self):
        """
        Calcula el numero de factura segun el
        establecimiento seleccionado
        """
        if self.reference:
            self.invoice_number = '{0}{1}{2}'.format(
                self.auth_inv_id.serie_entidad,
                self.auth_inv_id.serie_emision,
                self.reference
            )
        else:
            self.invoice_number = '*'

    invoice_number = fields.Char(
        compute='_get_invoice_number',
        store=True,
        readonly=True,
        copy=False
    )
    internal_inv_number = fields.Char('Numero Interno', copy=False)

    @api.multi
    def action_number(self):
        self.ensure_one()
        if self.type not in ['out_invoice', 'liq_purchase']:
            return
        number = self.internal_inv_number
        if not number:
            sequence = self.journal_id.auth_id.sequence_id
            number = sequence.next_by_id()
        self.write({'reference': number, 'internal_inv_number': number})
