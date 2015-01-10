# -*- coding: utf-8 -*-
##############################################################################
#
#    E-Invoice Module - Ecuador
#    Copyright (C) 2014 VIRTUALSAMI CIA. LTDA. All Rights Reserved
#    alcides@virtualsami.com.ec
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

import os
import base64
import StringIO
import hashlib
import datetime
import subprocess
try:
    from OpenSSL import crypto
except ImportError:
    raise ImportError('Instalar la libreria para soporte OpenSSL: pip install PyOpenSSL')

from pytz import timezone
from lxml import etree
from lxml.etree import DocumentInvalid
from xml.dom.minidom import parse, parseString

try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError('Instalar Libreria suds')


class SRIService(object):

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
        tipo_emision = self.get_type_emission()
        dato = values[0] + [tipo_emision] + values[1]
        modulo = check_digit.compute_mod11(dato)
        access_key = ''.join([dato, modulo])
        return access_key    

    def get_type_emission(self):
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
        

class CheckDigit(object):

    def __init__(self):
        # Definicion modulo 11
        self.MODULO_11 = {
            'BASE': 11,
            'FACTOR': 2,
            'RETORNO11': 0,
            'RETORNO10': 1,
            'PESO': 2,
            'MAX_WEIGHT': 7
            }

    def _eval_mod11(self, modulo):
        if modulo == self.MODULO_11['BASE']:
            return self.MODULO_11['RETORNO11']
        elif modulo == self.MODULO_11['BASE'] - 1:
            return self.MODULO_11['RETORNO10']
        else:
            return modulo

    def compute_mod11(self, dato):
        """
        Calculo mod 11
        return int
        """
        total = 0
        weight = self.MODULO_11['PESO']
        
        for item in reversed(dato):
            total += int(item) * weight
            weight += 1
            if weight > self.MODULO_11['MAX_WEIGHT']:
                weight = self.MODULO_11['PESO']
        mod = 11 - total % self.MODULO_11['BASE']

        mod = self._eval_mod11(mod)
        return mod


class Xades(object):

    def validate_xml(self, factura):
        """
        """
        INVOICE_XSD_PATH = 'docs/factura.xsd'
        file_path = os.path.join(os.path.dirname(__file__), INVOICE_XSD_PATH)
        schema_file = open(file_path)
        file_factura = etree.tostring(factura, pretty_print=True, encoding='utf-8')
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        try:
            xmlschema.assertValid(factura)
        except DocumentInvalid as e:
            raise osv.except_osv('Error de Datos', """El sistema generó el XML pero la factura no pasa la validación XSD del SRI.
            \nLos errores mas comunes son:\n* RUC,Cédula o Pasaporte contiene caracteres no válidos.\n* Números de documentos están duplicados.\n\nEl siguiente error contiene el identificador o número de documento en conflicto:\n\n %s""" % str(e))

    def apply_digital_signature(self, factura):
        """
        Metodo que aplica la firma digital al XML
        """
        OPT_PATH = '/opt/facturas/'
        JAR_PATH = 'firma/prctXadesBes.jar'
        JAVA_CMD = 'java'
        ds_document = False
        tree = etree.ElementTree(factura)
        name = '%s%s.xml' % (OPT_PATH, claveAcceso)
        tree.write(name, pretty_print=True, xml_declaration=True, encoding='utf-8', method="xml")
        # firma electrónica del xml
        firma_path = os.path.join(os.path.dirname(__file__), JAR_PATH)
        #
        file_pk12 = ''
        password = ''
        # invocación del jar de la firma electrónica
        subprocess.call([JAVA_CMD, '-jar', firma_path, name, name, file_pk12, password])
        return ds_document
        

if __name__ == '__main__':
    cd = CheckDigit()
    dato = '41261533'
    modulo = cd.compute_mod11(dato)
    print modulo
