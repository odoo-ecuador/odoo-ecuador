# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Fábrica de Software Libre (www.libre.ec)
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
    'name': 'Instalador - Localización Ecuatoriana',
    'version': '8.0.1.0.0',
    'category': 'Generic Modules/Tools',
    'summary': 'Instalador de la localización Ecuatoriana',
    'description': """

Este módulo tiene la finalidad de ayudar a la instalación inicial de la localización ecuatoriana.

Luego de instalarlo debes ir a:

--> Configuraciones --> Configuraciones --> Para Ecuador.

Su uso es intuitivo, selecciona los casilleros de las funcionalidades que desee instalar y luego presiona "Aplicar".

    """,

    'author': "Fábrica de Software Libre",
    'website': "www.libre.ec",

    'category': 'Herramientas',
    'version': '0.01',

    'images': [
    ],

    'depends': [
        'base_setup'
    ],
    'data': [
        'views/res_config_views.xml',
    ],
    'demo': [
    ],

    'test': [
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
