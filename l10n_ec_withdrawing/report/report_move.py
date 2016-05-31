# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw
from openerp import pooler


class move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(move, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_analytic_lines': self.get_analytic_lines,
            'get_user': self.get_user,
        })

    def get_analytic_lines(self, obj_id, data):
        move = self.pool.get('account.move').browse(self.cr, self.uid, obj_id)
        lines = []
        for line in move.line_id:
            for al in line.analytic_lines:
                if al.amount == 0:
                    continue
                line_data = {'acc_name': al.account_id.complete_name,
                             'code': al.account_id.code,
                             'amount': abs(al.amount),
                             'name': al.name}
                lines.append(line_data)
        return lines

    def get_user(self, move):
        user_name = '*'
        user_pool = pooler.get_pool(self.cr.dbname).get('res.users')
        if move.line_id and move.line_id[0] and move.line_id[0].invoice:
            user_name = move.line_id[0].invoice.user_id.name
        else:
            self.cr.execute("select create_uid from account_move where id=%s" % move.id)  # noqa
            data = self.cr.fetchone()
            user = user_pool.browse(self.cr, self.uid, data[0])
            user_name = user.name
        return user_name

report_sxw.report_sxw('report.account.move',
                      'account.move',
                      'addons/retention/report/report_move.rml',
                      parser=move)
