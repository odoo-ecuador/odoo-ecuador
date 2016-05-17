# -*- coding: utf-8 -*-

{
    'name': 'Accounting for Ecuador',
    'version': '4',
    "category": 'Generic Modules/Accounting',
    'depends': [
        'l10n_ec_authorisation', 'report_webkit',
        ],
    'author': 'Cristian Salamea.',
    'description': '''
Contabilidad para Ecuador
=========================
    Documentos de retenciones, liquidaciones de compra, ATS
    ''',
    'website': 'http://www.ayni.com.ec',
    'update_xml': [
        'invoice_workflow.xml',
        'withdrawing_view.xml',
        'withdrawing_report.xml',
        'retention_wizard.xml',
        'data/account.fiscal.position.csv'
    ],
    'installable': True,
}
