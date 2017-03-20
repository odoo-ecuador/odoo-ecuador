# -*- coding: utf-8 -*-
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    Copyright (C) 2016 Cristian Salamea <critian.salamea@gmail.com>
{
    'name': 'Manage Employee Contracts for Ecuador',
    'version': '10.0.0.1.0',
    'category': 'Generic Modules/Human Resources',
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>, "
    "Cristian Salamea <cristian.salamea@gmail.com>"
    "Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr_contract',
        'hr_holidays',
        'l10n_ec_hr_employee'
    ],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/hr_data.xml',
        'data/hr.contract.commision.csv',
        'data/hr.contract.branch.csv',
        'data/hr.contract.code.csv',
        'data/hr_contract_cron.xml',
        'data/hr_contract_data.xml',
        'view/hr_contract_view.xml',
        'view/hr_base.xml',
        'view/res_config_view.xml'
    ]
}
