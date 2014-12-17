#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
  
"""Ecuador S.R.I. Electronic Invoice (Emisión de Documentos Electrónicos)"""
 
# Modified by: @miltonlab

from __future__ import unicode_literals
  
import unittest
import pysimplesoap
from pysimplesoap.client import SoapClient, SoapFault
  
import sys
if sys.version > '3':
    basestring = str
    long = int
  
# Documentation: http://www.sri.gob.ec/web/10138/145
  
  
class TestSRI(unittest.TestCase):

    # @unittest.skip("starting ...")  
    def test_validar(self):
        "Prueba de envío de un comprobante electrónico"
        import base64
        WSDL = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
        # https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl
        #client = SoapClient(wsdl=WSDL, ns="ec")
	client = SoapClient(
		location='https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes',
		wsdl='https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl',
		#namespace='http://ec.gob.sri.ws.recepcion',
		#action='validarComprobante',
                action='http://ec.gob.sri.ws.recepcion/comprobantes-electronicos-ws/RecepcionComprobantes/validarComprobante',
		trace=False,
		ns='http://ec.gob.sri.ws.recepcion',

	)
        from pysimplesoap.simplexml import SimpleXMLElement
        print 'client.__dict__: ', client.__dict__
        xml = open('../docs/factura35.xml', mode='rb').read()
        print 'xml: ', xml
        xml_simple = SimpleXMLElement(xml)
        # xml_encode = base64.b64encode(xml)
        response = client.validarComprobante(
            xml=xml_simple.as_xml()
            # xml=xml_encode
        )
        print '>>> ', response
        # self.assertEquals(ret, {'RespuestaRecepcionComprobante': {'comprobantes': [{'comprobante': {'mensajes': [{'mensaje': {'identificador': '35', 'mensaje': 'ARCHIVO NO CUMPLE ESTRUCTURA XML', 'informacionAdicional': 'Content is not allowed in prolog.', 'tipo': 'ERROR'}}], 'claveAcceso': 'N/A'}}], 'estado': 'DEVUELTA'}})

    @unittest.skip("starting ...")
    def test_validar_pysimplesoap(self):
        from pysimplesoap.simplexml import SimpleXMLElement
        from pysimplesoap.client import SoapClient
        xml = SimpleXMLElement(open('../docs/factura35.xml').read())
        headers = {'Content-type': 'text/html; charset="UTF-8"',
                   'Content-length': '%s' % len(xml),
                   'SOAPAction': '"validarComprobante"'}
        cli = SoapClient()
        cli.http.request(
            'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes', 
            'POST', body=xml.as_xml(), headers=headers)

    @unittest.skip("starting ...")
    def test_validar_pure_http(self):
        import httplib
        import xml.dom.minidom
        HOST = "https://celcer.sri.gob.ec"
        API_URL = "/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl"
        request = open('../docs/factura.xml', "r").read()
        wsSRI = httplib.HTTP(host=HOST, port=443)
        wsSRI.putrequest("POST", API_URL)
        wsSRI.putheader("Host", HOST)
        wsSRI.putheader("User-Agent", "Python post")
        wsSRI.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
        wsSRI.putheader("Content-length", "%d" % len(request))
        wsSRI.endheaders()
        statuscode, statusmessage, header = wsSRI.getreply()
        result = wsSRI.getfile().read()
        resultxml = xml.dom.minidom.parseString(result)
        print statuscode, statusmessage, header
        print resultxml.toprettyxml() 

    @unittest.skip("starting ...")
    def test_autorizar(self):
        WSDL = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'
        # https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl
        client = SoapClient(wsdl=WSDL, ns="ec")
        ret = client.autorizacionComprobante(claveAccesoComprobante="1702201205176001321000110010030001000011234567816")
        self.assertEquals(ret, {'RespuestaAutorizacionComprobante': {'autorizaciones': [], 'claveAccesoConsultada': '1702201205176001321000110010030001000011234567816', 'numeroComprobantes': '0'}})
  
  
# Run this TesCase:
# python -m unittest wstest


# Testing in ipyton
"""
elpy :: emacs - python - ide: elpy-use-ipython
xml=SimpleXMLElement(open('../docs/factura.xml').read())
headers = {'Content-type': 'text/html; charset="UTF-8"','Content-length': str(len(xml)), 'SOAPAction': '"validarComprobante"'}
cli = SoapClient()
cli.http.request('https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes', 'POST', body=xml.as_xml(), headers=headers)
"""
