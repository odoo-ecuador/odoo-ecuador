import time
from openerp.report import report_sxw
from openerp.osv import osv

class BankStatement(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(BankStatement, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_user': self.get_user,
        })

    def get_user(self, object):
        self.cr.execute("select create_uid from account_bank_statement where id=%s" % object.id)
        data = self.cr.fetchone()
        user = self.pool.get('res.users').browse(self.cr, self.uid, data[0])
        return user.name
        
   
report_sxw.report_sxw('report.bank.statement','account.bank.statement','addons/retention/report/bank_statement.mako',parser=BankStatement)
