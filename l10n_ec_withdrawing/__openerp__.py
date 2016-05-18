# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Accounting for Ecuador',
    'version': '4.0',
    "category": 'Generic Modules/Accounting',
    'depends': [
        'l10n_ec_authorisation',
        'report_webkit',
    ],
    'author': 'Cristian Salamea.',
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
