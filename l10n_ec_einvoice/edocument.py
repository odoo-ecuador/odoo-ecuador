# -*- coding: utf-8 -*-

import base64
import StringIO
from datetime import datetime

from openerp import models, fields, api
from openerp.exceptions import Warning

from . import utils
from .xades.sri import SriService


class Edocument(models.AbstractModel):

    _name = 'account.edocument'

    clave_acceso = fields.Char(
        'Clave de Acceso',
        size=49,
        readonly=True
    )
    numero_autorizacion = fields.Char(
        'Número de Autorización',
        size=37,
        readonly=True
    )
    estado_autorizacion = fields.Char(
        'Estado de Autorización',
        size=64,
        readonly=True
    )
    fecha_autorizacion = fields.Datetime(
        'Fecha Autorización',
        readonly=True
    )
    ambiente = fields.Char(
        'Ambiente',
        size=64,
        readonly=True
    )
    autorizado_sri = fields.Boolean('¿Autorizado SRI?', readonly=True)
    security_code = fields.Char('Código de Seguridad', size=8)
    emission_code = fields.Char('Tipo de Emisión', size=1)

    def _info_tributaria(self, document, access_key, emission_code):
        """
        """
        company = document.company_id
        auth = False
        if document._name == 'account.invoice':
            auth = document.journal_id.auth_id
        elif document._name == 'account.retention':
            auth = document.invoice_id.journal_id.auth_ret_id
        infoTributaria = {
            'ambiente': SriService.get_active_env(),
            'tipoEmision': emission_code,
            'razonSocial': company.name,
            'nombreComercial': company.name,
            'ruc': company.partner_id.ced_ruc,
            'claveAcceso':  access_key,
            'codDoc': utils.tipoDocumento[auth.type_id.code],
            'estab': auth.serie_entidad,
            'ptoEmi': auth.serie_emision,
            'secuencial': getattr(self, 'number', document.name)[6:15],  # noqa
            'dirMatriz': company.street
        }
        return infoTributaria

    def get_code(self):
        code = self.env['ir.sequence'].get('edocuments.code')
        return code

    @api.multi
    def _get_codes(self, name='account.invoice'):
        ak_temp = self.get_access_key(name)
        access_key = SriService.create_access_key(ak_temp)
        emission_code = self.company_id.emission_code
        return access_key, emission_code

    def get_access_key(self, name):
        if name == 'account.invoice':
            auth = self.journal_id.auth_id
            ld = self.date_invoice.split('-')
        elif name == 'account.retention':
            auth = self.invoice_id.journal_id.auth_ret_id
            ld = self.date.split('-')
        ld.reverse()
        fecha = ''.join(ld)
        tcomp = utils.tipoDocumento[auth.type_id.code]
        ruc = self.company_id.partner_id.ced_ruc
        serie = '{0}{1}'.format(auth.serie_entidad, auth.serie_emision)
        numero = getattr(self, 'number', self.name)[6:15]
        codigo_numero = self.get_code()
        tipo_emision = self.company_id.emission_code
        access_key = (
            [fecha, tcomp, ruc],
            [serie, numero, codigo_numero, tipo_emision]
            )
        return access_key

    @api.multi
    def check_before_sent(self):
        """
        """
        NOT_SENT = u'No se puede enviar el comprobante electrónico al SRI'
        MESSAGE_SEQUENCIAL = ' '.join([
            u'Los comprobantes electrónicos deberán ser',
            u'enviados al SRI para su autorización en orden cronológico',
            'y secuencial. Por favor enviar primero el',
            ' comprobante inmediatamente anterior.'])
        FIELD = {
            'account.invoice': 'number',
            'account.retention': 'name'
        }
        number = getattr(self, 'number', self.name)
        sql = ' '.join([
            "SELECT autorizado_sri, %s FROM %s" % (FIELD[self._name], self._table),  # noqa
            "WHERE state='open' AND %s < '%s'" % (FIELD[self._name], number),  # noqa
            "ORDER BY %s DESC LIMIT 1" % FIELD[self._name]
        ])
        self.env.cr.execute(sql)
        res = self.env.cr.fetchone()
        if not res:
            return True
        auth, number = res
        if auth is None and number:
            raise Warning(NOT_SENT, MESSAGE_SEQUENCIAL)
        return True

    def check_date(self, date_invoice):
        """
        Validar que el envío del comprobante electrónico
        se realice dentro de las 24 horas posteriores a su emisión
        """
        LIMIT_TO_SEND = 5
        NOT_SENT = u'Error de Envío'
        MESSAGE_TIME_LIMIT = u' '.join([
            u'Los comprobantes electrónicos deben',
            u'enviarse con máximo 24h desde su emisión.']
        )
        dt = datetime.strptime(date_invoice, '%Y-%m-%d')
        days = (datetime.now() - dt).days
        if days > LIMIT_TO_SEND:
            raise Warning(NOT_SENT, MESSAGE_TIME_LIMIT)

    @api.multi
    def update_document(self, auth, codes):
        DATE_SRI = "%d/%m/%Y %H:%M:%S"
        self.write({
            'numero_autorizacion': auth.numeroAutorizacion,
            'estado_autorizacion': auth.estado,
            'ambiente': auth.ambiente,
            'fecha_autorizacion': auth.fechaAutorizacion.strftime(DATE_SRI),
            'autorizado_sri': True,
            'clave_acceso': codes[0],
            'emission_code': codes[1]
        })

    @api.one
    def add_attachment(self, xml_element, auth):
        buf = StringIO.StringIO()
        buf.write(xml_element.encode('utf-8'))
        document = base64.encodestring(buf.getvalue())
        buf.close()
        attach_id = self.env['ir.attachment'].create(  # noqa
            {
                'name': '{0}.xml'.format(self.clave_acceso),
                'datas': document,
                'datas_fname':  '{0}.xml'.format(self.clave_acceso),
                'res_model': self._name,
                'res_id': self.id,
                'type': 'binary'
            },
        )
        return True

    def render_document(self, document, access_key, emission_code):
        pass
