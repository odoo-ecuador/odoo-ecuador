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

SCHEMAS = {
    'out_invoice': 'schemas/factura.xsd',
    'out_refund': 'schemas/nota_credito.xsd',
    'retention': 'schemas/retention.xsd',
    'delivery': 'schemas/delivery.xsd',
    'in_refund': 'schemas/nota_debito.xsd'
}

class DocumentXML(object):
    _schema = False
    document = False

    def __init__(self, document, type='out_invoice'):
        """
        document: XML representation
        type: determinate schema
        """
        self.document = document
        self.type_document = type
        self._schema = SCHEMAS[self.type_document]

    @classmethod
    def validate_xml(self):
        """
        """
        MSG_SCHEMA_INVALID = u"El sistema generó el XML pero el comprobante electrónico no pasa la validación XSD del SRI."
        file_path = os.path.join(os.path.dirname(__file__), self._schema)
        schema_file = open(file_path)
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        try:
            xmlschema.assertValid(self.document)
        except DocumentInvalid as e:
            raise osv.except_osv('Error de Datos', MSG_SCHEMA_INVALID)


class SriService(object):

    __AMBIENTE_PRUEBA = '1'
    __AMBIENTE_PROD = '2'
    __WS_TEST_RECEIV = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
    __WS_TEST_AUTH = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'
    __WS_RECEIV = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
    __WS_AUTH = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'

    __WS_TESTING = (__WS_TEST_RECEIV, __WS_TEST_AUTH)
    __WS_PROD = (__WS_RECEIV, __WS_AUTH)
    __WS_ACTIVE = __WS_TESTING

    @classmethod
    def get_active_env(self):
        return self.get_env_test()

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
    def get_active_ws(self):
        return self.__WS_ACTIVE

    @classmethod
    def create_access_key(self, values):
        """
        values: tuple ([], [])
        """
        env = self.get_active_env()
        dato = ''.join(values[0] + [env] + values[1])
        modulo = CheckDigit.compute_mod11(dato)
        access_key = ''.join([dato, str(modulo)])
        return access_key
