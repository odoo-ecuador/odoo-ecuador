# -*- coding: utf-8 -*-
# © 2016 Cristian Salamea <cristian.salamea@ayni.com.ec>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from . import amount_to_text_es


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    check_report_id = fields.Many2one(
        'ir.actions.report.xml',
        'Formato de Cheque'
    )


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    third_party_name = fields.Char(
        'A nombre de Tercero',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    to_third_party = fields.Boolean(
        'A nombre de terceros ?',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    @api.onchange('amount')
    def _onchange_amount(self):
        if hasattr(super(AccountPayment, self), '_onchange_amount'):
            super(AccountPayment, self)._onchange_amount()
        check_amount_in_words = amount_to_text_es.amount_to_text(self.amount, lang='en')  # noqa
        self.check_amount_in_words = check_amount_in_words

    @api.multi
    def do_print_checks(self):
        """
        Validate numbering
        Print from journal check template
        """
        for payment in self:
            report = payment.journal_id.check_report_id
            return self.env['report'].get_action(
                payment,
                report.report_name
            )
