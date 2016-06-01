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
    'version': '0.1',
    'depends': [
        'l10n_ec_partner',
        'point_of_sale'
    ],
    'data': [
        'views.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml'
        ],
}
