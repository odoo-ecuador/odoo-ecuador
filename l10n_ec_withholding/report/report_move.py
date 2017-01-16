# -*- coding: utf-8 -*-

from itertools import groupby

from odoo import api, models


class ReporteComprobante(models.AbstractModel):

    _name = 'report.l10n_ec_withholding.reporte_move'

    def groupby(self, lines):
        """
        Agrupa lineas por cuenta contable
        """
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

    @api.model
    def render_html(self, docids, data=None):
        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': self.env['account.move'].browse(docids),
            'groupby': self.groupby
        }
        return self.env['report'].render('l10n_ec_withholding.reporte_move', values=docargs)  # noqa
