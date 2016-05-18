# -*- coding: utf-8 -*-

from openerp.report import report_sxw


class report_retention(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_retention, self).__init__(cr, uid, name, context)
        self.localcontext.update({

        })
report_sxw.report_sxw('report.retention.pdf',
                      'account.retention',
                      'retention/report/report_retention.rml',
                      parser=report_retention,
                      header=False)
