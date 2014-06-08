from openerp.tests.common import TransactionCase

class PartnerTest(TransactionCase):

    def setUp(self):
        super(PartnerTest, self).setUp()
        self.Partner = self.registry('res.partner')

    def test_create(self):
        cursor = self.cr
        user_id = self.uid
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
        self.assertNotEquals(partner_id, 0)

