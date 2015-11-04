# -*- coding: utf-8 -*-
##############################################################################
#
#    Extension of Point of Sale Module - Ecuador
#    Copyright (C) 2015-Today VIRTUALSAMI CIA. LTDA. <alcides@virtualsami.com.ec>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Extension of Point of Sale',
    'version': '0.1',
    'category': 'Point of sale',
    'author': 'VIRTUALSAMI CIA. LTDA.',
    'website': 'http://www.virtualsami.com.ec/',
    'summary': 'Extension of Point of Sale for Ecuador',
    'description': """
	    Agregar campos del partner requeridos en el POS
    """,
    'depends': [
        'point_of_sale', 
        'l10n_ec_partner',
    ],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
