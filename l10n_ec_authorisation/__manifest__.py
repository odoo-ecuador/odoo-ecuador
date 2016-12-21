# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Establecimientos y autorizaciones del SRI',
    'version': '0.1.0.0.0',
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
    ]
}
