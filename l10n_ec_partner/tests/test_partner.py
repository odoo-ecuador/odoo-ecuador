# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class PartnerTest(TransactionCase):

    def setUp(self):
        super(PartnerTest, self).setUp()
        self.Partner = self.env['res.partner']

        self.partner_natural = self.Partner.create({
            'identifier': '0103893962',
            'name': 'CRISTIAN GONZALO SALAMEA MALDONADO',
            'type_identifier': 'cedula',
        })
        self.partner_juridico = self.Partner.create({
            'identifier': '0190416380001',
            'name': 'AYNI CONSULTING',
            'type_identifier': 'ruc'
        })

    def test_create(self):
        self.assertEquals(self.partner_natural.identifier, '0103893962')
        self.assertEquals(self.partner_juridico.identifier, '0190416380001')

    def test_search(self):
        res = self.Partner.search([('identifier', '=', '9999999999')], limit=1)
        self.assertEquals(res.name, 'CONSUMIDOR FINAL')
