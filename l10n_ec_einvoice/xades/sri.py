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

try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError('Instalar Libreria suds')

from .xades import CheckDigit


class InvoiceXML(object):

    INVOICE_XSD_PATH = 'schemas/factura.xsd'
    INVOICE_SCHEMA_INVALID = """El sistema generó el XML pero la factura no pasa la validación XSD del SRI.
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

    __AMBIENTE_PRUEBA = '1'
    __AMBIENTE_PROD = '2'
    __WS_TEST_RECEIV = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
    __WS_TEST_AUTH = 'https://celcer.sri.gob.ec/comprobantes-electronicos- ws/AutorizacionComprobantes?wsdl'
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
        env = self.get_env_test()
        tipo_emision = self.get_emission()
        dato = ''.join(values[0] + [env] + values[1] + [tipo_emision])
        modulo = CheckDigit.compute_mod11(dato)
        access_key = ''.join([dato, str(modulo)])
        return access_key, tipo_emision

    @classmethod    
    def get_emission(self):
        """
        Metodo de tipo de emision
        FIX FIX FIX TODO: mejorar documentacion
        """
        logger = logging.getLogger('suds.client')
        logger.setLevel(logging.DEBUG)
        NORMAL = '1'
        INDISPONIBILIDAD = '2'
        
        try:
            logger.info("Llamando servicio: %s" % self.get_ws_test()[0])
            client = Client(self.get_ws_test()[0])
        except TransportError, e:
            logger.warning("Servicio no disponible")
            return INDISPONIBILIDAD
        else:
            print client
            return NORMAL    

