# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from operator import itemgetter

from odoo import api, models, fields


class ReportAccountReportTax(models.AbstractModel):
    _name = 'report.l10n_ec_tax.reporte_account_tax_ec'

    def period(self, wiz):
        ds = fields.Date.from_string(wiz.date_start)
        period = '{0:02d}-{1}'.format(ds.month, ds.year)
        return period

    def get_taxes(self, wizard):
        taxes = []
        ret_ir = []  # ret_ir
        ret_vat = []  # ret_vat_*
        nc = []
        vat = []
        sales = []
        sale_vat = []
        sql = """
        SELECT ai.type, ait.code, ait.name, atg.code as gcode,
        SUM(ait.base) as base,
        ABS(SUM(amount)) AS total
        FROM account_invoice_tax ait
        INNER JOIN  account_invoice ai ON ait.invoice_id = ai.id
        INNER JOIN account_tax_group atg ON ait.group_id = atg.id
        WHERE ai.date BETWEEN '%s' and '%s' AND ai.state IN ('open', 'paid')
        AND ai.type in ('in_invoice', 'out_invoice',
        'out_refund', 'in_refund','liq_purchase')
        GROUP BY atg.code, ait.name, ai.type, ait.code
        ORDER BY code, type;
        """ % (wizard.date_start, wizard.date_end)
        self._cr.execute(sql)
        res = self._cr.fetchall()
        for row in res:
            row = list(row)
            if row[0] == 'out_invoice':
                if row[3] in ['vat', 'novat', 'vat0']:
                    sale_vat.append(row)
                else:
                    sales.append(row)
            elif row[0] in ['in_refund', 'out_refund']:
                nc.append(row)
            elif row[3] in ['ret_ir', 'no_ret_ir']:
                ret_ir.append(row)
            elif row[3] in ['ret_vat_b', 'ret_vat_srv']:
                ret_vat.append(row)
            elif row[3] in ['vat', 'novat', 'vat0']:
                vat.append(row)

        taxes.append({
            'title': 'IMPUESTO AL VALOR AGREGADO VENTAS',
            'lines': sorted(sale_vat, key=itemgetter(0)),
            'total_base': sum([v[4] for v in sale_vat if v[4] > 0]),
            'total_tax': sum([v[5] for v in sale_vat if v[5] > 0])
        })
        taxes.append({
            'title': 'IMPUESTO AL VALOR AGREGADO',
            'lines': sorted(vat, key=itemgetter(0)),
            'total_base': sum([v[4] for v in vat if v[4] > 0]),
            'total_tax': sum([v[5] for v in vat if v[5] > 0])
        })
        taxes.append({
            'title': 'NOTAS DE CREDITO Y DEBITO',
            'lines': sorted(nc, key=itemgetter(0)),
            'total_base': sum([v[4] for v in nc if v[4] > 0]),
            'total_tax': sum([v[5] for v in nc if v[5] > 0])
        })
        taxes.append({
            'title': 'RETENCION EN LA FUENTE DE IVA',
            'lines': sorted(ret_vat, key=itemgetter(0)),
            'total_base': sum([v[4] for v in ret_vat if v[4] > 0]),
            'total_tax': sum([v[5] for v in ret_vat if v[5] > 0])
        })
        taxes.append({
            'title': 'RETENCION EN LA FUENTE DEL IMPUESTO A LA RENTA',
            'lines': sorted(ret_ir, key=itemgetter(0)),
            'total_base': sum([v[4] for v in ret_ir if v[4] > 0]),
            'total_tax': sum([v[5] for v in ret_ir if v[5] > 0])
        })
        taxes.append({
            'title': 'RETENCIONES APLICADAS A LA EMPRESA',
            'lines': sorted(sales, key=itemgetter(0)),
            'total_base': sum([v[4] for v in sales if v[4] > 0]),
            'total_tax': sum([v[4] for v in sales if v[5] > 0])
        })
        return taxes

    @api.model
    def render_html(self, docids, data=None):
        docsargs = {
            'doc_ids': docids,
            'doc_model': 'account.report.tax',
            'docs': self.env['account.report.tax'].browse(docids),
            'period': self.period,
            'get_taxes': self.get_taxes
        }
        return self.env['report'].render(
            'l10n_ec_tax.reporte_account_tax_ec',
            values=docsargs
        )
