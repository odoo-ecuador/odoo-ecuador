# -*- coding: utf-8 -*-
##############################################################################
#
#    E-Invoice Module - Ecuador
#    Copyright (C) 2014 VIRTUALSAMI CIA. LTDA. All Rights Reserved
#    alcides@virtualsami.com.ec
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name' : 'Electronic Documents for Ecuador',
    'version': '0.1.0',
    'author': 'VIRTUALSAMI CIA. LTDA.',
    "category" : "Localization",
    'complexity' : 'normal',
    'website': 'http://www.virtualsami.com.ec',
    'data': [
        'einvoice_view.xml',
        'partner_view.xml',
        'einvoice_report.xml',
        'edi/einvoice_data.xml'
    ],
     'depends': [
        'l10n_ec_withdrawing'
    ],
    'update_xml': [
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'test': [
    ],
    'description': '''
    <p>Este módulo permite generar documentos electrónicos para Ecuador.</br>
    Requiere la instalación de la librería suds-jurko: </br>
    En debian/Ubuntu:</br>
    apt-get -y install python-pip</br>
    pip install suds-jurko</br>
    Si está utilizando la imagen docker-odoo-ecuador, la librería se encuentra instalada.</p>
    ''',
    'installable': True,
    'auto_install': False,
    'application': True,
}
