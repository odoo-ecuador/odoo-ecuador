# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Cristian Salamea.
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
import logging

from lxml import etree
from suds.client import Client

from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import openerp.addons.decimal_precision as dp

#Move as field in company ?
TEST_RECEIV_DOCS = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
TEST_AUTH_DOCS = 'https://celcer.sri.gob.ec/comprobantes-electronicos- ws/AutorizacionComprobantes?wsdl'


class AccountInvoice(osv.osv):
    _inherit = 'account.invoice'

    MODULO_11 = 11
    AMBIENTE_PRUEBA = '1'
    AMBIENTE_PROD = '2'

    def get_mod(self, data, mod=11):
        """
        Compute mod 11
        CHECK: must be here ?
        """
        factor = [2,3,4,5,6,7]
        dreverse = data[::-1]
        i = 0
        suma = 0
        for d in dreverse:
            suma += int(d) * factor[i]
            if i == 5:
                i = 0
            else:
                i += 1
        modulo = mod - (suma % mod)
        return modulo

    def get_code(self, cr, uid, invoice):
        """
        TODO: implement!
        1 rule: length string 8
        """
        return '12345678'

    def get_tipo_emision(self, cr, uid, invoice):
        """
        TODO: realizar verificacion de servicio SRI
        Emisión Normal: 1
        Emisión por Indisponibilidad del Sistema: 2        
        """
        logger = logging.getLogger('suds.client').setLevel(logging.INFO)
        
        NORMAL = '1'
        INDISPONIBILIDAD = '2'
        
        try:
            client = Client(TEST_RECEIV_DOCS)
        except TransportError, e:
            return INDISPONIBILIDAD
        else:
            print client
            return NORMAL        

    def get_access_key(self, cr, uid, invoice):
        """
        """
        auth = invoice.journal_id.auth_id
        ld = invoice.date_invoice.split('-')
        ld.reverse()
        fecha = ''.join(ld)
        # 
        tcomp = auth.type_id.code
        ruc = self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.ced_ruc
        serie = '{0}{1}'.format(auth.serie_entidad,auth.serie_emision)
        numero = invoice.supplier_invoice_number # FIX w/ number
        codigo_numero = self.get_code(cr, uid, invoice)
        tipo_emision = self.get_tipo_emision(cr, uid, invoice)
        #
        ak_temp = ''.join([fecha, tcomp, ruc, self.AMBIENTE_PRUEBA,
                           serie, numero, codigo_numero, tipo_emision])
        access_key = ''.join([ak_temp, str(self.get_mod(ak_temp, self.MODULO_11))])
        return access_key

    def action_generate_einvoice(self, cr, uid, ids, context=None):
        """
        Generacion de Xml para factura electronica
        """
        for obj in self.browse(cr, uid, ids, context):
            access_key = self.get_access_key(cr, uid, obj)
            print len(access_key)
            print access_key
