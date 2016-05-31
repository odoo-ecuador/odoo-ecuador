# -*- coding: utf-8 -*-

{
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
    'installable': True,
}
