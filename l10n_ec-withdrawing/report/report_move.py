# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

import time
from report import report_sxw
from osv import osv
import pooler

class move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(move, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_analytic_lines': self.get_analytic_lines,
            'get_user': self.get_user,
        })

    def get_analytic_lines(self, obj_id, data):
        print obj_id, data
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
            self.cr.execute("select create_uid from account_move where id=%s" % move.id)
            data = self.cr.fetchone()
            user = user_pool.browse(self.cr, self.uid, data[0])
            user_name = user.name
        return user_name
   
report_sxw.report_sxw('report.account.move','account.move','addons/retention/report/report_move.rml',parser=move)

