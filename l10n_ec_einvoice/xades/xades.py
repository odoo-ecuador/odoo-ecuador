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


class CheckDigit(object):

    # Definicion modulo 11
    _MODULO_11 = {
        'BASE': 11,
        'FACTOR': 2,
        'RETORNO11': 0,
        'RETORNO10': 1,
        'PESO': 2,
        'MAX_WEIGHT': 7
    }

    @classmethod
    def _eval_mod11(self, modulo):
        if modulo == self._MODULO_11['BASE']:
            return self._MODULO_11['RETORNO11']
        elif modulo == self._MODULO_11['BASE'] - 1:
            return self._MODULO_11['RETORNO10']
        else:
            return modulo

    @classmethod
    def compute_mod11(self, dato):
        """
        Calculo mod 11
        return int
        """
        total = 0
        weight = self._MODULO_11['PESO']
        
        for item in reversed(dato):
            total += int(item) * weight
            weight += 1
            if weight > self._MODULO_11['MAX_WEIGHT']:
                weight = self._MODULO_11['PESO']
        mod = 11 - total % self._MODULO_11['BASE']

        mod = self._eval_mod11(mod)
        return mod


class Xades(object):

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
