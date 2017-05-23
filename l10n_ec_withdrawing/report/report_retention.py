# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Gnuthink (<http://gnuthink.com>).
#
#    Author :  Cristian Salamea cristian.salamea@gnuthink.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#
##############################################################################

from datetime import datetime
from openerp.report import report_sxw

class report_retention(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_retention, self).__init__(cr, uid, name, context)
        self.localcontext.update({
      
        })   
report_sxw.report_sxw('report.retention.pdf','account.retention','retention/report/report_retention.rml',parser=report_retention, header=False)
                  


    
