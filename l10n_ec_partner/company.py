# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-Today Jonathan Finlay <jfinlay@riseup.net>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class Company(osv.osv):
    _name = "res.company"
    _inherit = "res.company"

    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        """ Read the 'address' functional fields. """
        return super(Company, self)._get_address_data(cr, uid, ids, field_names, arg, context=context)

    def _set_address_data(self, cr, uid, company_id, name, value, arg, context=None):
        """ Write the 'address' functional fields. """
        return super(Company, self)._set_address_data(cr, uid, company_id, name, value, arg, context=context)

    _columns = {
        'city': fields.function(_get_address_data, fnct_inv=_set_address_data,
                                type='many2one', domain="[('state_id', '=', state_id)]",
                                relation='res.country.city', string="City", multi='address'),
    }
