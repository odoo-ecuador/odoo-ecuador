# -*- coding: utf-8 -*-  # pylint: disable=C0111

import time

from odoo.tests.common import TransactionCase


class TestAuthorisation(TransactionCase):
    """
    Prueba de documentos de autorizacion
    """
    def setUp(self):
        super(TestAuthorisation, self).setUp()
        self.Authorisation = self.env['account.authorisation']
        self.Partner = self.env['res.partner']
        self.AtsDoc = self.env['account.ats.doc']

    def test_create(self):
        type_id = self.AtsDoc.create(
            {
                'code': '01',
                'name': 'FACTURA'
            }
        )

        partner_id = self.Partner.create(
            {
                'identifier': '0103893962',
                'name': 'CRISTIAN GONZALO SALAMEA MALDONADO',
                'type_identifier': 'cedula',
                'tipo_persona': '6'
            }
        )

        auth_id = self.Authorisation.create(
            {
                'name': '0123456789',
                'serie_entidad': '001',
                'serie_emision': '001',
                'num_start': 1000,
                'num_end': 3000,
                'expiration_date': time.strftime('%Y-%m-%d'),
                'in_type': 'interno',
                'type_id': type_id,
                'partner_id': partner_id
            }
        )

        self.assertEquals(auth_id.name, '0123456789')
