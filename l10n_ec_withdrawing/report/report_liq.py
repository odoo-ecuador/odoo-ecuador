# -*- coding: utf-8 -*-
##############################################################################
#
#    Author :  Cristian Salamea cristian.salamea@gnuthink.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from openerp.report import report_sxw

class report_liq(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_liq, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                })
        
report_sxw.report_sxw('report.liq.pdf', 'account.invoice', 'retention/report/report_liq.rml', parser=report_liq, header=False)


    
