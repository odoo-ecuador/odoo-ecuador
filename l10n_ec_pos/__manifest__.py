# -*- coding: utf-8 -*-
{
    'name': "l10n_ec_pos",
    'summary': """
    Cambios en el POS para Ecuador
    """,
    'description': """
        Agregar campos del partner requeridos en el POS
    """,
    'author': "Cristian Salamea",
    'website': "http://www.ayni.com.ec",
    'category': 'POS',
    'version': '10.0.0.0.0',
    'depends': [
        'point_of_sale',
        'l10n_ec_authorisation'
    ],
    'data': [
        'data/pos.xml',
        'views.xml'
    ],
    'qweb': [
        'static/src/xml/l10n_ec_pos.xml',
        'static/src/xml/pos.xml'
    ]
}
