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

    name = fields.Char('Codigo', required=True, default='/')
    journal_id = fields.Many2one(
        'account.journal',
        'Banco',
        required=True
    )
    date_start = fields.Date(
        'Desde',
        required=True,
        default=_default_date_start
    )
    date_stop = fields.Date(
        'Hasta',
        required=True,
        default=_default_date_stop
    )
    balance_start = fields.Monetary(
        'Balance Inicial',
        default=_default_balance
    )
    balance_stop = fields.Monetary('Balance Final')
    currency_id = fields.Many2one(
        'res.currency',
        'Moneda'
    )
    line_ids = fields.One2many(
        'account.bank.reconcile.line',
        'reconcile_id',
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
    def process_lines(self, move_lines):
        for line in move_lines:
            data = {
                'reconcile_id': self.id,
                'ref': line.ref or '/',
                'date': line.date,
                'account_id': line.account_id.id,
                'partner_id': line.partner_id.id,
                'debit': line.debit,
                'credit': line.credit
            }
            self.env['account.bank.reconcile.line'].create(data)

    @api.multi
    def action_load_entries(self):
        for obj in self:
            obj.line_ids.unlink()
            domain = [
                ('journal_id', '=', self.journal_id.id),
                ('date', '>=', self.date_start),
                ('date', '<=', self.date_stop),
                ('account_id', '=', self.journal_id.default_debit_account_id.id)  # noqa
            ]
            lines = self.env['account.move.line'].search(domain)
            obj.process_lines(lines)
        return True

    @api.multi
    def action_done(self):
        for obj in self:
            debits = sum([l.debit for l in obj.line_ids.filtered(lambda r: r.done)])  # noqa
            credits = sum([l.credit for l in obj.line_ids.filtered(lambda r: r.done)])  # noqa
            computed = self.balance_start + debits - credits
            if not obj.balance_stop == computed:
                raise UserError('El saldo final es incorrecto')
            obj.write({'state': 'done'})
        return True


class AccountBankReconcileLine(models.Model):

    _name = 'account.bank.reconcile.line'

    @api.multi
    def action_done(self):
        self.write({'done': not self.done})

    reconcile_id = fields.Many2one(
        'account.bank.reconcile',
        'Sheet',
        ondelete='cascade'
    )
    ref = fields.Char('Ref', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        'Empresa',
        required=True
    )
    account_id = fields.Many2one(
        'account.account',
        'Cuenta'
    )
    date = fields.Date('Fecha')
    debit = fields.Monetary('Debito')
    credit = fields.Monetary('Credito')
    done = fields.Boolean('Depositado / Cobrado ?')
    currency_id = fields.Many2one(
        'res.currency',
        'Moneda'
    )
    # TODO: decidir por tipo o por debit/credit
