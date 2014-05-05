# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Cristian Salamea.
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

{
    'name' : 'SRI Authorisation Documents',
    'version' : '0.1.0',
    'author' : 'Cristian Salamea',
    'category': 'Localization',
    'complexity': 'normal',
    'website': 'http://www.ayni.io',
    'data': [
#        'security/ir.model.access.csv',
        'view/authorisation_view.xml',
#        'report/l10n_ec_authorisation_report.xml',
#        'data/l10n_ec_authorisation_data.xml',
    ],
    'depends' : [
        'account'
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
