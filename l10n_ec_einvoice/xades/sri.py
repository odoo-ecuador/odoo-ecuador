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

from lxml import etree
from lxml.etree import DocumentInvalid


class InvoiceXML(object):

    self.INVOICE_XSD_PATH = 'schemas/factura.xsd'
    self.INVOICE_SCHEMA_INVALID = """El sistema generó el XML pero la factura no pasa la validación XSD del SRI.
            \nLos errores mas comunes son:\n* RUC,Cédula o Pasaporte contiene caracteres no válidos.\n* Números de documentos están duplicados.\n\nEl siguiente error contiene el identificador o número de documento en conflicto:\n\n %s"""

    def __init__(self, element):
        self.invoice_element = element

    def to_string(self):
        inv_str = etree.tostring(factura, pretty_print=True, encoding='utf-8')
        return inv_str
    
    def validate_xml(self):
        """
        """
        file_path = os.path.join(os.path.dirname(__file__), self.INVOICE_XSD_PATH)
        schema_file = open(file_path)
        file_factura = etree.tostring(self.invoice_element, pretty_print=True, encoding='utf-8')
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        try:
            xmlschema.assertValid(factura)
        except DocumentInvalid as e:
            raise osv.except_osv('Error de Datos',  self.INVOICE_SCHEMA_INVALID % str(e))    


class Service(object):

    def __init__(self):
        self.__AMBIENTE_PRUEBA = '1'
        self.__AMBIENTE_PROD = '2'
        self.__WS_TEST_RECEIV = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
        self.__WS_TEST_AUTH = 'https://celcer.sri.gob.ec/comprobantes-electronicos- ws/AutorizacionComprobantes?wsdl'
        self.__WS_RECEIV = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
        self.__WS_AUTH = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'

    def get_env_test(self):
        return self.__AMBIENTE_PRUEBA

    def get_env_prod(self):
        return self.__AMBIENTE_PROD

    def get_ws_test(self):
        return self.__WS_TEST_RECEIV, self.__WS_TEST_AUTH

    def get_ws_prod(self):
        return self.__WS_RECEIV, self.__WS_AUTH

    def create_access_key(self, values):
        """
        values: tuple ([], [])
        """
        check_digit = CheckDigit()
        tipo_emision = self.get_emission()
        dato = values[0] + [tipo_emision] + values[1]
        modulo = check_digit.compute_mod11(dato)
        access_key = ''.join([dato, modulo])
        return access_key    

    def get_emission(self):
        """
        Metodo de tipo de emision
        FIX FIX FIX TODO: mejorar documentacion
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

