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
import logging

from lxml import etree

from osv import osv, fields
from tools import config
from tools.translate import _
from tools import ustr
import decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

from .xades.sri import Service as SRIService, InvoiceXML

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
        'numero_autorizacion': fields.char('Número de Autorización', size=37, readonly=True),
        'fecha_autorizacion':  fields.datetime('Fecha y Hora de Autorización', readonly=True),
        'autorizado_sri': fields.boolean('¿Autorizado SRI?', readonly=True),
        'security_code': fields.char('Código de Seguridad', size=8)
        }

    def get_code(self, cr, uid, invoice):
        """
        TODO: revisar la generacion
        del codigo de 8 digitos
        """
        arreglo = invoice.origin.split('/')
        return (arreglo[1] + arreglo[2])[2:10]

    def _get_tax_element(self, invoice, access_key, emission_code):
        """
        """
        company = invoice.company_id
        auth = invoice.journal_id.auth_id
        infoTributaria = etree.Element('infoTributaria')
        etree.SubElement(infoTributaria, 'ambiente').text = SRIService.get_env_test()
        etree.SubElement(infoTributaria, 'tipoEmision').text = emission_code
        etree.SubElement(infoTributaria, 'razonSocial').text = company.name
        etree.SubElement(infoTributaria, 'nombreComercial').text = company.name
        etree.SubElement(infoTributaria, 'ruc').text = company.partner_id.ced_ruc
        etree.SubElement(infoTributaria, 'claveAcceso').text = access_key
        etree.SubElement(infoTributaria, 'codDoc').text = auth.type_id.code
        etree.SubElement(infoTributaria, 'estab').text = auth.serie_entidad
        etree.SubElement(infoTributaria, 'ptoEmi').text = auth.serie_emision
        etree.SubElement(infoTributaria, 'secuencial').text = invoice.supplier_invoice_number.replace('-','')[6:15]
        etree.SubElement(infoTributaria, 'dirMatriz').text = company.street
        return infoTributaria

    def _get_discount(self, cr, uid, invoice):
        descuento = '0.00'
        ## for line in invoice.invoice_line:
        ##     if line.product_id.default_code == 'DESC':
        ##         descuento = '%.2f' % (line.price_unit*-1)
        return descuento

    def _get_invoice_element(self, cr, uid, invoice):
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
        etree.SubElement(infoFactura, 'totalDescuento').text = self.get_discount(cr, uid, invoice)

        # totalConImpuestos
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

        if invoice.state == 'paid':
            pagos = self.get_payment_element(cr, uid, invoice)
            infoFactura.append(pagos)        

        return infoFactura

    def _get_detail_element(self, invoice):
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
                    tax_amount = cur_obj.compute(cr, uid, invoice.currency_id.id, company_currency, tax_line.amount * tax_line.tax_sign, context={'date': invoice.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
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

        # generar detalles
        detalles = self._get_detail_element(invoice)

        factura.append(detalles)        
        return factura

    def get_access_key(self, cr, uid, invoice):
        auth = invoice.journal_id.auth_id
        ld = invoice.date_invoice.split('-')
        ld.reverse()
        fecha = ''.join(ld)
        #
        tcomp = auth.type_id.code
        ruc = invoice.company_id.partner_id.ced_ruc
        serie = '{0}{1}'.format(auth.serie_entidad, auth.serie_emision)
        numero = invoice.supplier_invoice_number[6:15] # FIX w/ number
        codigo_numero = self.get_code(cr, uid, invoice)
        access_key = (
            [fecha, tcomp, ruc],
            [serie, numero, codigo_numero]
            )
        return access_key    

    def action_generate_einvoice(self, cr, uid, ids, context=None):
        """
        
        """
        for obj in self.browse(cr, uid, ids):
            # Codigo de acceso
            ak_temp = self.get_access_key(cr, uid, obj)            
            access_key, emission_code = SRIService.create_access_key(ak_temp)
            self.write(cr, uid, [obj.id], {'clave_acceso': access_key})

            # XML del comprobante electrónico: factura
            factura = self._generate_xml_invoice(cr, uid, obj, access_key, emission_code)

            #validación del xml
            inv_xml = InvoiceXML(factura)
            InvoiceXML.validate_xml()
            inv_str = InvoiceXML.to_string()

            # firma de XML, now what ??
            # TODO: zip, checksum, save, send
            xades = Xades(inv_str)
            xades.sign_document()
            ds_invoice = xades.get_xml()
            
        return True

"""    def action_einvoice_send_receipt(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        name = '%s%s.xml' %('/opt/facturas/', obj.clave_acceso)
        cadena = open(name, mode='rb').read()
        document = parseString(cadena.strip())
        xml = document.toxml('UTF-8').encode('base64')
    
        url = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
        client = Client(url)
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
                mensaje_error += 'Identificador: ' + mensaje[i].identificador + '\nMensaje: ' + mensaje[i].mensaje + '\nInformación Adicional: ' + mensaje[i].informacionAdicional + "\nTipo: " + mensaje[i].tipo + "\n"
                i += 1
            raise osv.except_osv('Error SRI', mensaje_error)
        return True

    def action_einvoice_authorization(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        if not obj.numero_autorizacion:
            try:
                url_auto = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'
                client_auto = Client(url_auto)
                result_auto =  client_auto.service.autorizacionComprobante(obj.clave_acceso)
                self.__logger.info("AutorizacionComprobantes: %s" % result_auto)
                if result_auto[2] == '':
                    raise osv.except_osv('Error SRI', 'No existe comprobante')
                else:
                    autorizaciones = result_auto[2].autorizacion
                    i = 0
                    while i < len(autorizaciones):
                        autorizacion = autorizaciones[i]
                        estado = autorizacion.estado
                        fecha_autorizacion = autorizacion.fechaAutorizacion
                        if (estado == 'NO AUTORIZADO'):
                            self.write(cr, uid, obj.id, {'autorizado_sri': False})
                            mensajes = autorizacion.mensajes
                            j = 0
                            mensaje_error += "\nErrores:\n"
                            while j < len(mensajes):
                                mensaje = mensajes[j]
                                mensaje_error += 'Identificador: ' + mensaje[j].identificador + '\nMensaje: ' + mensaje[j].mensaje + '\nTipo: ' + mensaje[j].tipo + '\n'
                                j += 1
                            raise osv.except_osv('Error SRI', mensaje_error)
                        else:
                            numero_autorizacion = autorizacion.numeroAutorizacion
                            self.write(cr, uid, obj.id, {'autorizado_sri': True, 'numero_autorizacion': numero_autorizacion, 'fecha_autorizacion': fecha_autorizacion})
                            autorizacion_xml = etree.Element('autorizacion')
                            etree.SubElement(autorizacion_xml, 'estado').text = estado
                            etree.SubElement(autorizacion_xml, 'numeroAutorizacion').text = numero_autorizacion
                            local_tz = timezone('America/Guayaquil')
                            etree.SubElement(autorizacion_xml, 'fechaAutorizacion').text = str(fecha_autorizacion.strftime("%d/%m/%Y %H:%M:%S"))
                            etree.SubElement(autorizacion_xml, 'comprobante').text = etree.CDATA(autorizacion.comprobante)
                    
                            tree = etree.ElementTree(autorizacion_xml)
                            name = '%s%s.xml' %('/opt/facturas/', obj.clave_acceso)
                            fichero = tree.write(name,pretty_print=True,xml_declaration=True,encoding='utf-8',method="xml")
                                
                        i += 1
            except TransportError as e:
                #raise osv.except_osv('Error', str(e))
                raise osv.except_osv(('Warning!'), (str(e)))
                
        return True
        
    def action_einvoice_send_mail(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        name = '%s%s.xml' %('/opt/facturas/', obj.clave_acceso)
        cadena = open(name, mode='rb').read()
        attachment_id = self.pool.get('ir.attachment').create(cr, uid, 
            {
                'name': '%s.xml' % (obj.clave_acceso),
                'datas': base64.b64encode(cadena),
                'datas_fname':  '%s.xml' % (obj.clave_acceso),
                'res_model': self._name,
                'res_id': obj.id,
                'type': 'binary'
            }, context=context)
                            
        email_template_obj = self.pool.get('email.template')
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'email_template_edi_invoice')[1]
        email_template_obj.write(cr, uid, template_id, {'attachment_ids': [(6, 0, [attachment_id])]})  
        email_template_obj.send_mail(cr, uid, template_id, obj.id, True)
        
        return True
"""
