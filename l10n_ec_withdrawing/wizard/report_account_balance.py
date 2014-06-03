from osv import osv, fields

class AccountBalanceReport(osv.osv_memory):

    _inherit = 'account.balance.report'

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance1', 'datas': data}


AccountBalanceReport()
