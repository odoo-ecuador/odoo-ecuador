# -*- coding: utf-8 -*-
# © <2016> <Cristian Salamea>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Retenciones para Ecuador',
    'version': '4.0',
    "category": 'Generic Modules/Accounting',
    'depends': [
        'l10n_ec_authorisation',
        'l10n_ec_invoice_sequence'
    ],
    'description': """
Gestion Contable para Ecuador
==============================

Modulo para gestion de:

    * retenciones
    * Exportar ATS
    * liquidaciones de compra
    * codigos para formularios 103 y 104
    * Impreso de asiento contable

    """,
    'author': 'Cristian Salamea.',
    'website': 'http://www.ayni.com.ec',
    'data': [
        'data/account.fiscal.position.csv',
        'security/ir.model.access.csv',
        'invoice_workflow.xml',
        'views/report_account_move.xml',
        'withdrawing_view.xml',
        'withdrawing_report.xml',
        'retention_wizard.xml'
    ],
    'installable': True,
}
