# -*- coding: utf-8 -*-
##############################################################################
#
#    Partner Module - Ecuador
#    Copyright (C) 2015 VIRTUALSAMI CIA. LTDA. All Rights Reserved
#    alcides@virtualsami.com.ec
#    Copyright (C) 2015 FABRICA DE SOFTWARE LIBRE. All Rights Reserved
#    desarrollo@libre.ec
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

from openerp import fields, models

class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    tradename = fields.Char('Nombre Comercial', size=300)
    ruc_contador = fields.Char('Ruc del Contador', size=13)
    cedula_rl = fields.Char('Cédula Representante Legal', size=10)