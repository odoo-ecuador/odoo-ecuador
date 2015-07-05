# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2015 Cristian Salamea All Rights Reserved
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
    'name' : 'Accounting for Ecuador',
    'version' : '3',
    "category": 'Generic Modules/Accounting',
    'depends' : ['l10n_ec_authorisation', 'report_webkit',
        ],
    'author' : 'Cristian Salamea.',
    'description': '''
    Accounting for Ecuador, retention docuements
    ''',
    'website': 'http://www.invbox.com.ec',
    'update_xml': [
        'invoice_workflow.xml',
        'withdrawing_view.xml',
        'withdrawing_report.xml',
        'retention_wizard.xml',
        'data/account.fiscal.position.csv'
    ],
    'installable': True,
    'active': False,
}
