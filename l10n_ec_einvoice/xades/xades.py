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
from OpenSSL import crypto

from pytz import timezone
from lxml import etree
from lxml.etree import DocumentInvalid
from xml.dom.minidom import parse, parseString
from suds.client import Client
from suds.transport import TransportError

MOD_OPT_11 = 0
MOD_OPT_10 = 1
OPTION_1 = 10

AMBIENTE_PRUEBA = '1'
AMBIENTE_PROD = '2'

#Move as field in company ?
TEST_RECEIV_DOCS = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
TEST_AUTH_DOCS = 'https://celcer.sri.gob.ec/comprobantes-electronicos- ws/AutorizacionComprobantes?wsdl'


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

    def get_standard_emission(self, invoice):
        """
        Metodo de tipo de emision
        TODO: mejorar documentacion
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
            
    def get_access_key(self, invoice):
        auth = invoice.journal_id.auth_id
        ld = invoice.date_invoice.split('-')
        ld.reverse()
        fecha = ''.join(ld)
        #
        tcomp = auth.type_id.code
        ruc = invoice.company_id.partner_id.ced_ruc
        serie = '{0}{1}'.format(auth.serie_entidad, auth.serie_emision)
        numero = invoice.supplier_invoice_number # FIX w/ number
        codigo_numero = self.get_code(cr, uid, invoice)
        tipo_emision = self.get_standard_emission(cr, uid, invoice)
        #
        ak_temp = ''.join([fecha, tcomp, ruc, self.AMBIENTE_PRUEBA, 
                           serie, numero, codigo_numero, tipo_emision])
        access_key = ''.join([ak_temp, str(self.get_mod(ak_temp, self.MODULO_11))])
        return access_key

    def _get_tax_element(self, invoice, access_key):
        """
        """
        company = invoice.company_id
        auth = invoice.journal_id.auth_id
        infoTributaria = etree.Element('infoTributaria')
        etree.SubElement(infoTributaria, 'ambiente').text = self.AMBIENTE_PRUEBA
        etree.SubElement(infoTributaria, 'tipoEmision').text = self.get_standard_emission(cr, uid, obj)
        etree.SubElement(infoTributaria, 'razonSocial').text = company.name
        etree.SubElement(infoTributaria, 'nombreComercial').text = company.name
        etree.SubElement(infoTributaria, 'ruc').text = company.partner_id.ced_ruc
        etree.SubElement(infoTributaria, 'claveAcceso').text = access_key
        etree.SubElement(infoTributaria, 'codDoc').text = auth.type_id.code
        etree.SubElement(infoTributaria, 'estab').text = auth.serie_entidad
        etree.SubElement(infoTributaria, 'ptoEmi').text = auth.serie_emision
        etree.SubElement(infoTributaria, 'secuencial').text = invoice.supplier_invoice_number
        etree.SubElement(infoTributaria, 'dirMatriz').text = company.street
        return infoFactura

    def _get_invoice_element(self, invoice):
        company = invoice.company_id
        partner = invoice.partner_id
        infoFactura = etree.Element('infoFactura')
        etree.SubElement(infoFactura, 'fechaEmision').text = time.strftime('%d/%m/%Y', obj.date_invoice)
        etree.SubElement(infoFactura, 'dirEstablecimiento').text = company.street2
        etree.SubElement(infoFactura, 'contribuyenteEspecial').text = company.company_registry
        etree.SubElement(infoFactura, 'obligadoContabilidad').text = 'SI'
        etree.SubElement(infoFactura, 'tipoIdentificacionComprador').text = tipoIdentificacion[partner.type_ced_ruc]
        etree.SubElement(infoFactura, 'razonSocialComprador').text = partner.name
        etree.SubElement(infoFactura, 'identificacionComprador').text = partner.ced_ruc
        etree.SubElement(infoFactura, 'totalSinImpuestos').text = '%.2f' % (invoice.amount_untaxed)
        descuento = '0.00'
        for line in invoice.invoice_line:
            if line.product_id.default_code == 'DESC':
                descuento = '%.2f' % (line.price_unit*-1)
        etree.SubElement(infoFactura, 'totalDescuento').text = descuento
        #totalConImpuestos
        totalConImpuestos = etree.Element('totalConImpuestos')
        for tax in invoice.tax_line:
            #totalImpuesto
            if tax.tax_group in ['vat', 'vat0', 'ice', 'other']:
                totalImpuesto = etree.Element('totalImpuesto')
                etree.SubElement(totalImpuesto, 'codigo').text = codigoImpuesto[tax.tax_group]
                etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax.tax_group]
                etree.SubElement(totalImpuesto, 'baseImponible').text = '%.2f' % (tax.base_amount)
                etree.SubElement(totalImpuesto, 'valor').text = '%.2f' % (tax.tax_amount)
                totalConImpuestos.append(totalImpuesto)
        infoFactura.append(totalConImpuestos)
        etree.SubElement(infoFactura, 'propina').text = '0.0000'
        etree.SubElement(infoFactura, 'importeTotal').text = '%.2f' % (invoice.amount_pay)
        return infoFactura

    def _generate_detail_element(self, invoice):
        """
        """
        detalles = etree.Element('detalles')
        for line in invoice.invoice_line:
            if line.product_id.default_code == 'DESC':
                continue
            detalle = etree.Element('detalle')
            etree.SubElement(detalle, 'codigoPrincipal').text = line.product_id.default_code
            if line.product_id.manufacturer_pref:
                etree.SubElement(detalle, 'codigoAuxiliar').text = line.product_id.manufacturer_pref
            etree.SubElement(detalle, 'descripcion').text = line.product_id.name
            etree.SubElement(detalle, 'cantidad').text = '%.6f' % (line.quantity)
            etree.SubElement(detalle, 'precioUnitario').text = '%.6f' % (line.price_unit)
            etree.SubElement(detalle, 'descuento').text = '0.0000'
            etree.SubElement(detalle, 'precioTotalSinImpuesto').text = '%.2f' % (line.price_subtotal)
            impuestos = etree.Element('impuestos')
            for tax_line in line.invoice_line_tax_id:
                if tax_line.tax_group in ['vat', 'vat0', 'ice', 'other']:
                    base_amount = cur_obj.compute(cr, uid, invoice.currency_id.id, company_currency, line.price_subtotal * tax_line.base_sign, context={'date': invoice.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    tax_amount = cur_obj.compute(cr, uid, obj.currency_id.id, company_currency, tax_line.amount * tax_line.tax_sign, context={'date': invoice.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    impuesto = etree.Element('impuesto')
                    etree.SubElement(impuesto, 'codigo').text = codigoImpuesto[tax_line.tax_group]
                    etree.SubElement(impuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax_line.tax_group]
                    etree.SubElement(impuesto, 'tarifa').text = '%.2f' % (tax_amount * 100)
                    etree.SubElement(impuesto, 'baseImponible').text = '%.2f' % (base_amount)
                    etree.SubElement(impuesto, 'valor').text = '%.2f' % (base_amount * tax_amount)
                    impuestos.append(impuesto)
            detalle.append(impuestos)
            detalles.append(detalle)
        return detalles    

    def _generate_xml_invoice(self, invoice, access_key):
        """
        """
        factura = etree.Element('factura')
        factura.set("id", "comprobante")
        factura.set("version", "1.1.0")

        # generar infoTributaria
        infoTributaria = self._get_tax_element(invoice, access_key)
        factura.append(infoTributaria)

        # generar infoFactura
        infoFactura = self.get_invoice_element(invoice)
        factura.append(infoFactura)

        # generar detalles
        detalles = self.get_detail_element(invoice)

        factura.append(detalles)        
        return factura

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
