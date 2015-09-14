# -*- encoding: utf-8 -*-

from openerp import models, api, _
from openerp.exceptions import Warning

class res_partner(models.Model):
    _inherit = "res.partner"

    @api.one
    @api.constrains('vat', 'parent_id', 'company_id')
    def check_vat_unique(self):
        if not self.vat:
            return True

        # get first parent
        parent = self
        while parent.parent_id:
            parent = parent.parent_id

        same_vat_partners = self.search([
            ('vat', '=', self.vat),
            ('vat', '!=', False),
            ('company_id', '=', self.company_id.id),
            ])

        if same_vat_partners:
            related_partners = self.search([
                ('id', 'child_of', parent.id),
                ('company_id', '=', self.company_id.id),
                ])
            same_vat_partners = self.search([
                ('id', 'in', same_vat_partners.ids),
                ('id', 'not in', related_partners.ids),
                ('company_id', '=', self.company_id.id),
                ])
            if same_vat_partners:
                raise Warning(_(
                    'Cada cliente o proveedor debe tener un número de identificación único a menos que estén relacionados. Los terceros que tienen el mismo número y no están relacionados son: %s!') % (', '.join(x.name for x in same_vat_partners)))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
