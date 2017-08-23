# -*- coding: utf-8 -*-

{
    'name': 'OpenERP Partner for Ecuador',
    'version': '8.0.1.0.0',
    'author': 'Cristian Salamea',
    'category': 'Localization',
    'complexity': 'normal',
    'website': 'http://www.ayni.com.ec',
    'external_dependencies': {
        'python': ['stdnum']
    },
    'depends': [
        'base', 'base_vat'
    ],
    'data': [
        'view/partner_view.xml',
    ],
    'installable': True,
}
