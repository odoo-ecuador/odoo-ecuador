# -*- coding: utf-8 -*-  # pylint: disable=C0111

from openerp.tests.common import TransactionCase  # pylint: disable=F0401

import time


class TestAuthorisation(TransactionCase):  # pylint: disable=W0232
    """
    Prueba de documentos de autorizacion
    """
    def setUp(self):
        super(TestAuthorisation, self).setUp()
        self.Authorisation = self.registry('account.authorisation')
        self.Partner = self.registry('res.partner')
        self.AtsDoc = self.registry('account.ats.doc')

    def test_create(self):
        cursor = self.cr
        user_id = self.uid

        type_id = self.AtsDoc.create(
            cursor,
            user_id,
            {
                'code': '06',
                'name': 'FACTURA'
            }
        )

        partner_id = self.Partner.create(
            cursor,
            user_id,
            {
                'ced_ruc': '0103893962',
                'name': 'CRISTIAN GONZALO SALAMEA MALDONADO',
                'type_ced_ruc': 'cedula',
                'tipo_persona': '6'
            }
        )

        auth_id = self.Authorisation.create(
            cursor,
            user_id,
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

        self.assertNotEquals(auth_id, 0)
