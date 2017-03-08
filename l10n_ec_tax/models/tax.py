# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
import datetime
import calendar

from odoo import api, fields, models
from odoo import tools


class AccountInvoiceTax(models.Model):

    _inherit = 'account.invoice.tax'

    fiscal_year = fields.Char(
        'Ejercicio Fiscal',
        size=4,
        default=time.strftime('%Y')
    )
    group_id = fields.Many2one(
        related='tax_id.tax_group_id',
        store=True,
        string='Grupo'
    )
    base = fields.Monetary(store=True)
    code = fields.Char(
        related='tax_id.description',
        string='Código',
        store=True
    )
    percent_report = fields.Char(related='tax_id.percent_report')
    retention_id = fields.Many2one(
        'account.retention',
        'Retención',
        index=True
    )


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    """
            ('vat', 'IVA Diferente de 0%'),
            ('vat0', 'IVA 0%'),
            ('novat', 'No objeto de IVA'),
            ('ret_vat_b', 'Retención de IVA (Bienes)'),
            ('ret_vat_srv', 'Retención de IVA (Servicios)'),
            ('ret_ir', 'Ret. Imp. Renta'),
            ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'),
            ('imp_ad', 'Imps. Aduanas'),
            ('imp_sbs', 'Super de Bancos'),
            ('ice', 'ICE'),
            ('other', 'Other')
    """

    code = fields.Char('Código')


class AccountTax(models.Model):

    _inherit = 'account.tax'

    percent_report = fields.Char('% para Reportes')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def compute_compensaciones(self):
        res = []
        for line in self.tax_line_ids:
            if line.group_id.code == 'comp':
                res.append({
                    'codigo': line.tax_id.description,
                    'tarifa': line.tax_id.percent_report,
                    'valor': abs(line.amount)
                })
        return res or False


class AccountReportTax(models.TransientModel):
    _name = 'account.report.tax'

    @api.model
    def _default_start(self):
        today = datetime.date.today()
        today = today.replace(day=1)
        res = fields.Date.to_string(today)
        return res

    @api.model
    def _default_end(self):
        today = datetime.date.today()
        first, last = calendar.monthrange(today.year, today.month)
        today = today.replace(day=last)
        res = fields.Date.to_string(today)
        return res

    date_start = fields.Date('Inicio Periodo', default=_default_start)
    date_end = fields.Date('Final de Periodo', default=_default_end)

    @api.multi
    def action_print(self):
        return self.env['report'].get_action(
            self,
            'l10n_ec_tax.reporte_account_tax_ec'
        )


class ReportVatPartner(models.Model):
    _name = 'report.vat.partner'
    _auto = False

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(
            self._cr,
            'report_vat_partner'
        )
        sql = """
        CREATE OR REPLACE VIEW report_vat_partner as (
        SELECT min(ait.id) as id, ai.date as date,
        ai.partner_id as partner_id, ai.type as type, ait.code as code,
        ait.name as name, ait.group_id as tax_group, SUM(ait.base) as base,
        ABS(SUM(amount)) AS total
        FROM account_invoice_tax ait
        INNER JOIN  account_invoice ai ON ait.invoice_id = ai.id
        WHERE ai.state IN ('open', 'paid')
        AND ai.type in ('in_invoice', 'out_invoice',
        'out_refund', 'in_refund', 'liq_purchase')
        GROUP BY ait.group_id, ait.name, ai.type,
        ai.partner_id, ai.date, ait.code, ait.base
        ORDER BY type
        )
        """
        self._cr.execute(sql)

    id = fields.Integer('ID')
    date = fields.Date('Fecha Contable')
    partner_id = fields.Many2one('res.partner', 'Empresa')
    type = fields.Selection(
        [
            ('out_invoice', 'Venta'),
            ('in_invoice', 'Compra'),
            ('out_refund', 'NC Cliente'),
            ('in_refund', 'NC Prov.'),
            ('liq_purchase', 'Liq. de Compra')
        ], 'Tipo'
    )
    code = fields.Char('Codigo')
    tax_group = fields.Many2one('account.tax.group', 'Grupo')
    name = fields.Char('Impuesto')
    base = fields.Float('Base')
    total = fields.Float('Imp. Aplicado')
