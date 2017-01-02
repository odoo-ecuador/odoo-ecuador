# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import (
    RedirectWarning,
    ValidationError,
    Warning as UserError
)


class AccountAtsDoc(models.Model):
    _name = 'account.ats.doc'
    _description = 'Tipos Comprobantes Autorizados'

    code = fields.Char('Código', size=2, required=True)
    name = fields.Char('Tipo Comprobante', size=64, required=True)


class AccountAtsSustento(models.Model):
    _name = 'account.ats.sustento'
    _description = 'Sustento del Comprobante'

    @api.multi
    @api.depends('code', 'type')
    def name_get(self):
        res = []
        for record in self:
            name = '%s - %s' % (record.code, record.type)
            res.append((record.id, name))
        return res

    _rec_name = 'type'

    code = fields.Char('Código', size=2, required=True)
    type = fields.Char('Tipo de Sustento', size=128, required=True)


class AccountAuthorisation(models.Model):

    _name = 'account.authorisation'
    _order = 'expiration_date desc'

    @api.multi
    @api.depends('type_id', 'num_start', 'num_end')
    def name_get(self):
        res = []
        for record in self:
            name = u'%s (%s-%s)' % (
                record.type_id.code,
                record.num_start,
                record.num_end
            )
            res.append((record.id, name))
        return res

    @api.one
    @api.depends('expiration_date')
    def _check_active(self):
        """
        Check the due_date to give the value active field
        """
        if not self.expiration_date:
            return
        now = datetime.strptime(time.strftime("%Y-%m-%d"), '%Y-%m-%d')
        due_date = datetime.strptime(self.expiration_date, '%Y-%m-%d')
        self.active = now < due_date

    def _get_type(self):
        return self._context.get('type', 'in_invoice')  # pylint: disable=E1101

    def _get_in_type(self):
        return self._context.get('in_type', 'externo')

    def _get_partner(self):
        partner = self.env.user.company_id.partner_id
        if self._context.get('partner_id'):
            partner = self._context.get('partner_id')
        return partner

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        partner_id = self.env.user.company_id.partner_id.id
        if values['partner_id'] == partner_id:
            name_type = '{0}_{1}'.format(values['name'], values['type_id'])
            sequence_data = {
                'name': name_type,
                'padding': 9,
                'number_next': values['num_start'],
                }
            seq = self.env['ir.sequence'].create(sequence_data)
            values.update({'sequence_id': seq.id})
        return super(AccountAuthorisation, self).create(values)

    @api.multi
    def unlink(self):
        inv = self.env['account.invoice']
        res = inv.search([('auth_inv_id', '=', self.id)])
        if res:
            raise UserError(
                'Esta autorización esta relacionada a un documento.'
            )
        return super(AccountAuthorisation, self).unlink()

    name = fields.Char('Num. de Autorización', size=128)
    serie_entidad = fields.Char('Serie Entidad', size=3, required=True)
    serie_emision = fields.Char('Serie Emision', size=3, required=True)
    num_start = fields.Integer('Desde')
    num_end = fields.Integer('Hasta')
    is_electronic = fields.Boolean('Documento Electrónico ?')
    expiration_date = fields.Date('Fecha de Vencimiento')
    active = fields.Boolean(
        compute='_check_active',
        string='Activo',
        store=True,
        default=True
        )
    in_type = fields.Selection(
        [('interno', 'Internas'),
         ('externo', 'Externas')],
        string='Tipo Interno',
        readonly=True,
        change_default=True,
        default=_get_in_type
        )
    type_id = fields.Many2one(
        'account.ats.doc',
        'Tipo de Comprobante',
        required=True
        )
    partner_id = fields.Many2one(
        'res.partner',
        'Empresa',
        required=True,
        default=_get_partner
        )
    sequence_id = fields.Many2one(
        'ir.sequence',
        'Secuencia',
        help='Secuencia Alfanumerica para el documento, se debe registrar cuando pertenece a la compañia',  # noqa
        ondelete='cascade'
        )

    _sql_constraints = [
        ('number_unique',
         'unique(partner_id,expiration_date,type_id)',
         u'La relación de autorización, serie entidad, serie emisor y tipo, debe ser única.'),  # noqa
        ]

    def is_valid_number(self, number):
        """
        Metodo que verifica si @number esta en el rango
        de [@num_start,@num_end]
        """
        if self.num_start <= number <= self.num_end:
            return True
        return False

    @api.constrains('expiration_date')
    def _check_type_active(self):
        res = self.search([('partner_id', '=', self.partner_id.id),
                           ('type_id', '=', self.type_id.id),
                           ('active', '=', True)])
        if res:
            MSG = u'Ya existe una autorización activa para %s' % self.type_id.name  # noqa
            raise ValidationError(MSG)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    authorisation_ids = fields.One2many(
        'account.authorisation',
        'partner_id',
        'Autorizaciones'
        )

    @api.multi
    def get_authorisation(self, type_document):
        map_type = {
            'out_invoice': '18',
            'in_invoice': '01',
            'out_refund': '04',
            'in_refund': '05',
            'liq_purchase': '03',
            'ret_in_invoice': '07',
        }
        code = map_type[type_document]
        for a in self.authorisation_ids:
            if a.active and a.type_id.code == code:
                return a
        MSG = 'No ha configurado una autorización para este tipo de documento.'
        act_ex = 'l10n_ec_authorisation.action_account_auth_tree'
        act_in = 'l10n_ec_authorisation.action_account_authin_tree'
        act_to = code in ['18', '04', '03'] and act_in or act_ex
        act = self.env.ref(act_to)
        raise RedirectWarning(MSG, act.id, 'Ir a configurar autorizaciones')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """
        Redefinicion de metodo para obtener:
        numero de autorizacion
        numero de documento
        El campo auth_inv_id representa la autorizacion para
        emitir el documento.
        """
        DOCUMENTOS_EMISION = ['out_invoice', 'liq_purchase', 'out_refund']
        super(AccountInvoice, self)._onchange_partner_id()
        partner = self.type in DOCUMENTOS_EMISION and self.company_id.partner_id or self.partner_id  # noqa
        if not partner:
            return
        self.auth_inv_id = partner.get_authorisation(self.type)
        self.auth_number = self.auth_inv_id.name
        number = '{0}'.format(
            str(self.auth_inv_id.sequence_id.number_next_actual).zfill(9)
        )
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
    auth_inv_id = fields.Many2one(
        'account.authorisation',
        string='Establecimiento',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Autorizacion para documento',
        copy=False
    )
    auth_number = fields.Char('Autorización')
    sustento_id = fields.Many2one(
        'account.ats.sustento',
        string='Sustento del Comprobante'
    )

    @api.onchange('reference')
    def _onchange_ref(self):
        # TODO: agregar validacion numerica a reference
        if self.reference:
            self.reference = self.reference.zfill(9)

    @api.constrains('auth_number')
    def check_reference(self):
        """
        Metodo que verifica la longitud de la autorizacion
        10: documento fisico
        35: factura electronica modo online
        49: factura electronica modo offline
        """
        if self.type not in ['in_invoice', 'liq_purchase']:
            return
        if self.auth_number and len(self.auth_number) not in [10, 35, 49]:
            raise UserError(
                u'Debe ingresar 10, 35 o 49 dígitos según el documento.'
            )

    @api.multi
    def action_number(self):
        # TODO: ver donde incluir el metodo de numeracion
        self.ensure_one()
        if self.type not in ['out_invoice', 'liq_purchase']:
            return
        number = self.internal_inv_number
        if not number:
            sequence = self.journal_id.auth_id.sequence_id
            number = sequence.next_by_id()
        self.write({'reference': number, 'internal_inv_number': number})
