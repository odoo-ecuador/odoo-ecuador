# -*- coding: utf-8 -*-

import logging
import urllib
import urllib2

from openerp import api, models, fields

_logger = logging.getLogger(__name__)

STDNUM__ge__1_0 = False
try:
    import stdnum
    try:
        from stdnum import ec
        STDNUM__ge__1_0 = True
    except ImportError:
        _logger.warning(
            'l10n_ec_partner: required library version stdnum >= 1.0 found: %s',
            stdnum.__version__)
except ImportError:
    _logger.warning(
        'l10n_ec_partner: required library not found: stdnum >= 1.0')

SRI_URL = 'https://declaraciones.sri.gob.ec/facturacion-internet/consultas/publico/ruc-datos2.jspa'  # noqa


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):  # noqa
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            ids = self.search(cr, uid, [('vat', operator, name)] + args, limit=limit, context=context)  # noqa
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)  # noqa
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    ced_ruc = fields.Char(
        'Cedula/RUC', compute='_compute_ced_ruc', inverse='_inverse_ced_ruc',
        help='Identificación o Registro Unico de Contribuyentes.',
        deprecated=True)
    type_ced_ruc = fields.Selection([
        ('cedula', 'CEDULA'),
        ('ruc', 'RUC'),
        ('pasaporte', 'PASAPORTE')
    ], string='Tipo ID')
    tipo_persona = fields.Selection([
        ('6', 'Persona Natural'),
        ('9', 'Persona Juridica')
    ], string='Persona', required=True, default='9')
    is_company = fields.Boolean(default=True)

    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + ['type_ced_ruc']

    @api.multi
    def check_vat(self):
        for rec in self.filtered(lambda r: r.vat):
            if not super(ResPartner, rec.with_context(
                    type_ced_ruc=rec.type_ced_ruc)).check_vat():
                return False
        return True

    @api.multi
    def _construct_constraint_msg(self):
        return super(ResPartner, self)._construct_constraint_msg()

    _constraints = [(check_vat, _construct_constraint_msg, ['vat'])]

    @api.multi
    @api.depends('vat')
    def _compute_ced_ruc(self):
        for rec in self:
            rec.ced_ruc = rec.vat

    @api.multi
    def _inverse_ced_ruc(self):
        for rec in self:
            rec.vat = rec.ced_ruc

    @api.model
    def simple_vat_check(self, country_code, vat_number):
        ctx = self.env.context

        if country_code.upper() == 'EC' and ctx.get('type_ced_ruc'):
            vat_number = '%%(%s)s%s' % (ctx['type_ced_ruc'], vat_number) % {
                'cedula': 'C', 'ruc': 'R', 'pasaporte': 'P'}

        return super(ResPartner, self).simple_vat_check(country_code, vat_number)  # noqa

    def check_vat_ec(self, vat):
        """ Validación del Nº de Cédula/Ruc para Ecuador. """
        if len(vat) < 2:
            return False

        type_ced_ruc, vat = vat[0].upper(), vat[1:]

        if not STDNUM__ge__1_0:
            # No podemos validar, avisamos en los logs
            _logger.warning('Unable to validate VAT %s', vat)
            return True
        elif type_ced_ruc == 'C':  # Cédula de Identidad
            return ec.ci.is_valid(vat)
        elif type_ced_ruc == 'R':  # Registro Único de Contribuyentes
            return ec.ruc.is_valid(vat)
        elif type_ced_ruc == 'P':  # Pasaporte
            return True  # TODO

        return False

    def validate_from_sri(self):
        """
        TODO
        """
        SRI_LINK = "https://declaraciones.sri.gob.ec/facturacion-internet/consultas/publico/ruc-datos1.jspa"  # noqa
        texto = '0103893954'  # noqa

    @api.multi
    def sri_vat_check(self, country_code, vat_number):
        """ TODO: Valida mediante el Servicio de Rentas Internas. """
        req = urllib2.Request(SRI_URL, urllib.urlencode({
            'accion': 'siguiente',
            'ruc': vat_number,
            'lineasPagina': ''
        }))
        try:
            urllib2.urlopen(req)  # 200
            return True
        except urllib2.HTTPError:  # 500
            return False


class ResCompany(models.Model):
    _inherit = 'res.company'

    ruc_contador = fields.Char('Ruc del Contador', size=13)
    cedula_rl = fields.Char('Cédula Representante Legal', size=10)
