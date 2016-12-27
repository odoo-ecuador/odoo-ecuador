# -*- coding: utf-8 -*-
# © 2016 Diagram Software S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_invoice(self, order, lines):
        """
            Borramos el campo reference por defecto para que no choque con el
            constraint del módulo l10n_ec_withdrawing 'check_reference'
        """
        res = super(PurchaseOrder, self)._prepare_invoice(order, lines)
        if 'reference' in res:
            res.pop("reference")
        authorisation = self.env['account.authorisation'].search(
            [('partner_id', '=', res.get("partner_id")),
             ('in_type', '=', 'externo')],
            limit=1
        )
        if authorisation:
            res['auth_inv_id'] = authorisation.id
            res['reference'] = authorisation.name
        return res
