# -*- coding: utf-8 -*-
{
    'name': "NIIF Pymes - Ecuador",
    "category": 'Generic Modules/Accounting',
    'summary': """Plantilla de plan de cuentas para Ecuador""",

    'description': """
<p>Crea una plantilla con las cuentas contables del catálogo publicado por la Supercias. <br/>Se eliminan las cuentas que no son comunes (de Instituciones financieras, contructoras, químicas" pues estas se integrarán en módulos apartados a fin de permitir su instalación de forma selectiva.</p>
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

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}