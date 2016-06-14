# -*- coding: utf-8 -*-

from openerp import (
    models,
    fields,
    api
)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.one
    @api.depends(
        'state',
        'supplier_invoice_number'
    )
    def _get_invoice_number(self):
        """
        Calcula el numero de factura segun el
        establecimiento seleccionado
        """
        if self.supplier_invoice_number:
            self.invoice_number = '{0}{1}{2}'.format(
                self.auth_inv_id.serie_entidad,
                self.auth_inv_id.serie_emision,
                self.supplier_invoice_number
            )
        else:
            self.invoice_number = '*'

    invoice_number = fields.Char(
        compute='_get_invoice_number',
        store=True,
        readonly=True,
        copy=False
    )
