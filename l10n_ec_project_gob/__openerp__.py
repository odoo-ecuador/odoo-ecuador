# -*- coding: utf-8 -*-
################################################################################
#                
#    l10n_project_gob module for OpenERP, Project Management for Gov in Ecuador
#    Copyright (C) 2014 Gnuthink Cia. Ltda. (<https://github.com/openerp-ecuador/openerp-ecuador>) 
#                
#    This file is a part of l10n_project_gob
#                
#    l10n_project_gob is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License v3 or later
#    as published by the Free Software Foundation, either version 3 of the 
#    License, or (at your option) any later version.
#                
#    l10n_project_gob is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License v3 or later for more details.
#                
#    You should have received a copy of the GNU Affero General Public License
#    v3 or later along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#                
#################################################################################
{
    'name': 'l10n_ec_project_gob',
    'version': '0.1',
    'category': 'Government',
    'description': """
    Project Management for Gov in Ecuador
    """,
    'author': 'Cristian Salamea',
    'website': 'https://github.com/openerp-ecuador/openerp-ecuador',
    'depends': ['hr',
                'project',
                'account_budget'],
    'data': [
        'security/security.xml',
        'view/menu.xml',
        'view/project_view.xml',
        'data/account.budget.post.csv'
    ],
    'test': [
    ],
    'demo': [
    ],
    'js': [
    ],
    'qweb' : [
    ],
    'css': [
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
    'license': 'AGPL-3',
}
