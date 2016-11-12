# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Retenciones para Ecuador',
    'version': '9.0.1.0.0',
    'category': 'Generic Modules/Accounting',
    'license': 'AGPL-3',
    'depends': [
        'l10n_ec_authorisation',
        'l10n_ec_tax',
        'web_action_conditionable'
    ],
    'author': 'Cristian Salamea.',
    'website': 'http://www.ayni.com.ec',
    'data': [
        'data/account.fiscal.position.csv',
        'security/ir.model.access.csv',
        'views/invoice_workflow.xml',
        'views/report_account_move.xml',
        'views/withholding_view.xml'
    ],
    'installable': True,
}
