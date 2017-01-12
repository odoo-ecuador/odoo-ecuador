# -*- coding: utf-8 -*-
# © <2016> <Alcides Rivera VIRTUALSAMI CIA LTDA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Ecuador - Accounting Chart',
    'version': '1.1',
    'category': 'Localization/Account Charts',
    'description': """
    This is the base module to manage
    the accounting chart for Ecuador in OpenERP.
    """,
    'author': 'Alcides Rivera',
    'depends': [
        'account',
        'account_chart',
    ],
    'data': [
        'account_chart.xml',
        'l10n_chart_ec_wizard.xml',
    ],
    'installable': True,
}
