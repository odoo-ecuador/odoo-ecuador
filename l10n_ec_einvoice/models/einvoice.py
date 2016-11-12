# -*- coding: utf-8 -*-

import os
import time
import logging
import itertools

from jinja2 import Environment, FileSystemLoader

from openerp import models, api
from openerp.exceptions import Warning

from . import utils
from ..xades.sri import DocumentXML
from ..xades.xades import Xades


class AccountInvoice(models.Model):

    _name = 'account.invoice'
    _inherit = ['account.invoice', 'account.edocument']
    _logger = logging.getLogger('account.edocument')
    TEMPLATES = {
        'out_invoice': 'out_invoice.xml',
        'out_refund': 'out_refund.xml'
    }

    def _info_factura(self, invoice):
        """
        """
        def fix_date(date):
            d = time.strftime('%d/%m/%Y',
                              time.strptime(date, '%Y-%m-%d'))
            return d

        company = invoice.company_id
        partner = invoice.partner_id
        infoFactura = {
            'fechaEmision': fix_date(invoice.date_invoice),
            'dirEstablecimiento': company.street2,
            'obligadoContabilidad': 'SI',
            'tipoIdentificacionComprador': utils.tipoIdentificacion[partner.type_ced_ruc],  # noqa
            'razonSocialComprador': partner.name,
            'identificacionComprador': partner.ced_ruc,
            'totalSinImpuestos': '%.2f' % (invoice.amount_untaxed),
            'totalDescuento': '0.00',
            'propina': '0.00',
            'importeTotal': '{:.2f}'.format(invoice.amount_pay),
            'moneda': 'DOLAR',
            'formaPago': invoice.epayment_id.code,
            'valorRetIva': '{:.2f}'.format(invoice.taxed_ret_vatsrv+invoice.taxed_ret_vatb),  # noqa
            'valorRetRenta': '{:.2f}'.format(invoice.amount_tax_ret_ir)
        }
        if company.company_registry:
            infoFactura.update({'contribuyenteEspecial':
                                company.company_registry})

        totalConImpuestos = []
        for tax in invoice.tax_line:
            if tax.tax_group in ['vat', 'vat0', 'ice']:
                totalImpuesto = {
                    'codigo': utils.tabla17[tax.tax_group],
                    'codigoPorcentaje': utils.tabla18[tax.percent],
                    'baseImponible': '{:.2f}'.format(tax.base_amount),
                    'tarifa': tax.percent,
                    'valor': '{:.2f}'.format(tax.tax_amount)
                    }
                totalConImpuestos.append(totalImpuesto)

        infoFactura.update({'totalConImpuestos': totalConImpuestos})

        if self.type == 'out_refund':
            inv = self.search([('number', '=', self.origin)], limit=1)
            inv_number = '{0}-{1}-{2}'.format(inv.invoice_number[:3], inv.invoice_number[3:6], inv.invoice_number[6:])  # noqa
            notacredito = {
                'codDocModificado': inv.auth_inv_id.type_id.code,
                'numDocModificado': inv_number,
                'motivo': self.name,
                'fechaEmisionDocSustento': fix_date(inv.date_invoice),
                'valorModificacion': self.amount_total
            }
            infoFactura.update(notacredito)
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
            codigoPrincipal = line.product_id and \
                line.product_id.default_code and \
                fix_chars(line.product_id.default_code) or '001'
            priced = line.price_unit * (1 - (line.discount or 0.00) / 100.0)
            discount = (line.price_unit - priced) * line.quantity
            detalle = {
                'codigoPrincipal': codigoPrincipal,
                'descripcion': fix_chars(line.name.strip()),
                'cantidad': '%.6f' % (line.quantity),
                'precioUnitario': '%.6f' % (line.price_unit),
                'descuento': '%.2f' % discount,
                'precioTotalSinImpuesto': '%.2f' % (line.price_subtotal)
            }
            impuestos = []
            for tax_line in line.invoice_line_tax_id:
                if tax_line.tax_group in ['vat', 'vat0', 'ice']:
                    impuesto = {
                        'codigo': utils.tabla17[tax_line.tax_group],
                        'codigoPorcentaje': utils.tabla18[tax_line.porcentaje],  # noqa
                        'tarifa': tax_line.porcentaje,
                        'baseImponible': '{:.2f}'.format(line.price_subtotal),
                        'valor': '{:.2f}'.format(line.price_subtotal *
                                                 tax_line.amount)
                    }
                    impuestos.append(impuesto)
            detalle.update({'impuestos': impuestos})
            detalles.append(detalle)
        return {'detalles': detalles}

    def _compute_discount(self, detalles):
        total = sum([float(det['descuento']) for det in detalles['detalles']])
        return {'totalDescuento': total}

    def render_document(self, invoice, access_key, emission_code):
        tmpl_path = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(tmpl_path))
        einvoice_tmpl = env.get_template(self.TEMPLATES[self.type])
        data = {}
        data.update(self._info_tributaria(invoice, access_key, emission_code))
        data.update(self._info_factura(invoice))
        detalles = self._detalles(invoice)
        data.update(detalles)
        data.update(self._compute_discount(detalles))
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
                continue
            self.check_date(obj.date_invoice)
            self.check_before_sent()
            access_key, emission_code = self._get_codes(name='account.invoice')
            einvoice = self.render_document(obj, access_key, emission_code)
            inv_xml = DocumentXML(einvoice, obj.type)
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
            attach = self.add_attachment(auth_einvoice, auth)
            self.send_document(
                attachments=[a.id for a in attach],
                tmpl='l10n_ec_einvoice.email_template_einvoice'
            )

    def invoice_print(self, cr, uid, ids, context=None):
        datas = {'ids': ids, 'model': 'account.invoice'}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_einvoice',
            'model': 'account.invoice',
            'datas': datas,
            'nodestroy': True,
            }
