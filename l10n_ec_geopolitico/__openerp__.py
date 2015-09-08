# -*- coding: utf-8 -*-
{
    'name': "Contribuyentes de Ecuador",

    'summary': """Información de contribuyentes en Ecuador""",

    'description': """
Introduce las modificaciones en res.partner necesarias para que el modelo se ajuste a los requerimientos de las normativas ecuatorianas.
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
	'data/l10n_ec_contribuyentes.canton.csv',
#	'data/l10n_ec_contribuyentes.parroquia.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
