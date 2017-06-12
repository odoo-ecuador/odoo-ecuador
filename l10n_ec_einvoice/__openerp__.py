# -*- coding: utf-8 -*-
#    Copyright (C) 2017 Cristian Salamea <cristian.salamea@gmail.com>
#    Copyright (C) 2017 Alcides Rivera VIRTUALSAMI CIA LTDA <alcides.rivera84@gmail.com>

{
    'name': 'Documentos Electrónicos para Ecuador',
    'version': '0.1.0',
    'author': "Cristian Salamea <cristian.salamea@gmail.com>, "
    "Alcides Rivera VIRTUALSAMI CIA LTDA <alcides.rivera84@gmail.com>",
    'category': 'Localization',
    'complexity': 'normal',
    'data': [
        'edi/einvoice_edi.xml',
        'data/data_einvoice.xml',
        'views/einvoice_view.xml',
        'views/partner_view.xml',
        'views/report_einvoice.mako',
        'einvoice_report.xml',
    ],
    'depends': [
        'report_webkit',
        'l10n_ec_withdrawing',
    ],
    'description': '''
    Este módulo permite generar Documentos Electrónicos para Ecuador
    ''',
}
