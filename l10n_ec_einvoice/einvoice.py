# -*- coding: utf-8 -*-

import os
import time
import logging
import itertools

from jinja2 import Environment, FileSystemLoader

from openerp import models, api
from openerp.exceptions import Warning

from . import utils
from .xades.sri import DocumentXML
from .xades.xades import Xades


class AccountInvoice(models.Model):

    _name = 'account.invoice'
    _inherit = ['account.invoice', 'account.edocument']
    __logger = logging.getLogger('account.edocument')

    def _info_factura(self, invoice):
        """
        """
        company = invoice.company_id
        partner = invoice.partner_id
        infoFactura = {
            'fechaEmision': time.strftime('%d/%m/%Y',
                                          time.strptime(invoice.date_invoice,
                                                        '%Y-%m-%d')),
            'dirEstablecimiento': company.street2,
            'obligadoContabilidad': 'SI',
            'tipoIdentificacionComprador': utils.tipoIdentificacion[partner.type_ced_ruc],  # noqa
            'razonSocialComprador': partner.name,
            'identificacionComprador': partner.ced_ruc,
            'totalSinImpuestos': '%.2f' % (invoice.amount_untaxed),
            'totalDescuento': '0.00',
            'propina': '0.00',
            'importeTotal': '{:.2f}'.format(invoice.amount_pay),
            'moneda': 'DOLAR'
        }
        if company.company_registry:
            infoFactura.update({'contribuyenteEspecial':
                                company.company_registry})

        totalConImpuestos = []
        for tax in invoice.tax_line:
            if tax.tax_group in ['vat', 'vat0', 'ice', 'other']:
                totalImpuesto = {
                    'codigo': utils.codigoImpuesto[tax.tax_group],
                    'codigoPorcentaje': utils.tarifaImpuesto[tax.tax_group],
                    'baseImponible': '{:.2f}'.format(tax.base_amount),
                    'valor': '{:.2f}'.format(tax.tax_amount)
                    }
                totalConImpuestos.append(totalImpuesto)

        infoFactura.update({'totalConImpuestos': totalConImpuestos})
        return infoFactura

    def _detalles(self, invoice):
        """
        """
        def fix_chars(code):
            special = [
                [u'%', ' '],
                [u'º', ' '],
                [u'Ñ', 'N'],
                [u'ñ', 'n']
            ]
            for f, r in special:
                code = code.replace(f, r)
            return code

        detalles = []
        for line in invoice.invoice_line:
            detalle = {
                'codigoPrincipal': fix_chars(line.product_id.default_code),
                'descripcion': fix_chars(line.name),
                'cantidad': '%.6f' % (line.quantity),
                'precioUnitario': '%.6f' % (line.price_unit),
                'descuento': '0.00',
                'precioTotalSinImpuesto': '%.2f' % (line.price_subtotal)
             }
            impuestos = []
            for tax_line in line.invoice_line_tax_id:
                if tax_line.tax_group in ['vat', 'vat0', 'ice', 'other']:
                    impuesto = {
                        'codigo': utils.codigoImpuesto[tax_line.tax_group],
                        'codigoPorcentaje': utils.tarifaImpuesto[tax_line.tax_group],  # noqa
                        'tarifa': tax_line.porcentaje,
                        'baseImponible': '{:.2f}'.format(line.price_subtotal),
                        'valor': '{:.2f}'.format(line.price_subtotal *
                                                 tax_line.amount)
                    }
                    impuestos.append(impuesto)
            detalle.update({'impuestos': impuestos})
            detalles.append(detalle)
        return {'detalles': detalles}

    def render_document(self, invoice, access_key, emission_code):
        tmpl_path = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tmpl_path))
        einvoice_tmpl = env.get_template('einvoice.xml')
        data = {}
        data.update(self._info_tributaria(invoice, access_key, emission_code))
        data.update(self._info_factura(invoice))
        data.update(self._detalles(invoice))
        einvoice = einvoice_tmpl.render(data)
        return einvoice

    def render_authorized_einvoice(self, autorizacion):
        tmpl_path = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tmpl_path))
        einvoice_tmpl = env.get_template('authorized_einvoice.xml')
        auth_xml = {
            'estado': autorizacion.estado,
            'numeroAutorizacion': autorizacion.numeroAutorizacion,
            'ambiente': autorizacion.ambiente,
            'fechaAutorizacion': str(autorizacion.fechaAutorizacion.strftime("%d/%m/%Y %H:%M:%S")),  # noqa
            'comprobante': autorizacion.comprobante
        }
        auth_invoice = einvoice_tmpl.render(auth_xml)
        return auth_invoice

    @api.multi
    def action_generate_einvoice(self):
        """
        Metodo de generacion de factura electronica
        TODO: usar celery para enviar a cola de tareas
        la generacion de la factura y envio de email
        """
        for obj in self:
            if obj.type not in ['out_invoice', 'out_refund']:
                print "no disponible para otros documentos"
                continue
            self.check_date(obj.date_invoice)
            self.check_before_sent()
            access_key, emission_code = self._get_codes(name='account.invoice')  # noqa
            if obj.type == 'out_invoice':
                einvoice = self.render_document(obj, access_key, emission_code)
                inv_xml = DocumentXML(einvoice, 'out_invoice')
                inv_xml.validate_xml()
                xades = Xades()
                file_pk12 = obj.company_id.electronic_signature
                password = obj.company_id.password_electronic_signature
                signed_document = xades.sign(einvoice, file_pk12, password)
                ok, errores = inv_xml.send_receipt(signed_document)
                if not ok:
                    raise Warning('Errores', errores)
                auth, m = inv_xml.request_authorization(access_key)
                if not auth:
                    msg = ' '.join(list(itertools.chain(*m)))
                    raise Warning('Error', msg)
                auth_einvoice = self.render_authorized_einvoice(auth)
                self.update_document(auth, [access_key, emission_code])
                self.add_attachment(auth_einvoice, auth)
            else:
                # Revisar codigo que corre aca
                if not obj.origin:
                    raise Warning('Error de Datos',
                                  u'Sin motivo de la devolución')
                inv_ids = self.search([('number', '=', obj.name)])
                factura_origen = self.browse(inv_ids)
                # XML del comprobante electrónico: factura
                factura = self._generate_xml_refund(obj, factura_origen, access_key, emission_code)  # noqa
                # envío del correo electrónico de nota de crédito al cliente
                self.send_mail_refund(obj, access_key)

    @api.multi
    def invoice_print(self):
        # Método para imprimir reporte de liquidacion de compra
        datas = {'ids': [self.id], 'model': 'account.invoice'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_einvoice',
            'model': 'account.invoice',
            'datas': datas,
            'nodestroy': True,
            }
