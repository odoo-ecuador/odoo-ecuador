# -*- coding: utf-8 -*-
{
    'name': 'Electronic Documents for Ecuador',
    'version': '10.0.0.1.0',
    'author': 'Cristian Salamea',
    'category': 'Localization',
    'license': 'AGPL-3',
    'complexity': 'normal',
    'data': [
        'security/ir.model.access.csv',
        'data/data_einvoice.xml',
        'data/account.epayment.csv',
        'edi/einvoice_edi.xml',
        'views/einvoice_view.xml',
        'views/partner_view.xml',
        'views/report_einvoice.xml',
        'views/edocument_layouts.xml',
    ],
    'depends': [
        'l10n_ec_withholding',
    ]
}
