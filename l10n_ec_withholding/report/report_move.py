# -*- coding: utf-8 -*-

from itertools import groupby

from openerp.report import report_sxw
from openerp.osv import osv


class ReporteComprobante(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(ReporteComprobante, self).__init__(
            cr, uid, name, context=context
        )
        self.localcontext.update({
            'groupby': self.groupby
        })

    def groupby(self, lines):
        glines = []
        for k, g in groupby(lines, key=lambda r: r.account_id):
            debit = 0
            credit = 0
            for i in g:
                debit += i.debit
                credit += i.credit
            glines.append({
                'code': k.code,
                'name': k.name,
                'debit': debit,
                'credit': credit
            })
        return glines


class ReporteMove(osv.AbstractModel):

    _name = "report.l10n_ec_withholding.account_move_report"
    _inherit = "report.abstract_report"
    _template = "l10n_ec_withholding.account_move_report"
    _wrapped_report_class = ReporteComprobante
