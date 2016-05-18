# -*- coding: utf-8 -*-


from openerp.report import report_sxw


class report_invoice(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_invoice, self).__init__(cr, uid, name, context)
        self.localcontext.update({

                })

report_sxw.report_sxw(
    'report.invoice.pdf',
    'account.invoice',
    'retention/report/report_invoice.rml',
    parser=report_invoice,
    header=False)
