# -*- coding: utf-8 -*-

from report import report_sxw


class report_liq(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_liq, self).__init__(cr, uid, name, context)
        self.localcontext.update({})

report_sxw.report_sxw('report.liq.pdf',
                      'account.invoice',
                      'retention/report/report_liq.rml',
                      parser=report_liq, header=False)
