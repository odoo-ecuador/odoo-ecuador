# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class PartnerTest(TransactionCase):

    def setUp(self):
        super(PartnerTest, self).setUp()
        self.Partner = self.env['res.partner']

    def test_create(self):
        partner = self.Partner.create(
            {
                'identifier': '0103893962',
                'name': 'CRISTIAN GONZALO SALAMEA MALDONADO',
                'type_identifier': 'cedula',
                'tipo_persona': '6'
            }
        )
        self.assertEquals(partner.identifier, '0103893962')
