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

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        doc_code = {
            'out_invoice': '18',
            'in_invoice': '07',
            'liq_purchase': '03',
            'out_refund': '04'
        }
        super(AccountInvoice, self)._onchange_journal_id()
        if self.journal_id:
            inv_type = self.type
            auth = self.env['account.authorisation'].search([('type_id.code', '=', doc_code[inv_type])], limit=1)  # noqa
            # TODO: cargar num de retencion
            if inv_type in ['out_invoice', 'liq_purchase', 'out_refund']:
                if auth is None:
                    return {
                        'warning': {
                            'title': 'Error',
                            'message': u'No se ha configurado una autorización.'  # noqa
                        }
                    }
                number = '{0}'.format(
                    str(auth.sequence_id.number_next_actual).zfill(9)
                )
                self.auth_inv_id = auth.id
                self.reference = number

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
