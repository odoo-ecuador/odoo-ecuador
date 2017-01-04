# -*- coding: utf-8 -*-
##############################################################################
#
#    Organización Territorial del Estado Module - Ecuador
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
    'name' : 'OpenERP OTE for Ecuador',
    'version' : '0.1.0',
    'author' : 'VIRTUALSAI CIA. LTDA.',
    'category': 'Localization',
    'complexity': 'normal',
    'website': 'http://www.virtualsami.com.ec',
    'data': [
        'view/country_view.xml',
        'data/res.country.state.csv',
        'data/res.country.city.csv',
        'data/res_country.xml',
        'security/ir.model.access.csv',
    ],
    'depends' : [
      'base'
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
