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
import os
import base64
import subprocess

from lxml import etree

from osv import osv, fields
from tools import config
from tools.translate import _
from tools import ustr
from xml.dom.minidom import parse, parseString

import decimal_precision as dp
import netsvc

try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError('Instalar Libreria suds')

from .xades.sri import Service as SRIService, InvoiceXML

tipoIdentificacion = {
    'ruc' : '04',
    'cedula' : '05',
    'pasaporte' : '06',
    'venta_consumidor_final' : '07',
    'identificacion_exterior' : '08',
    'placa' : '09',
}

codigoImpuestoRetencion = {
    'ret_ir': '1',
    'ret_vat_b': '2',
    'ret_vat_srv': '2',
    'ice': '3',
}

class account_retention(osv.osv):
    
    _inherit = 'account.retention'
    __logger = logging.getLogger(_inherit)
    
    _columns = {
        'access_key': fields.char('Clave de Acceso', size=49, readonly=True, store=True),
        'authorization_number': fields.char('Número de Autorización', size=37, readonly=True),
        'authorization_date':  fields.datetime('Fecha y Hora de Autorización', readonly=True),
        'authorization_sri': fields.boolean('¿Autorizado SRI?', readonly=True),
        'security_code': fields.char('Código de Seguridad', size=8)
        }
        
    def get_code(self, cr, uid, retention):
        """
        TODO: revisar la generacion
        del codigo de 8 digitos
        """
        return self.pool.get('ir.sequence').get_id(cr, uid, 71)
    
    def get_access_key(self, cr, uid, retention):
        auth = retention.invoice_id.journal_id.auth_ret_id
        ld = retention.date.split('-')
        ld.reverse()
        fecha = ''.join(ld)
        #
        tcomp = auth.type_id.code
        ruc = retention.company_id.partner_id.ced_ruc
        serie = '{0}{1}'.format(auth.serie_entidad, auth.serie_emision)
        numero = retention.name[6:15] # FIX w/ number
        tipo_emision = retention.company_id.emission_code
        codigo_numero = self.get_code(cr, uid, retention)
        access_key = (
            [fecha, tcomp, ruc],
            [serie, numero, codigo_numero, tipo_emision]
            )
        return access_key
        
    def _get_tax_element(self, retention, access_key, emission_code):
        """
        """
        company = retention.company_id
        auth = retention.invoice_id.journal_id.auth_ret_id
        infoTributaria = etree.Element('infoTributaria')
        etree.SubElement(infoTributaria, 'ambiente').text = SRIService.get_env_prod()
        etree.SubElement(infoTributaria, 'tipoEmision').text = emission_code
        etree.SubElement(infoTributaria, 'razonSocial').text = company.name
        etree.SubElement(infoTributaria, 'nombreComercial').text = company.name
        etree.SubElement(infoTributaria, 'ruc').text = company.partner_id.ced_ruc
        etree.SubElement(infoTributaria, 'claveAcceso').text = access_key
        etree.SubElement(infoTributaria, 'codDoc').text = auth.type_id.code
        etree.SubElement(infoTributaria, 'estab').text = auth.serie_entidad
        etree.SubElement(infoTributaria, 'ptoEmi').text = auth.serie_emision
        etree.SubElement(infoTributaria, 'secuencial').text = retention.name[6:15]
        etree.SubElement(infoTributaria, 'dirMatriz').text = company.street
        return infoTributaria
    
    def _get_retention_element(self, retention):
        company = retention.company_id
        partner = retention.invoice_id.partner_id
        infoCompRetencion = etree.Element('infoCompRetencion')
        etree.SubElement(infoCompRetencion, 'fechaEmision').text = time.strftime('%d/%m/%Y',time.strptime(retention.date, '%Y-%m-%d'))
        etree.SubElement(infoCompRetencion, 'dirEstablecimiento').text = company.street2
        if company.company_registry:
            etree.SubElement(infoCompRetencion, 'contribuyenteEspecial').text = company.company_registry
        etree.SubElement(infoCompRetencion, 'obligadoContabilidad').text = 'SI'
        etree.SubElement(infoCompRetencion, 'tipoIdentificacionSujetoRetenido').text = tipoIdentificacion[partner.type_ced_ruc]
        etree.SubElement(infoCompRetencion, 'razonSocialSujetoRetenido').text = partner.name
        etree.SubElement(infoCompRetencion, 'identificacionSujetoRetenido').text = partner.ced_ruc
        etree.SubElement(infoCompRetencion, 'periodoFiscal').text = retention.period_id.name
        return infoCompRetencion
        
    def _get_detail_element(self, retention):
        """
        """
        impuestos = etree.Element('impuestos')
        for line in retention.tax_ids:
            #Impuesto
            impuesto = etree.Element('impuesto')
            etree.SubElement(impuesto, 'codigo').text = codigoImpuestoRetencion[line.tax_group]
            if line.tax_group in ['ret_vat_b', 'ret_vat_srv']:
                if line.percent == '30':
                    etree.SubElement(impuesto, 'codigoRetencion').text = '1'
                elif line.percent == '70':
                    etree.SubElement(impuesto, 'codigoRetencion').text = '2'
                else:
                    etree.SubElement(impuesto, 'codigoRetencion').text = '3'
            else:
                etree.SubElement(impuesto, 'codigoRetencion').text = line.base_code_id.code
                
            etree.SubElement(impuesto, 'baseImponible').text = '%.2f' % (line.base)
            etree.SubElement(impuesto, 'porcentajeRetener').text = str(line.percent)
            etree.SubElement(impuesto, 'valorRetenido').text = '%.2f' % (abs(line.amount))
            etree.SubElement(impuesto, 'codDocSustento').text = retention.invoice_id.sustento_id.code
            etree.SubElement(impuesto, 'numDocSustento').text = line.num_document
            etree.SubElement(impuesto, 'fechaEmisionDocSustento').text = time.strftime('%d/%m/%Y',time.strptime(retention.invoice_id.date_invoice, '%Y-%m-%d'))
            impuestos.append(impuesto)
        return impuestos
        
    def _generate_xml_retention(self, retention, access_key, emission_code):
        """
        """
        comprobanteRetencion = etree.Element('comprobanteRetencion')
        comprobanteRetencion.set("id", "comprobante")
        comprobanteRetencion.set("version", "1.0.0")
        
        # generar infoTributaria
        infoTributaria = self._get_tax_element(retention, access_key, emission_code)
        comprobanteRetencion.append(infoTributaria)
        
        # generar infoCompRetencion
        infoCompRetencion = self._get_retention_element(retention)
        comprobanteRetencion.append(infoCompRetencion)
        
        #Impuestos
        impuestos = self._get_detail_element(retention)
        comprobanteRetencion.append(impuestos)
        
        return comprobanteRetencion
        
    def action_generate_eretention(self, cr, uid, ids, context=None):
        """
        """
        for obj in self.browse(cr, uid, ids):
            # Validar que el envío del comprobante electrónico se realice dentro de las 24 horas posteriores a su emisión
            if (datetime.now() - datetime.strptime(obj.date, '%Y-%m-%d')).days > 30:
                raise osv.except_osv(u'No se puede enviar el comprobante electrónico al SRI', u'Los comprobantes electrónicos deberán enviarse a las bases de datos del SRI para su autorización en un plazo máximo de 24 horas')
            else:
                # Validar que el envío de los comprobantes electrónicos sea secuencial
                auth = obj.invoice_id.journal_id.auth_ret_id
                numero = obj.name[6:15]
                numero_anterior = int(numero) - 1
                numero_comprobante_anterior = '{0}{1}{2}'.format(auth.serie_entidad, auth.serie_emision,str(numero_anterior).zfill(9))
                anterior_ids = self.pool.get('account.retention').search(cr, uid, [('name','=',numero_comprobante_anterior)])
                comprobante_anterior = self.browse(cr, uid, anterior_ids, context = context)
                if not comprobante_anterior[0].authorization_sri:
                    raise osv.except_osv(u'No se puede enviar el comprobante electrónico al SRI', u'Los comprobantes electrónicos deberán ser enviados al SRI para su autorización en orden cronológico y secuencial. Por favor enviar primero el comprobante inmediatamente anterior')
                else:
                    if not obj.access_key:
                        # Codigo de acceso
                        ak_temp = self.get_access_key(cr, uid, obj)
                        access_key = SRIService.create_access_key(ak_temp)
                        emission_code = obj.company_id.emission_code
                        self.write(cr, uid, [obj.id], {'access_key': access_key, 'emission_code': emission_code})
                    else:
                        access_key = obj.access_key
                        emission_code = obj.company_id.emission_code

                    # XML del comprobante electrónico: retención
                    comprobanteRetencion = self._generate_xml_retention(obj, access_key, emission_code)        
                    # Grabación del xml en el disco
                    tree = etree.ElementTree(comprobanteRetencion)
                    name = '%s%s.xml' %('/opt/retenciones/', access_key)
                    tree.write(name,pretty_print=True,xml_declaration=True,encoding='utf-8',method="xml")
                    # Firma electrónica del xml
                    firma_path = os.path.join(os.path.dirname(__file__), 'xades/firma/prctXadesBes.jar')
                    file_pk12 = obj.company_id.electronic_signature
                    password = obj.company_id.password_electronic_signature
                    # Invocación del jar de la firma electrónica
                    subprocess.call(['java', '-jar', firma_path, name, name, file_pk12, password])
        
                    cadena = open(name, mode='rb').read()
                    document = parseString(cadena.strip())
                    xml = document.toxml('UTF-8').encode('base64')
                    # Recepción de comprobantes electrónicos en el SRI
                    url = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
                    client = Client(url)
                    result =  client.service.validarComprobante(xml)
                    self.__logger.info("RecepcionComprobantes: %s" % result)
                    mensaje_error = ""
                    if (result[0] == 'DEVUELTA'):
                        # Recepción fallida: en caso de rechazo se envía el arreglo con los motivos
                        comprobante = result[1].comprobante
                        mensaje_error += 'Clave de Acceso: ' + comprobante[0].claveAcceso
                        mensajes = comprobante[0].mensajes
                        i = 0
                        mensaje_error += "\nErrores:\n"
                        while i < len(mensajes):
                            mensaje = mensajes[i]
                            mensaje_error += 'Identificador: ' + mensaje[i].identificador + '\nMensaje: ' + mensaje[i].mensaje + '\nTipo: ' + mensaje[i].tipo
                            i += 1
                        raise osv.except_osv('Error SRI', mensaje_error)
                    else:
                        # Recepción exitosa
                        self.write(cr, uid, obj.id, {'security_code': self.get_code(cr, uid, obj), 'access_key': access_key})
                        return {'warning':{'title':'Autorizado SRI', 'message':'Retención Autorizada por el SRI!'}}
                            
            return True
        
    def action_authorization_sri(self, cr, uid, ids, context=None):
        """
        """
        for obj in self.browse(cr, uid, ids):
            url = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'
            client_auto = Client(url)
            result_auto = client_auto.service.autorizacionComprobante(obj.access_key)
            self.__logger.info("AutorizacionComprobantes: %s" % result_auto)
            if result_auto[2] == '':
                raise osv.except_osv('Error SRI', 'No existe comprobante')
            else:
                autorizaciones = result_auto[2].autorizacion
                i = 0
                autorizado = False
                mensaje_error = ''
                while i < len(autorizaciones):
                    autorizacion = autorizaciones[i]
                    estado = autorizacion.estado
                    fecha_autorizacion = autorizacion.fechaAutorizacion

                    if (estado == 'NO AUTORIZADO'):                        
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
                    self.write(cr, uid, obj.id, {'authorization_sri': True, 'authorization_number': numero_autorizacion, 'authorization_date': fecha_autorizacion})
                    autorizacion_xml = etree.Element('autorizacion')
                    etree.SubElement(autorizacion_xml, 'estado').text = estado
                    etree.SubElement(autorizacion_xml, 'numeroAutorizacion').text = numero_autorizacion
                    etree.SubElement(autorizacion_xml, 'fechaAutorizacion').text = str(fecha_autorizacion.strftime("%d/%m/%Y %H:%M:%S"))
                    etree.SubElement(autorizacion_xml, 'comprobante').text = etree.CDATA(autorizacion.comprobante)
                            
                    tree = etree.ElementTree(autorizacion_xml)
                    name = '%s%s.xml' %('/opt/retenciones/', obj.access_key)
                    fichero = tree.write(name,pretty_print=True,xml_declaration=True,encoding='utf-8',method="xml")
                    
                    self.send_mail(cr, uid, obj, obj.access_key, context)
                else:
                    raise osv.except_osv('Error SRI', mensaje_error)
        return True

    def send_mail(self, cr, uid, obj, access_key, context):
        name = '%s%s.xml' %('/opt/retenciones/', access_key)
        cadena = open(name, mode='rb').read()
        attachment_id = self.pool.get('ir.attachment').create(cr, uid,
            {
                'name': '%s.xml' % (access_key),
                'datas': base64.b64encode(cadena),
                'datas_fname': '%s.xml' % (access_key),
                'res_model': self._name,
                'res_id': obj.id,
                'type': 'binary'
            }, context=context)

        email_template_obj = self.pool.get('email.template')
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'l10n_ec_withdrawing', 'email_template_edi_retention')[1]
        email_template_obj.write(cr, uid, template_id, {'attachment_ids': [(6, 0, [attachment_id])]})
        email_template_obj.send_mail(cr, uid, template_id, obj.id, True)

        return True
