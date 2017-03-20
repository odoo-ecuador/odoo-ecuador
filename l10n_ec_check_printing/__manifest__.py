# -*- coding: utf-8 -*-
# © 2016 Cristian Salamea <cristian.salamea@ayni.com.ec>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Impresion de Cheques para Ecuador',
    'version': '10.0.0.1.0',
    'author': 'Cristian Salamea',
    'category': 'Accounting',
    'complexity': 'normal',
    'website': 'www.ayni.com.ec',
    'license': 'AGPL-3',
    'data': [
        'views/report_check_pacifico.xml',
        'views/reports.xml',
        'views/account_view.xml'
    ],
    'depends': [
        'account_check_printing',
    ]
}
