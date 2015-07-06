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


import time
from datetime import datetime
import logging
import base64
import urllib2
import httplib

from lxml import etree
from xml.dom.minidom import parse, parseString
from socket import error as SocketError

from osv import osv, fields
from tools import config
from tools.translate import _
from tools import ustr
import decimal_precision as dp
import netsvc

import utils
from .xades.sri import Service as SRIService, InvoiceXML
from .xades.xades import Xades

try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError('Instalar Libreria suds')

tipoDocumento = {
    '01': '01',
    '04': '04',
    '05': '05',
    '06': '06',
    '07': '07',
    '18': '01',
}

tipoIdentificacion = {
    'ruc' : '04',
    'cedula' : '05',
    'pasaporte' : '06',
    'venta_consumidor_final' : '07',
    'identificacion_exterior' : '08',
    'placa' : '09',
}

codigoImpuesto = {
    'vat': '2',
    'vat0': '2',
    'ice': '3',
    'other': '5'
}

tarifaImpuesto = {
    'vat0': '0',
    'vat': '2',
    'novat': '6',
    'other': '7',
}

class AccountInvoice(osv.osv):

    _inherit = 'account.invoice'
    __logger = logging.getLogger(_inherit)
    
    _columns = {
        'clave_acceso': fields.char('Clave de Acceso', size=49, readonly=True, store=True),
        'numero_autorizacion': fields.char('Número de Autorización', size=37, readonly=True, store=True),
        'fecha_autorizacion':  fields.datetime('Fecha y Hora de Autorización', readonly=True, store=True),
        'autorizado_sri': fields.boolean('¿Autorizado SRI?', readonly=True, store=True),
        'security_code': fields.char('Código de Seguridad', size=8),
	'emission_code': fields.char('Tipo de Emisión', size=1),
        }

    def _get_tax_element(self, invoice, access_key, emission_code):
        """
        """
        company = invoice.company_id
        auth = invoice.journal_id.auth_id
        infoTributaria = etree.Element('infoTributaria')
        etree.SubElement(infoTributaria, 'ambiente').text = SRIService.get_env_prod()
        etree.SubElement(infoTributaria, 'tipoEmision').text = emission_code
        etree.SubElement(infoTributaria, 'razonSocial').text = company.name
        etree.SubElement(infoTributaria, 'nombreComercial').text = company.name
        etree.SubElement(infoTributaria, 'ruc').text = company.partner_id.ced_ruc
        etree.SubElement(infoTributaria, 'claveAcceso').text = access_key
        etree.SubElement(infoTributaria, 'codDoc').text = tipoDocumento[auth.type_id.code]
        etree.SubElement(infoTributaria, 'estab').text = auth.serie_entidad
        etree.SubElement(infoTributaria, 'ptoEmi').text = auth.serie_emision
        etree.SubElement(infoTributaria, 'secuencial').text = invoice.number[6:15]
        etree.SubElement(infoTributaria, 'dirMatriz').text = company.street
        return infoTributaria

    def _get_invoice_element(self, invoice):
        """
        """
        company = invoice.company_id
        partner = invoice.partner_id
        infoFactura = etree.Element('infoFactura')
        etree.SubElement(infoFactura, 'fechaEmision').text = time.strftime('%d/%m/%Y',time.strptime(invoice.date_invoice, '%Y-%m-%d'))
        etree.SubElement(infoFactura, 'dirEstablecimiento').text = company.street2
        if company.company_registry:
            etree.SubElement(infoFactura, 'contribuyenteEspecial').text = company.company_registry
        etree.SubElement(infoFactura, 'obligadoContabilidad').text = 'SI'
        etree.SubElement(infoFactura, 'tipoIdentificacionComprador').text = tipoIdentificacion[partner.type_ced_ruc]
        etree.SubElement(infoFactura, 'razonSocialComprador').text = partner.name
        etree.SubElement(infoFactura, 'identificacionComprador').text = partner.ced_ruc
        etree.SubElement(infoFactura, 'totalSinImpuestos').text = '%.2f' % (invoice.amount_untaxed)
        etree.SubElement(infoFactura, 'totalDescuento').text = '0.00'#'%.2f' % (invoice.discount_total)
        
        #totalConImpuestos
        totalConImpuestos = etree.Element('totalConImpuestos')
        for tax in invoice.tax_line:

            if tax.tax_group in ['vat', 'vat0', 'ice', 'other']:
                totalImpuesto = etree.Element('totalImpuesto')
                etree.SubElement(totalImpuesto, 'codigo').text = codigoImpuesto[tax.tax_group]
                etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax.tax_group]
                etree.SubElement(totalImpuesto, 'baseImponible').text = '{:.2f}'.format(tax.base_amount)
                etree.SubElement(totalImpuesto, 'valor').text = '{:.2f}'.format(tax.tax_amount)
                totalConImpuestos.append(totalImpuesto)
                
        infoFactura.append(totalConImpuestos)
        
        etree.SubElement(infoFactura, 'propina').text = '0.00'
        etree.SubElement(infoFactura, 'importeTotal').text = '{:.2f}'.format(invoice.amount_pay)
        etree.SubElement(infoFactura, 'moneda').text = 'DOLAR'
            
        return infoFactura

    def _get_refund_element(self, refund, invoice):
        """
        """
        company = refund.company_id
        partner = refund.partner_id
        infoNotaCredito = etree.Element('infoNotaCredito')
        etree.SubElement(infoNotaCredito, 'fechaEmision').text = time.strftime('%d/%m/%Y',time.strptime(refund.date_invoice, '%Y-%m-%d'))
        etree.SubElement(infoNotaCredito, 'dirEstablecimiento').text = company.street2
        etree.SubElement(infoNotaCredito, 'tipoIdentificacionComprador').text = tipoIdentificacion[partner.type_ced_ruc]
        etree.SubElement(infoNotaCredito, 'razonSocialComprador').text = partner.name
        etree.SubElement(infoNotaCredito, 'identificacionComprador').text = partner.ced_ruc
        etree.SubElement(infoNotaCredito, 'contribuyenteEspecial').text = company.company_registry
        etree.SubElement(infoNotaCredito, 'obligadoContabilidad').text = 'SI'
        etree.SubElement(infoNotaCredito, 'codDocModificado').text = '01'
        if refund.name:
            etree.SubElement(infoNotaCredito, 'numDocModificado').text = invoice[0].supplier_invoice_number
            etree.SubElement(infoNotaCredito, 'fechaEmisionDocSustento').text = time.strftime('%d/%m/%Y',time.strptime(invoice[0].date_invoice, '%Y-%m-%d'))
        else:
            etree.SubElement(infoNotaCredito, 'numDocModificado').text = refund.reference_invoice_number
            etree.SubElement(infoNotaCredito, 'fechaEmisionDocSustento').text = time.strftime('%d/%m/%Y',time.strptime(refund.reference_invoice_date, '%Y-%m-%d'))
        etree.SubElement(infoNotaCredito, 'totalSinImpuestos').text = '%.2f' % (abs(refund.amount_untaxed))
        etree.SubElement(infoNotaCredito, 'valorModificacion').text = '%.2f' % (abs(refund.amount_pay))
        etree.SubElement(infoNotaCredito, 'moneda').text = 'DOLAR'
        
        #totalConImpuestos
        totalConImpuestos = etree.Element('totalConImpuestos')
        for tax in refund.tax_line:

            if tax.tax_group in ['vat', 'vat0', 'ice', 'other']:
                totalImpuesto = etree.Element('totalImpuesto')
                etree.SubElement(totalImpuesto, 'codigo').text = codigoImpuesto[tax.tax_group]
                etree.SubElement(totalImpuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax.tax_group]
                etree.SubElement(totalImpuesto, 'baseImponible').text = '{:.2f}'.format(abs(tax.base_amount))
                etree.SubElement(totalImpuesto, 'valor').text = '{:.2f}'.format(abs(tax.tax_amount))
                totalConImpuestos.append(totalImpuesto)
                
        infoNotaCredito.append(totalConImpuestos)
        etree.SubElement(infoNotaCredito, 'motivo').text = refund.origin
        return infoNotaCredito
        
    def _get_detail_element(self, invoice):
        """
        """
        def fix_chars(code):
            if code:
                code.replace(u'%',' ').replace(u'º', ' ').replace(u'Ñ', 'N').replace(u'ñ','n')
                return code
            return ''
            
        detalles = etree.Element('detalles')
        for line in invoice.invoice_line:
            detalle = etree.Element('detalle')
            etree.SubElement(detalle, 'codigoPrincipal').text = fix_chars(line.product_id.default_code)
