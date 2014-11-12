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
    'name' : 'E-Invoicing',
    'version' : '0.1.0',
    'author' : 'Cristian Salamea',
    'category': 'Account',
    'complexity': 'normal',
    'website': 'www.ayni.io',
    'data': [
        'security/l10n_ec_einvoice_security.xml',
        'security/ir.model.access.csv',
        'view/l10n_ec_einvoice_view.xml',
        'report/l10n_ec_einvoice_report.xml',
        'data/l10n_ec_einvoice_data.xml',
    ],
    'depends' : [
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