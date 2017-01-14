# -*- coding: utf-8 -*-  # pylint: disable=C0111

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
        type_doc = self.AtsDoc.create(
            {
                'code': '01',
                'name': 'FACTURA'
            }
        )

        partner = self.Partner.create(
            {
                'identifier': '0103893962',
                'name': 'CRISTIAN GONZALO SALAMEA MALDONADO',
                'type_identifier': 'cedula',
                'tipo_persona': '6'
            }
        )

        auth = self.Authorisation.create(
            {
                'name': '0123456789',
                'serie_entidad': '001',
                'serie_emision': '001',
                'num_start': 1000,
                'num_end': 3000,
                'expiration_date': '2018-12-31',
                'in_type': 'interno',
                'type_id': type_doc.id,
                'partner_id': partner.id
            }
        )

        self.assertEquals(auth.name, '0123456789')

    def test_is_valid(self):
        type_doc = self.AtsDoc.create(
            {
                'code': '01',
                'name': 'FACTURA'
            }
        )

        partner = self.Partner.create(
            {
                'identifier': '2490005261001',
                'name': 'CRISTIAN GONZALO SALAMEA MALDONADO',
                'type_identifier': 'ruc',
                'tipo_persona': '6'
            }
        )
        auth = self.Authorisation.create(
            {
                'name': '0123456781',
                'serie_entidad': '001',
                'serie_emision': '001',
                'num_start': 1000,
                'num_end': 3000,
                'expiration_date': '2018-12-31',
                'in_type': 'externo',
                'type_id': type_doc.id,
                'partner_id': partner.id
            }
        )
        res = auth.is_valid_number(1500)
        self.assertEquals(res, True)
        res = auth.is_valid_number(4500)
        self.assertEquals(res, False)

    def test_unlink(self):
        type_doc = self.AtsDoc.create(
            {
                'code': '01',
                'name': 'FACTURA'
            }
        )

        partner = self.Partner.create(
            {
                'identifier': '1803433729',
                'name': 'CRISTIAN GONZALO SALAMEA MALDONADO',
                'type_identifier': 'cedula',
                'tipo_persona': '6'
            }
        )
        auth = self.Authorisation.create(
            {
                'name': '0123456871',
                'serie_entidad': '001',
                'serie_emision': '001',
                'num_start': 1000,
                'num_end': 3000,
                'expiration_date': '2018-12-31',
                'in_type': 'externo',
                'type_id': type_doc.id,
                'partner_id': partner.id
            }
        )
        res = auth.unlink()
        self.assertEquals(res, True)
