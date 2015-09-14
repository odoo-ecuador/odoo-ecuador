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

from openerp import models, fields

class Company(models.Model):
    _inherit = 'res.company'
    
    electronic_signature = fields.Char('Firma Electrónica', size=128, required=True)
    password_electronic_signature = fields.Char('Clave Firma Electrónica', size=128, required=True)
    emission_code = fields.Selection([('1','Normal'),
                                      ('2','Indisponibilidad')],
                                      string='Tipo de Emisión',
                                      required=True,
                                      default='1')
    contingency_key_ids = fields.One2many('res.company.contingency.key','company_id', string='Claves de Contingencia', help='Claves de contingencia relacionadas con esta empresa.'),

class CompanyContingencyKey(models.Model):
    _name = 'res.company.contingency.key'
    _description = 'Clave de Contingencia'
    
    def _get_company(self, cr, uid, context):
        if context.get('company_id', False):
            return context.get('company_id')
        else:
            user = self.pool.get('res.users').browse(cr, uid, uid)
            return user.company_id.id
            
    key = fields.Char(string='Clave', size=37, required=True)
    used = fields.Boolean(string='¿Utilizada?',
                          readonly=True,
                          default=False)
    company_id = fields.Many2one('res.company', string='Empresa', required=True, default='_get_company')
    
    _sql_constraints = [
        ('key_unique', 'unique(key)', u'Clave de contingencia asignada debe ser única.'),
        ]