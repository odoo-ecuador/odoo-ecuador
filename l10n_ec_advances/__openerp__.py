# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2009 GnuThink Software All Rights Reserved
#    info@gnuthink.com
#    $Id$
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
    'name' : 'Advances Payment for Customers/Suppliers',
    'author': 'Gnuthink Software Cia. Ltda.',
    'website': 'http://www.gnuthink.com',
    "category" : "Generic Modules/Accounting",    
    'version' : '1',
    'depends' : ['account_voucher'],
    'description': '''
    This module allows make Advances Payments for Suppliers register
    allow reconciliation with invoices
    ''',
    'init_xml': [],
    'update_xml': ['account_advances_view.xml',
                   'account_advances_report.xml',
                   ],
    'installable': True,
    'active': False,
}
