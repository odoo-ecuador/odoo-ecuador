# -*- coding: utf-8 -*-
{
    'name': "Ecuador Geopolítico",

    'summary': """Datos de provincias, cantones y parroquias de Ecuador.""",

    'description': """
Introduce las modificaciones en res.partner y e ingresa la información geopolítica de Ecuador.
- Se crean los modelos provincia (state), cantón y parroquia.
- Se ingresan las provincias, cantones y parroquias de Ecuador.
    """,

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Contable',
    'version': '0.02',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
    ],

    # always loaded 
    'data': [
	'views/res_partner_views.xml',
	'data/res.country.state.csv',
	'data/l10n_ec_geopolitico.canton.csv',
#	'data/l10n_ec_geopolitico.parroquia.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