#            if line.product_id.manufacturer_pref:
#                etree.SubElement(detalle, 'codigoAuxiliar').text = line.product_id.manufacturer_pref.replace(u'%',' ').replace(u'º', ' ').replace(u'Ñ', 'N').replace(u'ñ','n')
            etree.SubElement(detalle, 'descripcion').text = fix_chars(line.product_id.name)
            etree.SubElement(detalle, 'cantidad').text = '%.6f' % (line.quantity)
            etree.SubElement(detalle, 'precioUnitario').text = '%.6f' % (line.price_unit)
            etree.SubElement(detalle, 'descuento').text = '0.00'#'%.2f' % (line.discount_value)
            etree.SubElement(detalle, 'precioTotalSinImpuesto').text = '%.2f' % (line.price_subtotal)
            impuestos = etree.Element('impuestos')
            for tax_line in line.invoice_tax: #iterar en invoice_tax
                if tax_line.tax_group in ['vat', 'vat0', 'ice', 'other']:
                    impuesto = etree.Element('impuesto')
                    etree.SubElement(impuesto, 'codigo').text = codigoImpuesto[tax_line.tax_group]
                    etree.SubElement(impuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax_line.tax_group]
                    etree.SubElement(impuesto, 'tarifa').text = '%.2f' % (tax_line.amount * 100)
                    etree.SubElement(impuesto, 'baseImponible').text = '%.2f' % (line.price_subtotal)
                    etree.SubElement(impuesto, 'valor').text = '%.2f' % (line.amount_tax)
                    impuestos.append(impuesto)
            detalle.append(impuestos)
            detalles.append(detalle)
        return detalles

    def _get_detail_element_refund(self, invoice):
        """
        """
        detalles = etree.Element('detalles')
        for line in invoice.invoice_line:
            detalle = etree.Element('detalle')
            etree.SubElement(detalle, 'codigoInterno').text = line.product_id.default_code.replace(u'%',' ').replace(u'º', ' ').replace(u'Ñ', 'N').replace(u'ñ','n')
            if line.product_id.manufacturer_pref:
                etree.SubElement(detalle, 'codigoAdicional').text = line.product_id.manufacturer_pref.replace(u'%',' ').replace(u'º', ' ').replace(u'Ñ', 'N').replace(u'ñ','n')
            etree.SubElement(detalle, 'descripcion').text = line.product_id.name.replace(u'%',' ').replace(u'º', ' ').replace(u'Ñ', 'N').replace(u'ñ','n')
            etree.SubElement(detalle, 'cantidad').text = '%.6f' % (line.quantity)
            etree.SubElement(detalle, 'precioUnitario').text = '%.6f' % (line.price_unit)
            etree.SubElement(detalle, 'descuento').text = '%.2f' % (line.discount_value)
            etree.SubElement(detalle, 'precioTotalSinImpuesto').text = '%.2f' % (line.price_subtotal)
            impuestos = etree.Element('impuestos')
            for tax_line in line.invoice_line_tax_id:
                if tax_line.tax_group in ['vat', 'vat0', 'ice', 'other']:
                    impuesto = etree.Element('impuesto')
                    etree.SubElement(impuesto, 'codigo').text = codigoImpuesto[tax_line.tax_group]
                    etree.SubElement(impuesto, 'codigoPorcentaje').text = tarifaImpuesto[tax_line.tax_group]
                    etree.SubElement(impuesto, 'tarifa').text = '%.2f' % (tax_line.amount * 100)
                    etree.SubElement(impuesto, 'baseImponible').text = '%.2f' % (line.price_subtotal)
                    etree.SubElement(impuesto, 'valor').text = '%.2f' % (line.amount_tax)
                    impuestos.append(impuesto)
            detalle.append(impuestos)
            detalles.append(detalle)
        return detalles

    def _generate_xml_invoice(self, invoice, access_key, emission_code):
        """
        """
        factura = etree.Element('factura')
        factura.set("id", "comprobante")
        factura.set("version", "1.1.0")
        
        # generar infoTributaria
        infoTributaria = self._get_tax_element(invoice, access_key, emission_code)
        factura.append(infoTributaria)
        
        # generar infoFactura
        infoFactura = self._get_invoice_element(invoice)
        factura.append(infoFactura)
        
        #generar detalles
        detalles = self._get_detail_element(invoice)
        
        factura.append(detalles)
        return factura

    def _generate_xml_refund(self, refund, invoice, access_key, emission_code):
        """
        """
        notaCredito = etree.Element('notaCredito')
        notaCredito.set("id", "comprobante")
        notaCredito.set("version", "1.1.0")
        
        # generar infoTributaria
        infoTributaria = self._get_tax_element(refund, access_key, emission_code)
        notaCredito.append(infoTributaria)
        
        
        # generar infoNotaCredito
        infoNotaCredito = self._get_refund_element(refund, invoice)
        notaCredito.append(infoNotaCredito)
        
        #generar detalles
        detalles = self._get_detail_element_refund(refund)
        notaCredito.append(detalles)
        
        return notaCredito
    
    def get_access_key(self, cr, uid, invoice):
        auth = invoice.journal_id.auth_id
        ld = invoice.date_invoice.split('-')
        ld.reverse()
        fecha = ''.join(ld)
        #
        tcomp = tipoDocumento[auth.type_id.code]
        ruc = invoice.company_id.partner_id.ced_ruc
        serie = '{0}{1}'.format(auth.serie_entidad, auth.serie_emision)
        numero = invoice.number[6:15]
        codigo_numero = '12345678'#invoice.security_code
        tipo_emision = invoice.company_id.emission_code
        access_key = (
            [fecha, tcomp, ruc],
            [serie, numero, codigo_numero, tipo_emision]
            )
        return access_key

    def check_before_sent(self, cr, uid, obj):
        """
        """
        sql = "select autorizado_sri, number from account_invoice where state='open' and number < '%s' order by number desc limit 1" % obj.number
        cr.execute(sql)
        res = cr.fetchone()
        return res[0] and True or False
        
    def action_generate_einvoice(self, cr, uid, ids, context=None):
        """
        """
        LIMIT_TO_SEND = 5
        TITLE_NOT_SENT = u'No se puede enviar el comprobante electrónico al SRI'
        MESSAGE_SEQUENCIAL = u'Los comprobantes electrónicos deberán ser enviados al SRI para su autorización en orden cronológico y secuencial. Por favor enviar primero el comprobante inmediatamente anterior'
        MESSAGE_TIME_LIMIT = u'Los comprobantes electrónicos deberán enviarse a las bases de datos del SRI para su autorización en un plazo máximo de 24 horas'
        for obj in self.browse(cr, uid, ids):
            # Codigo de acceso
            if obj.type in [ 'out_invoice', 'out_refund']:
                # Validar que el envío del comprobante electrónico se realice dentro de las 24 horas posteriores a su emisión
                if (datetime.now() - datetime.strptime(obj.date_invoice, '%Y-%m-%d')).days > LIMIT_TO_SEND:
                    raise osv.except_osv(TITLE_NOT_SENT, MESSAGE_TIME_LIMIT)
                else:
                    # Validar que el envío de los comprobantes electrónicos sea secuencial
                    if not self.check_before_sent(cr, uid, obj):
                        raise osv.except_osv(TITLE_NOT_SENT, MESSAGE_SEQUENCIAL)
                    else:
                        ak_temp = self.get_access_key(cr, uid, obj)
                        access_key = SRIService.create_access_key(ak_temp)
                        emission_code = obj.company_id.emission_code
                        self.write(cr, uid, [obj.id], {'clave_acceso': access_key, 'emission_code': emission_code})
        
                        if obj.type == 'out_invoice':
                            # XML del comprobante electrónico: factura
                            factura = self._generate_xml_invoice(obj, access_key, emission_code)
                        else:
                            if not obj.origin:
                                raise osv.except_osv('Error de Datos', u'Falta el motivo de la devolución')
                            invoice_ids = self.pool.get('account.invoice').search(cr, uid, [('number','=',obj.name)])
                            factura_origen = self.browse(cr, uid, invoice_ids, context = context)
                            # XML del comprobante electrónico: factura
                            factura = self._generate_xml_refund(obj, factura_origen, access_key, emission_code)
            
                        #validación del xml
                        inv_xml = InvoiceXML(factura)
                        inv_xml.validate_xml(obj.type)
                        inv_xml.save(access_key)

                        # firma de XML, now what ??
                        # TODO: zip, checksum, save, send_mail
                        xades = Xades()
                        file_pk12 = obj.company_id.electronic_signature
                        password = obj.company_id.password_electronic_signature
                        xades.apply_digital_signature(access_key, file_pk12, password)
            
                        # recepción del comprobante electrónico
                        if not obj.clave_acceso:
                            self.send_receipt(cr, uid, access_key)
                        time.sleep(3)            
                        # solicitud de autorización del comprobante electrónico
                        self.request_authorization(cr, uid, obj, access_key)

                        if obj.type == 'out_invoice':
                            # envío del correo electrónico de factura al cliente
                            self.send_mail_invoice(cr, uid, obj, access_key, context)
                        else:
                            # envío del correo electrónico de nota de crédito al cliente
                            self.send_mail_refund(cr, uid, obj, access_key, context)

    def send_receipt(self, cr, uid, access_key):
        try:
            name = '%s%s.xml' %('/opt/facturas/', access_key)
            cadena = open(name, mode='rb').read()
            document = parseString(cadena.strip())
            xml = document.toxml('UTF-8').encode('base64')
    
            client = Client(SRIService.get_ws_prod()[0])
            result =  client.service.validarComprobante(xml)
            self.__logger.info("RecepcionComprobantes: %s" % result)
            mensaje_error = ""
            if (result[0] == 'DEVUELTA'):
                comprobante = result[1].comprobante
                mensaje_error += 'Clave de Acceso: ' + comprobante[0].claveAcceso
                mensajes = comprobante[0].mensajes
                i = 0
                mensaje_error += "\nErrores:\n"
                while i < len(mensajes):
                    mensaje = mensajes[i]
                    mensaje_error += 'Identificador: ' + mensaje[i].identificador + '\nMensaje: ' + mensaje[i].mensaje + '\nTipo: ' + mensaje[i].tipo + "\n"
                    i += 1
                raise osv.except_osv('Error SRI', mensaje_error)
        except TransportError as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' + str(e))
        except urllib2.URLError as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' +  str(e))
        except urllib2.HTTPError as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' + str(e))
        except httplib.BadStatusLine as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' + str(e))
        #except SocketError as e:
        #        raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' + unicode(str(e), "utf-8"))
        return True

    def request_authorization(self, cr, uid, obj, access_key):
        if not obj.numero_autorizacion:
            try:
                client_auto = Client(SRIService.get_ws_prod()[1])
                result_auto =  client_auto.service.autorizacionComprobante(access_key)
                self.__logger.info("AutorizacionComprobantes: %s" % result_auto)
                if result_auto[2] == '':
                    self.write(cr, uid, [obj.id], {'clave_acceso': access_key})
                    self.__logger.info("Clave de Acceso")
                else:
                    autorizaciones = result_auto[2].autorizacion
                    i = 0
                    autorizado = False
                    while i < len(autorizaciones):
                        autorizacion = autorizaciones[i]
                        estado = autorizacion.estado
                        fecha_autorizacion = autorizacion.fechaAutorizacion
                        mensaje_error = ''
                        if (estado == 'NO AUTORIZADO'):
                            #comprobante no autorizado
                            mensajes = autorizacion.mensajes
                            j = 0
                            mensaje_error += "\nErrores:\n"
                            while j < len(mensajes):
                                mensaje = mensajes[j]
                                mensaje_error += 'Identificador: ' + mensaje[j].identificador + '\nMensaje: ' + mensaje[j].mensaje + '\nTipo: ' + mensaje[j].tipo + '\n'
                                j += 1
                        else:
                            autorizado = True
                            numero_autorizacion = autorizacion.numeroAutorizacion
                        i += 1    
                    if autorizado == True:
                        self.write(cr, uid, obj.id, {'autorizado_sri': True, 'numero_autorizacion': numero_autorizacion, 'fecha_autorizacion': fecha_autorizacion})
                        autorizacion_xml = etree.Element('autorizacion')
                        etree.SubElement(autorizacion_xml, 'estado').text = estado
                        etree.SubElement(autorizacion_xml, 'numeroAutorizacion').text = numero_autorizacion
                        etree.SubElement(autorizacion_xml, 'fechaAutorizacion').text = str(fecha_autorizacion.strftime("%d/%m/%Y %H:%M:%S"))
                        etree.SubElement(autorizacion_xml, 'comprobante').text = etree.CDATA(autorizacion.comprobante)
                    
                        tree = etree.ElementTree(autorizacion_xml)
                        name = '%s%s.xml' %('/opt/facturas/', access_key)
                        fichero = tree.write(name,pretty_print=True,xml_declaration=True,encoding='utf-8',method="xml")
                    else:
                        raise osv.except_osv('Error SRI', mensaje_error)
            except TransportError as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' + str(e))
            except urllib2.URLError as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' +  str(e))
            except urllib2.HTTPError as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' + str(e))
            except httplib.BadStatusLine as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' + str(e))
            except SocketError as e:
                raise osv.except_osv('Error SRI', 'Indisponibilidad de Servicios, ' + unicode(str(e), "utf-8"))
        return True
        
    def send_mail_invoice(self, cr, uid, obj, access_key, context=None):
        name = '%s%s.xml' %('/opt/facturas/', access_key)
        cadena = open(name, mode='rb').read()
        attachment_id = self.pool.get('ir.attachment').create(cr, uid, 
            {
                'name': '%s.xml' % (access_key),
                'datas': base64.b64encode(cadena),
                'datas_fname':  '%s.xml' % (access_key),
                'res_model': self._name,
                'res_id': obj.id,
                'type': 'binary'
            }, context=context)
                            
        email_template_obj = self.pool.get('email.template')
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'email_template_edi_invoice')[1]
        email_template_obj.write(cr, uid, template_id, {'attachment_ids': [(6, 0, [attachment_id])]})  
        email_template_obj.send_mail(cr, uid, template_id, obj.id, True)
        
        return True

    def send_mail_refund(self, cr, uid, obj, access_key, context=None):
        name = '%s%s.xml' %('/opt/facturas/', access_key)
        cadena = open(name, mode='rb').read()
        attachment_id = self.pool.get('ir.attachment').create(cr, uid,
            {
                'name': '%s.xml' % (access_key),
                'datas': base64.b64encode(cadena),
                'datas_fname':  '%s.xml' % (access_key),
                'res_model': self._name,
                'res_id': obj.id,
                'type': 'binary'
            }, context=context)

        email_template_obj = self.pool.get('email.template')
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'email_template_edi_refund')[1]
        email_template_obj.write(cr, uid, template_id, {'attachment_ids': [(6, 0, [attachment_id])]})
        email_template_obj.send_mail(cr, uid, template_id, obj.id, True)

        return True
