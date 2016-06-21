# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Accounting for Ecuador',
    'version': '4.0',
    "category": 'Generic Modules/Accounting',
    'depends': [
        'l10n_ec_authorisation',
        'l10n_ec_invoice_sequence'
    ],
    'author': 'Cristian Salamea.',
    'website': 'http://www.ayni.com.ec',
    'data': [
        'data/account.fiscal.position.csv',
        'security/ir.model.access.csv',
        'invoice_workflow.xml',
        'withdrawing_view.xml',
        'withdrawing_report.xml',
        'retention_wizard.xml'
    ],
    'installable': True,
}
