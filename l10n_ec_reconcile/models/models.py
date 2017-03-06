# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import calendar

from odoo import api, fields, models
from odoo.exceptions import Warning as UserError


class AccountBankReconcile(models.Model):

    _name = 'account.bank.reconcile'
    _order = 'date_start DESC'

    @api.multi
    def unlink(self):
        for ob in self:
            if ob.state != 'draft':
                raise UserError('No puede eliminar un documento validado.')
        super(AccountBankReconcile, self).unlink()
        return True

    @api.model
    def _default_date_start(self):
        today = datetime.date.today()
        today = today.replace(day=1)
        res = fields.Date.to_string(today)
        return res

    @api.model
    def _default_date_stop(self):
        today = datetime.date.today()
        first, last = calendar.monthrange(today.year, today.month)
        today = today.replace(day=last)
        res = fields.Date.to_string(today)
        return res

    @api.model
    def _default_balance(self):
        first = self.search([], limit=1)
        return first.balance_stop

    name = fields.Char(
        'Codigo',
        required=True,
        default='/',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    journal_id = fields.Many2one(
        'account.journal',
        'Banco',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    date_start = fields.Date(
        'Desde',
        required=True,
        default=_default_date_start,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    date_stop = fields.Date(
        'Hasta',
        required=True,
        default=_default_date_stop,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    balance_start = fields.Monetary(
        'Balance Inicial',
        default=_default_balance,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    balance_stop = fields.Monetary(
        'Balance Final',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Moneda'
    )
    line_ids = fields.One2many(
        'account.move.line',
        'concile_id',
        'Detalle'
    )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('done', 'Realizado')
        ],
        string='Estado',
        required=True,
        default='draft'
    )

    @api.multi
    def action_load_entries(self):
        for obj in self:
            obj.line_ids.unlink()
            domain = [
                ('journal_id', '=', self.journal_id.id),
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_stop),
                ('account_id', '=', self.journal_id.default_debit_account_id.id),  # noqa
                ('conciled', '=', False)
            ]
            lines = self.env['account.move.line'].search(domain)
            not_conciled = self.env['account.move.line'].search([
                ('journal_id', '=', self.journal_id.id),
                ('account_id', '=', self.journal_id.default_debit_account_id.id),  # noqa
                ('conciled', '=', False)
            ])
            lines.write({'concile_id': obj.id})
            not_conciled.write({'concile_id': obj.id})
        return True

    @api.multi
    def action_done(self):
        for obj in self:
            debits = sum([l.debit for l in obj.line_ids.filtered(lambda r: r.conciled)])  # noqa
            credits = sum([l.credit for l in obj.line_ids.filtered(lambda r: r.conciled)])  # noqa
            computed = self.balance_start + debits - credits
            if not obj.balance_stop == computed:
                raise UserError('El balance final es incorrecto.')
            code = self.env['ir.sequence'].next_by_code('bank.reconcile')
            obj.write({'state': 'done', 'name': code})
        return True

    @api.multi
    def action_print(self):
        pass


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def action_done(self):
        self.write({'conciled': not self.conciled})

    conciled = fields.Boolean('Conciliado ?')
    concile_id = fields.Many2one(
        'account.bank.reconcile',
        'Hoja de Conciliacion'
    )
