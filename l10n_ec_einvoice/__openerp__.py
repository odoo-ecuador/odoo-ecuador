# -*- coding: utf-8 -*-
{
    'name': 'Electronic Documents for Ecuador',
    'version': '0.1.0',
    'author': 'Cristian Salamea',
    'category': 'Localization',
    'complexity': 'normal',
    'data': [
        'edi/einvoice_edi.xml',
        'data/data_einvoice.xml',
        'views/einvoice_view.xml',
        'views/partner_view.xml',
        'views/report_einvoice.mako',
        'einvoice_report.xml'
    ],
    'depends': [
        'report_webkit',
        'l10n_ec_withdrawing',
    ],
    'description': '''
    This module allows generate Electronic Documents for Ecuador
    ''',
}
