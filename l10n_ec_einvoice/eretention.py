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
import StringIO

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
from .xades.sri import SriService, DocumentXML
from .xades.xades import Xades

try:
    from suds.client import Client
    from suds.transport import TransportError
except ImportError:
    raise ImportError('Instalar Libreria suds')

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
    'other': '6',
}

codigoRetencionIVA = {
    '10': '9',
    '20': '10',
    '30': '1',
    '70': '2',
    '100': '3',
    '0': '7',
}

codigoRetencionISD = {
    '5': '4580',
}

class account_retention(osv.osv):
    
    _inherit = 'account.retention'
    __logger = logging.getLogger(_inherit)
    
    _columns = {
        'access_key': fields.char('Clave de Acceso', size=49, readonly=True),
        'authorization_number': fields.char('Número de Autorización', size=49, readonly=True),
        'authorization_status': fields.char('Estado de Autorización', size=64, readonly=True),
        'authorization_date':  fields.datetime('Fecha de Autorización', readonly=True),
        'authorization_sri': fields.boolean('¿Autorizado SRI?', readonly=True),
        'security_code': fields.char('Código de Seguridad', size=8)
        'environment_code': fields.char('Ambiente', size=10, readonly=True),
        'emission_code': fields.char('Emisión', size=16, readonly=True),
        }
        
    def _get_tax_element(self, retention, access_key, emission_code):
        """
        """
        company = retention.company_id
        auth = retention.invoice_id.journal_id.auth_ret_id
        infoTributaria = etree.Element('infoTributaria')
        etree.SubElement(infoTributaria, 'ambiente').text = SriService.get_env_prod()
        etree.SubElement(infoTributaria, 'tipoEmision').text = emission_code
        etree.SubElement(infoTributaria, 'razonSocial').text = company.name
        if company.tradename:
            etree.SubElement(infoTributaria, 'nombreComercial').text = company.tradename
        etree.SubElement(infoTributaria, 'ruc').text = company.partner_id.ced_ruc
        if access_key:
            etree.SubElement(infoTributaria, 'claveAcceso').text = access_key
        else:
            raise osv.except_osv(u'Error', u'La Clave de Acceso no puede ser nula')
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
        if company.street2:
            etree.SubElement(infoCompRetencion, 'dirEstablecimiento').text = company.street2
        if company.company_registry:
            etree.SubElement(infoCompRetencion, 'contribuyenteEspecial').text = company.company_registry
        etree.SubElement(infoCompRetencion, 'obligadoContabilidad').text = 'SI'
        etree.SubElement(infoCompRetencion, 'tipoIdentificacionSujetoRetenido').text = tipoIdentificacion[partner.type_ced_ruc]
        etree.SubElement(infoCompRetencion, 'razonSocialSujetoRetenido').text = utils.remove_special_characters(partner.name)
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
                etree.SubElement(impuesto, 'codigoRetencion').text = codigoRetencionIVA[line.percent]
            else:
                etree.SubElement(impuesto, 'codigoRetencion').text = line.name[0:5].replace('-', '').strip()                
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
        
     def get_access_key(self, cr, uid, retention):
        auth = retention.invoice_id.journal_id.auth_ret_id
        ld = retention.date.split('-')
        ld.reverse()
        fecha = ''.join(ld)
        #
        tcomp = auth.type_id.code
        ruc = retention.company_id.partner_id.ced_ruc
        serie = '{0}{1}'.format(auth.serie_entidad, auth.serie_emision)
        numero = retention.name[6:15]
        tipo_emision = retention.company_id.emission_code
        codigo_numero = retention.security_code
        access_key = (
            [fecha, tcomp, ruc],
            [serie, numero, codigo_numero, tipo_emision]
            )
        return access_key

    def action_generate_eretention(self, cr, uid, ids, context=None):
        """
        """
        WAIT_FOR_RECEIPT = 3

        for obj in self.browse(cr, uid, ids):
            # Clave de acceso
            ak_temp = self.get_access_key(cr, uid, obj)
            access_key = SriService.create_access_key(ak_temp)
            emission_code = obj.company_id.emission_code
            # Move write
            if emission_code == '1'
                self.write(cr, uid, [obj.id], {'access_key': access_key, 'emission_code': 'NORMAL'})
            else:
                self.write(cr, uid, [obj.id], {'access_key': access_key, 'emission_code': 'INDISPONIBILIDAD'})
            # XML del comprobante electrónico: retención
            comprobanteRetencion = self._generate_xml_retention(obj, access_key, emission_code) 
            # validación del XML
            doc_xml = DocumentXML(comprobanteRetencion, 'retention')
            doc_xml.validate_xml()
            # firma de xml
            xades = Xades()
            file_pk12 = obj.company_id.electronic_signature
            password = obj.company_id.password_electronic_signature
            signed_document = xades.apply_digital_signature(comprobanteRetencion, file_pk12, password)
            # recepción del comprobante electrónico
            send_result, m = doc_xml.send_receipt(signed_document)
            if not send_result:
                raise osv.except_osv(u'Error', m)
            time.sleep(WAIT_FOR_RECEIPT)            
            # solicitud de autorización del comprobante electrónico
            auth_xml, m, auth = doc_xml.request_authorization(access_key)
            if auth_xml:
                # envío del correo electrónico del documento al cliente
                self.send_mail_retention(cr, uid, obj, auth_xml, auth, access_k$
            else:
                raise osv.except_osv(u'Error', m)                    
        return True
        
    def send_mail_retention(self, cr, uid, obj, xml_element, auth, access_key, context):
         self.write(cr, uid, [obj.id], {
            'authorization_number': auth.numeroAutorizacion,
            'authorization_status': auth.estado,
            'authorization_date': auth.fechaAutorizacion.strftime("%d/%m/%Y %H:%M:%S"),
            'authorization_sri': True,
            'environment_code': auth.ambiente,
        })
        eretention_xml = etree.tostring(xml_element, pretty_print=True, encoding='utf-8')
        buf = StringIO.StringIO()
        buf.write(eretention_xml)
        eretention = base64.encodestring(buf.getvalue())
        buf.close()
        attachment_id = self.pool.get('ir.attachment').create(cr, uid,
            {
                'name': '{0}.xml'.format(access_key),
                'datas': eretention,
                'datas_fname': '{0}.xml'.format(access_key),
                'res_model': self._name,
                'res_id': obj.id,
                'type': 'binary'
            }, context=context)

        email_template_obj = self.pool.get('email.template')
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'l10n_ec_withdrawing', 'email_template_edi_retention')[1]
        email_template_obj.write(cr, uid, template_id, {'attachment_ids': [(6, 0, [attachment_id])]})
        email_template_obj.send_mail(cr, uid, template_id, obj.id, True)

        return True
