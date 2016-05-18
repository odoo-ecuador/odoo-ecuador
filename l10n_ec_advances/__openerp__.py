# -*- coding: utf-8 -*-
{
    'name': 'Advances Payment for Customers/Suppliers',
    'author': 'Cristian Salamea',
    'website': 'http://www.ayni.com.ec',
    'category': 'Generic Modules/Accounting',
    'version': '1.0',
    'depends': ['account_voucher'],
    'description': '''
    This module allows make Advances Payments for Suppliers register
    allow reconciliation with invoices
    ''',
    'update_xml': [
        'account_advances_view.xml',
        'account_advances_report.xml',
    ],
    'installable': True,
}
