# -*- coding: utf-8 -*-
# © 2015 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
import logging

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_l = logging.getLogger(__name__)


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    lunch_from = fields.Float('Salida Almuerzo')
    lunch_to = fields.Float('Entrada Almuerzo')
    lunch_max = fields.Integer('Límite para Almuerzo (h)')
    tolerance_in = fields.Integer('Tolerancia de Retraso en ingreso')
    exception_ids = fields.One2many(
        'hr.calendar.exception',
        'calendar_id',
        string='Excepciones'
    )


class HrCalendarException(models.Model):
    _name = 'hr.calendar.exception'
    _order = 'date ASC'

    name = fields.Char('Motivo', size=64, required=True)
    date = fields.Date('Fecha que aplica', required=True)
    hour_from = fields.Float('Trabajar desde')
    hour_to = fields.Float('Trabajar hasta')
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('confirm', 'Confirmado')
        ],
        required=True,
        string='Estado',
        readonly=True
    )
    calendar_id = fields.Many2one('resource.calendar', 'Calendario')

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})
        return True


class HrContract(models.Model):

    _name = 'hr.contract'
    _inherit = ['hr.contract', 'mail.thread', 'ir.needaction_mixin']

    @api.multi
    def name_get(self):
        res = []
        for obj in self:
            res.append((obj.id, '%s - %s' % (obj.name, obj.employee_id.name)))
        return res

    @api.multi
    @api.depends('employee_id', 'state')
    def _compute_department(self):
        # TODO: revisar, debemos asegurar el departmento por contrato
        states = ['pending_done', 'done']
        for contract in self:
            if contract.department_id and contract.state in states:
                contract.department_id = contract.department_id.id
            elif contract.employee_id.department_id:
                contract.department_id = contract.employee_id.department_id.id

    @api.multi
    @api.depends('date_start', 'date_end')
    def _compute_days(self):
        for obj in self:
            ds = datetime.strptime(obj.date_start, DEFAULT_SERVER_DATE_FORMAT).date()  # noqa
            de = datetime.now().date()
            if obj.date_end:
                de = datetime.strptime(obj.date_end, DEFAULT_SERVER_DATE_FORMAT).date()  # noqa
            days = de - ds
            self.age_days = days.days

    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('trial', 'Pruebas'),
            ('trial_ending', 'Terminando Pruebas'),
            ('open', 'Abierto'),
            ('contract_ending', 'Finalizando'),
            ('pending_done', 'Pendiente de Cierre'),
            ('done', 'Completado')
        ],
        'State',
        readonly=True,
    )
    # store this field in the database and trigger a change only if the
    # contract is in the right state: we don't want future changes to an
    # employee's department to impact past contracts that have now ended.
    # Increased priority to override hr_simplify.
    department_id = fields.Many2one(
        'hr.department',
        compute='_compute_department',
        string="Department",
        readonly=True
    )
    # At contract end this field will hold the job_id, and the
    # job_id field will be set to null so that modules that
    # reference job_id don't include deactivated employees.
    end_job_id = fields.Many2one(
        'hr.job',
        'Job Title',
        readonly=True,
    )
    # The following are redefined again to make them editable only in
    # certain states
    employee_id = fields.Many2one(
        'hr.employee',
        "Employee",
        required=True,
        readonly=True,
        states={
            'draft': [('readonly', False)]
        },
    )
    type_id = fields.Many2one(
        'hr.contract.type',
        "Contract Type",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_start = fields.Date(
        'Start Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    wage = fields.Float(
        'Wage',
        digits=(16, 2),
        required=True,
        readonly=False,
        help="Basic Salary of the employee",
    )
    p_hipotecario = fields.Float(
        'Prestamo Hipotecario',
        digits=(16, 2),
        required=True,
        readonly=False,
        help="Valor Prestamo Hipotecario IESS",
    )
    p_quirografario = fields.Float(
        'Prestamo Quirografario',
        digits=(16, 2),
        required=True,
        readonly=False,
        help="Valor Prestamo Quirografario IESS",
    )
    anticipo_sueldo = fields.Float(
        'Anticipo Sueldo',
        digits=(16, 2),
        required=True,
        readonly=False,
        help="Valor Prestamo Anticipo de sueldo en la empresa",
    )
    otros_descuentos = fields.Float(
        'Otros Descuentos',
        digits=(16, 2),
        required=True,
        readonly=False,
    )
    base_trial_days = fields.Integer('Base dias para pruebas')
    wage_base_legal = fields.Float(
        'Salario Básico Unificado',
        required=True,
        readonly=False,
    )
    age_days = fields.Integer(
        compute='_compute_days',
        string='Días de Contrato',
        readonly=True
    )
    code_contract_id = fields.Many2one(
        'hr.contract.code',
        'Código Sectorial'
    )
    bonus_ids = fields.One2many(
        'hr.contract.bonus',
        'contract_id',
        'name'
    )

    _track = {
        'state': {
            'hr_contract_state.mt_alert_trial_ending': (
                lambda s, cr, u, o, c=None: o['state'] == 'trial_ending'),
            'hr_contract_state.mt_alert_open': (
                lambda s, cr, u, o, c=None: o['state'] == 'open'),
            'hr_contract_state.mt_alert_contract_ending': (
                lambda s, cr, u, o, c=None: o['state'] == 'contract_ending'),
        },
    }

    @api.model
    def _needaction_domain_get(self):

        users_obj = self.env['res.users']
        domain = []

        if users_obj.has_group('base.group_hr_manager'):
            domain = [
                ('state', 'in', ['draft', 'contract_ending', 'trial_ending'])]
            return domain

        return False

    @api.onchange('trial_date_start')
    def _onchange_trial_days(self):
        if not self.trial_date_start:
            return {}
        years, month, days = self.trial_date_start.split('-')
        d = datetime(year=int(years),
                     month=int(month),
                     day=int(days)) + relativedelta(days=self.base_trial_days)
        trial_end = d.strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.trial_date_end = trial_end

#    @api.onchange('job_id')
#    def onchange_job(self):
#        _l.debug('hr_contract_state: onchange_job()')
#        res = False
#        if self.state != 'draft':
#            self.job_id = res
#        return super(hr_contract, self).onchange_job()

    @api.multi
    def signal_confirm(self):
        """
        TODO: revisar condicionamiento de
        periodo de prueba
        """
        self.condition_trial_period()
        self.state_trial()
        self.update_job()
        self.update_holidays()

    @api.multi
    def condition_trial_period(self):
        for contract in self:
            if not contract.trial_date_start:
                return False
        return True

    @api.multi
    def signal_ending_contract(self):
        self.write({'state': 'contract_ending'})
        return True

    @api.multi
    def try_signal_ending_contract(self):
        d = datetime.now().date() + relativedelta(days=+30)
        ids = self.search([
            ('state', '=', 'open'),
            ('date_end', '<=', d.strftime(
                DEFAULT_SERVER_DATE_FORMAT))
        ])
        if len(ids) == 0:
            return
        self.signal_ending_contract()

    @api.multi
    def try_signal_contract_completed(self):
        d = datetime.now().date()
        ids = self.search([
            ('state', '=', 'open'),
            ('date_end', '<', d.strftime(
                DEFAULT_SERVER_DATE_FORMAT))
        ])
        if len(ids) == 0:
            return

        self.state_pending_done()

    @api.multi
    def signal_ending_trial(self):
        self.write({'state': 'trial_ending'})
        return True

    @api.multi
    def try_signal_ending_trial(self):
        d = datetime.now().date() + relativedelta(days=+10)
        ids = self.search([
            ('state', '=', 'trial'),
            ('trial_date_end', '<=', d.strftime(
                DEFAULT_SERVER_DATE_FORMAT))
        ])
        if len(ids) == 0:
            return

        self.signal_ending_trial()

    @api.multi
    def try_signal_open(self):

        d = datetime.now().date() + relativedelta(days=-5)
        ids = self.search([
            ('state', '=', 'trial_ending'),
            ('trial_date_end', '<=', d.strftime(
                DEFAULT_SERVER_DATE_FORMAT))
        ])
        if len(ids) == 0:
            return

        self.state_open()

    @api.onchange('date_start')
    def onchange_start(self):
        self.trial_date_start = self.date_start

    @api.multi
    def update_holidays(self):
        holidays = self.env['hr.holidays']
        for obj in self:
            res = holidays.search(
                [
                    ('employee_id', '=', obj.employee_id.id),
                    ('state', '=', 'confirm')
                ])
            if not res:
                return True
            holidays.holidays_validate()
        return True

    @api.multi
    def update_job(self):
        # metodo que actualiza el trabajo a ocupado
        for obj in self:
            hired = obj.job_id.no_of_hired_employee + 1
            obj.job_id.write(
                {
                    'state': 'open', 'no_of_hired_employee': hired
                })
            obj.employee_id.write(
                {
                    'department_id': obj.job_id.department_id.id,
                    'job_id': obj.job_id.id
                })
        return True

    @api.multi
    def state_trial(self):
        self.write({'state': 'trial'})
        return True

    @api.multi
    def state_open(self):
        self.write({'state': 'open'})
        return True

    @api.multi
    def state_pending_done(self):
        self.write({'state': 'pending_done'})
        return True

    @api.multi
    def state_done(self):
        for obj in self:
            vals = {
                'state': 'done',
                'date_end': False,
                'job_id': False,
                'end_job_id': obj.job_id.id
            }

            vals['date_end'] = obj.date_end or time.strftime(DEFAULT_SERVER_DATE_FORMAT)  # noqa
            obj.write(vals)
        return True


class HrContractBonus(models.Model):
    _name = 'hr.contract.bonus'

    contract_id = fields.Many2one('hr.contract', 'Contracto')
    name = fields.Char('Tipo Ingreso', size=64, required=True)
    amount = fields.Float(
        'Valor Bono',
        digits=(16, 2)
    )
