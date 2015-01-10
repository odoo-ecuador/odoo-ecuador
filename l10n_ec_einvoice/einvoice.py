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

from osv import osv, fields
from tools import config
from tools.translate import _
from tools import ustr
import decimal_precision as dp
import netsvc

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

    def action_generate_einvoice(self, cr, uid, ids, context=None):
        """
        
        """
        for obj in self.browse(cr, uid, ids):
            # Codigo de acceso
            access_key = self.get_access_key(cr, uid, obj)
            self.write(cr, uid, obj.id, {'clave_acceso': access_key})

            # XML del comprobante electrónico: factura
            factura = self.generate_xml_invoice(cr, uid, obj, access_key)

            #validación del xml
            self.validate_xml(cr, uid, factura)

            # firma de XML, now what ??
            ds_invoice = self.apply_digital_signature(cr, uid, factura)
            
        return True

    def action_einvoice_send_receipt(self, cr, uid, ids, context=None):
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
