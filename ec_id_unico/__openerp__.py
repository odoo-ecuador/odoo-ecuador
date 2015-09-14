# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Evitar repetición del R.U.C.',
    'version': '8.0.1.0.0',
    'category': 'Utilidades',
    'description': """
R.U.C único para terceros
==================
Se agrega una restricción para evitar duplicaciones del número de identificación en terceros, excepto en empresas con relación padre/hijo. Basado en el código del módulo partner_vat_unique de ADHOC S.A. www.adhoc.com.ar """,

    'author':  'Fábrica de Software Libre',
    'website': 'www.libre.ec',
    'images': [
    ],
    'depends': [
        'base'
    ],
    'data': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
