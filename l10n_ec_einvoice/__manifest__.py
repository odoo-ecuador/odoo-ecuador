# -*- coding: utf-8 -*-
{
    'name': 'Electronic Documents for Ecuador',
    'version': '10.0.0.0.0',
    'author': 'Cristian Salamea',
    'category': 'Localization',
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
    ],
    'description': '''
    This module allows generate Electronic Documents for Ecuador
    '''
}
