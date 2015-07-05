# -*- coding: utf-8 -*-
##############################################################################
#
#    XADES 
#    Copyright (C) 2014 Cristian Salamea All Rights Reserved
#    cristian.salamea@gmail.com
#    $Id$
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

import logging
import os
from osv import osv

from lxml import etree
from lxml.etree import DocumentInvalid

try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError('Instalar Libreria suds')

from .xades import CheckDigit

class InvoiceXML(object):

    INVOICE_XSD_PATH = 'schemas/factura_v1.1.0.xsd'
    REFUND_XSD_PATH = 'schemas/notaCredito_v1.1.0.xsd'
    INVOICE_SCHEMA_INVALID = u"""El sistema generó el XML pero el comprobante electrónico no pasa la validación XSD del SRI. \n\n %s"""

    @classmethod
    def __init__(self, element):
        self.invoice_element = element

    @classmethod
    def save(self, access_key):
        OPT_PATH = '/opt/facturas/'
        name = '%s%s.xml' % (OPT_PATH, access_key)
        tree = etree.ElementTree(self.invoice_element)
        tree.write(name, pretty_print=True, xml_declaration=True, encoding='utf-8', method='xml')
    
    @classmethod
    def validate_xml(self, tipo_comprobante):
        """
        """
        if tipo_comprobante == 'out_invoice':
            file_path = os.path.join(os.path.dirname(__file__), self.INVOICE_XSD_PATH)
        else:
            file_path = os.path.join(os.path.dirname(__file__), self.REFUND_XSD_PATH)
        schema_file = open(file_path)
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        try:
            xmlschema.assertValid(self.invoice_element)
        except DocumentInvalid as e:
            raise osv.except_osv('Error de Datos',  self.INVOICE_SCHEMA_INVALID % str(e))

class Service(object):

    __AMBIENTE_PRUEBA = '1'
    __AMBIENTE_PROD = '2'
    __WS_TEST_RECEIV = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
    __WS_TEST_AUTH = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'
    __WS_RECEIV = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
    __WS_AUTH = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'

    @classmethod
    def get_env_test(self):
        return self.__AMBIENTE_PRUEBA

    @classmethod
    def get_env_prod(self):
        return self.__AMBIENTE_PROD

    @classmethod
    def get_ws_test(self):
        return self.__WS_TEST_RECEIV, self.__WS_TEST_AUTH
    
    @classmethod
    def get_ws_prod(self):
        return self.__WS_RECEIV, self.__WS_AUTH

    @classmethod
    def create_access_key(self, values):
        """
        values: tuple ([], [])
        """
        env = self.get_env_prod()
        dato = ''.join(values[0] + [env] + values[1])
        modulo = CheckDigit.compute_mod11(dato)
        access_key = ''.join([dato, str(modulo)])
        return access_key
