# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ecuador - Taxes',
    'version': '9.0.1.0.0',
    'category': 'Accounting',
    'author': 'Cristian Salamea',
    'website': 'http://www.ayni.com.ec',
    'license': 'AGPL-3',
    'depends': [
        'l10n_ec_chart',
    ],
    'data': [
        'data/account.tax.group.csv',
        'data/account.tax.csv',
        'data/account.fiscal.position.csv'
    ],
    'installable': False,
}
