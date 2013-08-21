##############################################################################
#
# Copyright (c) 2008-2010 SIA "KN dati". (http://kndati.lv) All Rights Reserved.
#                    General contacts <info@kndati.lv>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from report import report_sxw
from report.report_sxw import rml_parse
import random
from tools import ustr
from osv import osv

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_auth':self.get_auth,
                'get_invoice_number':self.get_invoice_number,
                'get_moves':self.get_moves,
                })
        self.no = 0
        self.aux=0

    def get_auth(self, line):
        aux = ''
        if line.invoice:
            aux = line.invoice.auth_inv_id.name
        return aux
    
    def get_invoice_number(self, line, ref):
        aux=''
        if line.invoice:
            ceros = ref.zfill(9)
            aux=line.invoice.auth_inv_id.serie_entidad+'-'+line.invoice.auth_inv_id.serie_entidad+'-'+ceros
        return aux

    def get_moves(self, lines):
        aux = []
        for line in lines:
            if line.debit>0 or line.credit>0:
                aux.append(line)
        return aux
    

