# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    """
            ('vat', 'IVA Diferente de 0%'),
            ('vat0', 'IVA 0%'),
            ('novat', 'No objeto de IVA'),
            ('ret_vat_b', 'Retención de IVA (Bienes)'),
            ('ret_vat_srv', 'Retención de IVA (Servicios)'),
            ('ret_ir', 'Ret. Imp. Renta'),
            ('no_ret_ir', 'No sujetos a Ret. de Imp. Renta'),
            ('imp_ad', 'Imps. Aduanas'),
            ('imp_sbs', 'Super de Bancos'),
            ('ice', 'ICE'),
            ('other', 'Other')
    """

    code = fields.Char('Código')


class AccountTax(models.Model):

    _name = 'account.tax'
    _inherit = 'account.tax'
    _order = 'description ASC'
    _rec_name = 'description'

    porcentaje = fields.Char('% para Reportes', size=4)

    @api.v8
    def compute_all(self, price_unit, currency=None,
                    quantity=1.0, product=None, partner=None):
        """
        Redefinicion para revisar si necesitamos incluir el group
        en el return
        """
        return super(AccountTax, self).compute_all(
            price_unit, currency,
            quantity, product, partner)
