# -*- coding: utf-8 -*-
##############################################################################
#
#    Organización Territorial del Estado Module - Ecuador	
#    Copyright (C) 2014-Today Jonathan Finlay <jfinlay@riseup.net>.
#    Copyright (C) 2015-Today VIRTUALSAMI CIA. LTDA. <alcides@virtualsami.com.ec>
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

class CountryCity(osv.osv):
    _name = 'res.country.city'
    _description = "City model"

    _columns = {
        'country_id': fields.many2one('res.country', 'Country',
                                      required=True),
        'state_id': fields.many2one('res.country.state', 'State',
                                    domain="[('country_id','=',country_id)]",
                                    required=True),
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=4, required=True),
    }

