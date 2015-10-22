# -*- coding: utf-8 -*-  # pylint: disable=C0111
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

{  # pylint: disable=W0104
    'name': 'SRI Authorisation Documents',
    'version': '0.1.0',
    'author': 'Cristian Salamea',
    'category': 'Localization',
    'complexity': 'normal',
    'website': 'http://www.ayni.com.ec',
    'data': [
        'view/authorisation_view.xml',
        'data/account.ats.doc.csv',
        'data/account.ats.sustento.csv'
    ],
    'depends': [
        'l10n_ec_partner',
        'account'
    ],
    'test': [
    ],
    'installable': True,
}
