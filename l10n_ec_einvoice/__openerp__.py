# -*- coding: utf-8 -*-
{
    'name': 'Electronic Documents for Ecuador',
    'version': '0.1.0',
    'author': 'Cristian Salamea',
    'category': 'Localization',
    'complexity': 'normal',
    'data': [
        'einvoice_report.xml',
        'edi/einvoice_edi.xml',
        'data/data_einvoice.xml',
        'data/account.epayment.csv',
        'views/einvoice_view.xml',
        'views/partner_view.xml',
        'views/report_einvoice.xml',
    ],
    'depends': [
        'report_webkit',
        'l10n_ec_withholding',
    ],
    'description': '''
    This module allows generate Electronic Documents for Ecuador
    ''',
}
