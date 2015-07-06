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
import StringIO
import base64

from lxml import etree
from lxml.etree import DocumentInvalid

try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError('Instalar Libreria suds')

from osv import osv
from openerp.addons.l10n_ec_einvoice import utils
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

    @classmethod
    def __init__(self, document, type='out_invoice'):
        """
        document: XML representation
        type: determinate schema
        """
        self.document = document
        self.type_document = type
        self._schema = SCHEMAS[self.type_document]
        self.signed_document = False

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
            print e
            raise osv.except_osv('Error de Datos', MSG_SCHEMA_INVALID)

    @classmethod
    def send_receipt(self, document):
        """
        TODO: documentar
        """
        buf = StringIO.StringIO()
        buf.write(document)
        buffer_xml = base64.encodestring(buf.getvalue())

        if not utils.check_service('prueba'):
            raise osv.except_osv('Error SRI', 'Servicio SRI no disponible.')

        client = Client(SriService.get_active_ws()[0])
        result =  client.service.validarComprobante(buffer_xml)
        if result.estado == 'RECIBIDA':
            return True
        else:
            return False, result

    def request_authorization(self, access_key):
        messages = []
        client = Client(SriService.get_active_ws()[1])
        result =  client.service.autorizacionComprobante(access_key)
        autorizacion = result.autorizaciones[0][0]
        for m in autorizacion.mensajes[0]:
            messages.append([m.identificador, m.mensaje, m.tipo])
                
        if autorizacion.estado == 'AUTORIZADO':
            autorizacion_xml = etree.Element('autorizacion')
            etree.SubElement(autorizacion_xml, 'estado').text = autorizacion.estado
            etree.SubElement(autorizacion_xml, 'numeroAutorizacion').text = autorizacion.numeroAutorizacion
            etree.SubElement(autorizacion_xml, 'ambiente').text = autorizacion.ambiente
            etree.SubElement(autorizacion_xml, 'fechaAutorizacion').text = str(autorizacion.fechaAutorizacion.strftime("%d/%m/%Y %H:%M:%S"))
            etree.SubElement(autorizacion_xml, 'comprobante').text = etree.CDATA(autorizacion.comprobante)
            return autorizacion_xml, messages
        else:
            return False, messages


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

