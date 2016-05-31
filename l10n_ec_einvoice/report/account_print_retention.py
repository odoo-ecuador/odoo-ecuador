# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw


class account_retention(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_retention, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw(
    'report.account.eretention',
    'account.retention',
    'addons/l10n_ec_withdrawing/report/account_print_retention.rml',
    parser=account_retention
)
