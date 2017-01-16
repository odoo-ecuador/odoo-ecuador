# -*- coding: utf-8 -*-

import os
from StringIO import StringIO
import base64
import logging

from lxml import etree
from lxml.etree import fromstring, DocumentInvalid

try:
    from suds.client import Client
except ImportError:
    logging.getLogger('xades.sri').info('Instalar libreria suds-jurko')

from ..models import utils
from .xades import CheckDigit

SCHEMAS = {
    'out_invoice': 'schemas/factura.xsd',
    'out_refund': 'schemas/nota_credito.xsd',
    'withdrawing': 'schemas/retencion.xsd',
    'delivery': 'schemas/guia_remision.xsd',
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
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        self.document = fromstring(document.encode('utf-8'), parser=parser)
        self.type_document = type
        self._schema = SCHEMAS[self.type_document]
        self.signed_document = False
        self.logger = logging.getLogger('xades.sri')

    @classmethod
    def validate_xml(self):
        """
        Validar esquema XML
        """
        self.logger.info('Validacion de esquema')
        self.logger.debug(etree.tostring(self.document, pretty_print=True))
        file_path = os.path.join(os.path.dirname(__file__), self._schema)
        schema_file = open(file_path)
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        try:
            xmlschema.assertValid(self.document)
            return True
        except DocumentInvalid:
            return False

    @classmethod
    def send_receipt(self, document):
        """
        Metodo que envia el XML al WS
        """
        self.logger.info('Enviando documento para recepcion SRI')
        buf = StringIO()
        buf.write(document)
        buffer_xml = base64.encodestring(buf.getvalue())

        if not utils.check_service('prueba'):
            # TODO: implementar modo offline
            raise 'Error SRI', 'Servicio SRI no disponible.'

        client = Client(SriService.get_active_ws()[0])
        result = client.service.validarComprobante(buffer_xml)
        self.logger.info('Estado de respuesta documento: %s' % result.estado)
        errores = []
        if result.estado == 'RECIBIDA':
            return True, errores
        else:
            for comp in result.comprobantes:
                for m in comp[1][0].mensajes:
                    rs = [m[1][0].tipo, m[1][0].mensaje]
                    rs.append(getattr(m[1][0], 'informacionAdicional', ''))
                    errores.append(' '.join(rs))
            self.logger.error(errores)
            return False, ', '.join(errores)

    def request_authorization(self, access_key):
        messages = []
        client = Client(SriService.get_active_ws()[1])
        result = client.service.autorizacionComprobante(access_key)
        self.logger.debug("Respuesta de autorizacionComprobante:SRI")
        self.logger.debug(result)
        autorizacion = result.autorizaciones[0][0]
        mensajes = autorizacion.mensajes and autorizacion.mensajes[0] or []
        self.logger.info('Estado de autorizacion %s' % autorizacion.estado)
        for m in mensajes:
            self.logger.error('{0} {1} {2}'.format(
                m.identificador, m.mensaje, m.tipo, m.informacionAdicional)
            )
            messages.append([m.identificador, m.mensaje,
                             m.tipo, m.informacionAdicional])
        if not autorizacion.estado == 'AUTORIZADO':
            return False, messages
        return autorizacion, messages


class SriService(object):

    __AMBIENTE_PRUEBA = '1'
    __AMBIENTE_PROD = '2'
    __ACTIVE_ENV = False
    # revisar el utils
    __WS_TEST_RECEIV = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'  # noqa
    __WS_TEST_AUTH = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'  # noqa
    __WS_RECEIV = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'  # noqa
    __WS_AUTH = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'  # noqa

    __WS_TESTING = (__WS_TEST_RECEIV, __WS_TEST_AUTH)
    __WS_PROD = (__WS_RECEIV, __WS_AUTH)

    _WSDL = {
        __AMBIENTE_PRUEBA: __WS_TESTING,
        __AMBIENTE_PROD: __WS_PROD
    }
    __WS_ACTIVE = __WS_TESTING

    @classmethod
    def set_active_env(self, env_service):
        if env_service == self.__AMBIENTE_PRUEBA:
            self.__ACTIVE_ENV = self.__AMBIENTE_PRUEBA
        else:
            self.__ACTIVE_ENV = self.__AMBIENTE_PROD
        self.__WS_ACTIVE = self._WSDL[self.__ACTIVE_ENV]

    @classmethod
    def get_active_env(self):
        return self.__ACTIVE_ENV

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
