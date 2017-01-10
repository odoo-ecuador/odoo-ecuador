# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import (
    api,
    fields,
    models
)
from openerp.exceptions import (
    Warning as UserError
    )
import openerp.addons.decimal_precision as dp


class AccountWithdrawing(models.Model):
    """ Implementacion de documento de retencion """

    @api.multi
    @api.depends('tax_ids.amount')
    def _compute_total(self):
        """
        TODO
        """
        self.amount_total = sum(tax.amount for tax in self.tax_ids)

    @api.multi
    def _get_period(self):
        result = {}
        for obj in self:
            result[obj.id] = self.env['account.period'].find(obj.date)[0]
        return result

    @api.multi
    def _get_in_type(self):
        context = self._context
        return context.get('in_type', 'ret_out_invoice')

    STATES_VALUE = {'draft': [('readonly', False)]}

    _name = 'account.retention'
    _description = 'Withdrawing Documents'
    _order = 'name ASC'

    name = fields.Char(
        'Número',
        size=64,
        readonly=True,
        required=True,
        states=STATES_VALUE
        )
    internal_number = fields.Char(
        'Número Interno',
        size=64,
        readonly=True
        )
    manual = fields.Boolean(
        'Numeración Manual',
        readonly=True,
        states=STATES_VALUE,
        default=True
        )
    num_document = fields.Char(
        'Num. Comprobante',
        size=50,
        readonly=True,
        states=STATES_VALUE
        )
    auth_id = fields.Many2one(
        'account.authorisation',
        'Autorizacion',
        readonly=True,
        states=STATES_VALUE,
        domain=[('in_type', '=', 'interno')]
        )
    type = fields.Selection(
        related='invoice_id.type',
        string='Tipo Comprobante',
        readonly=True,
        store=True
        )
    in_type = fields.Selection(
        [
            ('ret_in_invoice', u'Retención a Proveedor'),
            ('ret_out_invoice', u'Retención de Cliente')
        ],
        string='Tipo',
        readonly=True,
        default=_get_in_type
        )
    date = fields.Date(
        'Fecha Emision',
        readonly=True,
        states={'draft': [('readonly', False)]}, required=True)
    tax_ids = fields.One2many(
        'account.invoice.tax',
        'retention_id',
        'Detalle de Impuestos',
        readonly=True,
        states=STATES_VALUE
        )
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Documento',
        required=False,
        readonly=True,
        states=STATES_VALUE,
        domain=[('state', '=', 'open')]
        )
    partner_id = fields.Many2one(
        'res.partner',
        string='Empresa',
        required=True,
        readonly=True,
        states=STATES_VALUE
        )
    move_id = fields.Many2one(
        related='invoice_id.move_id',
        string='Asiento Contable',
        readonly=True,
        store=True
        )
    move_ret_id = fields.Many2one(
        'account.move',
        string='Asiento Retención',
        readonly=True,
        )
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('done', 'Validado'),
            ('cancel', 'Anulado')
        ],
        readonly=True,
        string='Estado',
        default='draft'
        )
    amount_total = fields.Float(
        compute='_compute_total',
        string='Total',
        store=True,
        digits=dp.get_precision('Account')
        )
    to_cancel = fields.Boolean(
        string='Para anulación',
        readonly=True,
        states=STATES_VALUE
        )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        change_default=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['res.company']._company_default_get('account.invoice')  # noqa
        )

    _sql_constraints = [
        (
            'unique_number_partner',
            'unique(name,partner_id,type)',
            u'El número de retención es único.'
        )
    ]

    @api.onchange('name')
    def _onchange_name(self):
        if len(self.name) > 9 or not self.name.isdigit():
            raise UserError(u'Valor para número incorrecto.')
        if self.name:
            self.name = self.name.zfill(9)

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.state in ['done']:
                raise UserError('No se permite borrar retenciones validadas.')
        res = super(AccountWithdrawing, self).unlink()
        return res

    @api.onchange('name')
    def onchange_name(self):
        if self.name and self.type == 'in_invoice':
            self.name = self.name.zfill(9)

    @api.onchange('to_cancel')
    def onchange_tocancel(self):
        if self.to_cancel:
            company = self.env['res.company']._company_default_get('account.invoice')
            self.partner_id = company.partner_id.id

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        if not self.invoice_id:
            return
        self.num_document = self.invoice_id.invoice_number
        self.type = self.invoice_id.type

    @api.multi
    def action_number(self, number):
        for wd in self:
            if wd.to_cancel:
                raise UserError('El documento fue marcado para anular.')
            if wd.type == 'out_invoice':
                if not len(self.name) == 15:
                    raise UserError('El número para retenciones de clientes es de 15 dígitos.')  # noqa
                return True

            sequence = wd.auth_id.sequence_id
            if number.isdigit():
                wd_number = number[6:].zfill(sequence.padding)
            elif wd.internal_number:
                wd_number = wd.internal_number
            else:
                wd_number = self.env['ir.sequence'].get_id(sequence.id)
            number = '{0}{1}{2}'.format(wd.auth_id.serie_entidad,
                                        wd.auth_id.serie_emision,
                                        wd_number)
            wd.write({'name': number, 'internal_number': number})
        return True

    @api.multi
    def action_validate(self, number=None):
        """
        @number: Número para usar en el documento
        """
        self.action_number(number)
        return self.write({'state': 'done'})

    @api.multi
    def button_validate(self):
        """
        Botón de validación de Retención que se usa cuando
        se creó una retención manual, esta se relacionará
        con la factura seleccionada.
        """
        for ret in self:
            if not ret.tax_ids:
                raise UserError('No ha aplicado impuestos.')
            self.action_validate()
            if ret.manual:
                ret.invoice_id.write({'retention_id': ret.id})
                self.create_move()
        return True

    @api.multi
    def create_move(self):
        """
        Generacion de asiento contable para aplicar como
        pago a factura relacionada
        """
        for ret in self:
            inv = ret.invoice_id
            move_data = {
                'journal_id': inv.journal_id.id,
                'ref': ret.name,
                'date': ret.date
            }
            total_counter = 0
            lines = []
            for line in ret.tax_ids:
                if not line.manual:
                    continue
                lines.append((0, 0, {
                    'partner_id': ret.partner_id.id,
                    'account_id': line.account_id.id,
                    'name': ret.name,
                    'debit': abs(line.amount),
                    'credit': 0.00
                }))

                total_counter += abs(line.amount)

            lines.append((0, 0, {
                'partner_id': ret.partner_id.id,
                'account_id': inv.account_id.id,
                'name': ret.name,
                'debit': 0.00,
                'credit': total_counter
            }))
            move_data.update({'line_ids': lines})
            move = self.env['account.move'].create(move_data)
            acctype = self.type == 'in_invoice' and 'payable' or 'receivable'
            inv_lines = inv.move_id.line_ids
            acc2rec = inv_lines.filtered(lambda l: l.account_id.internal_type == acctype)  # noqa
            acc2rec += move.line_ids.filtered(lambda l: l.account_id.internal_type == acctype)  # noqa
            acc2rec.auto_reconcile_lines()
            ret.write({'move_ret_id': move.id})
        return True

    @api.multi
    def action_cancel(self):
        """
        Método para cambiar de estado a cancelado el documento
        """
        for ret in self:
            if ret.move_ret_id:
                raise UserError(u'Retención conciliada con la factura, no se puede anular.')  # noqa
            elif ret.auth_id.is_electronic:
                raise UserError(u'No puede anular un documento electrónico.')
            data = {'state': 'cancel'}
            if ret.to_cancel:
                # FIXME
                if len(ret.name) == 9 and ret.auth_id.is_valid_number(int(ret.name)):  # noqa
                    number = ret.auth_id.serie_entidad + ret.auth_id.serie_emision + ret.name  # noqa
                    data.update({'name': number})
                else:
                    raise UserError(
                        u'El número no es de 9 dígitos y/o no pertenece a la autorización seleccionada.'  # noqa
                    )
            self.write({'state': 'cancel'})
        return True

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_print(self):
        # Método para imprimir comprobante contable
        return self.env['report'].get_action(
            self.move_id,
            'l10n_ec_withholding.account_withholding'
        )
