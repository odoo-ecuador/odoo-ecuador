# -*- coding: utf-8 -*-
# © <2016> <Alcides Rivera VIRTUALSAMI CIA LTDA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'OpenERP OTE for Ecuador',
    'version': '0.1.0',
    'author': 'VIRTUALSAMI CIA. LTDA.',
    'category': 'Localization',
    'complexity': 'normal',
    'website': 'http://www.virtualsami.com.ec',
    'data': [
        'view/country_view.xml',
        'data/res.country.state.csv',
        'data/res.country.city.csv',
        'data/res_country.xml',
        'security/ir.model.access.csv'
    ],
    'depends': [
        'base'
    ],
    'installable': False,
}
