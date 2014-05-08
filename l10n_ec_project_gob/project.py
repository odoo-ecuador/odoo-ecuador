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

from osv import osv, fields


class ProjectType(osv.Model):
    """
    Tipos de proyectos que definen propiedades por defecto
    """
    _name = 'project.type'
    _description = 'Tipos de Proyectos'
    _order = 'name DESC'

    _columns = dict(
        code = fields.char('Código', size=12, required=True),
        name = fields.char('Tipo de Proyecto', size=64, required=True, select=True),
        properties_ids = fields.one2many('project.property', 'type_id',
                                         string="Propiedades por Tipo de Proyecto"),
#        kpi_ids = fields.one2many('project.kpi', 'project_type_id', string='Indicadores'),
        )


class ProjectEstrategy(osv.osv):

    _name = 'project.estrategy'
    _description = 'Lista de Estrategias'

    _columns = dict(
        sequence = fields.char('Prioridad', size=16, required=True),
        name = fields.char('Estrategia', size=128, required=True),
        axis_id = fields.many2one('project.axis', 'Eje Estratégico', required=True)
        )


class ProjectAxis(osv.osv):

    _name = 'project.axis'
    _description = 'Ejes Estrategicos'

    _columns = dict(
        name = fields.char('Eje Estratégico', size=64, required=True),
        legal_base = fields.text('Objetivo'),
        )

class ProjectProgram(osv.osv):

    _name = 'project.program'
    _description = 'Buscar Programas'

    def onchange_estrategy(self, cr, uid, ids, estrategy_id):
        """
        Metodo que devuelve el eje segun la estrategia seleccionada
        """
        res = {'value': {'axis_id': ''}}
        if estrategy_id:
            estrat = self.pool.get('project.estrategy').read(cr, uid, estrategy_id, ['axis_id'])
            res['value']['axis_id'] = estrat['axis_id']
        return res
        
    _columns = dict(
        sequence = fields.char('Código', size=32, required=True),
        name = fields.char('Programa', size= 64, required=True),
        estrategy_id = fields.many2one('project.estrategy',
                                  string='Estrategia',
                                  required=True),
        axis_id = fields.related('estrategy_id', 'axis_id', relation='project.axis',
                                 type='many2one', string='Eje Estratégico',
                                 readonly=True, store=True),
        description = fields.text('Descripción'),
        )

class ProjectProject(osv.osv):
    _inherit = 'project.project'
    __logger = logging.getLogger(_inherit)    
    STATES = {'open':[('readonly',False)]}

    _columns = {
        'axis_id': fields.many2one('project.axis',
                                   string='Eje',
                                   required=True,
                                   readonly=True, states=STATES),
        'estrategy_id': fields.many2one('project.estrategy',
                                        string='Estrategia',
                                        required=True,
                                        readonly=True, states=STATES),
        'program_id': fields.many2one('project.program',
                                      string='Programa',
                                      required=True,
                                      readonly=True, states=STATES)
        'background': fields.text('Antecendentes',
                                 required=True,
                                 readonly=True,
                                 states=STATES),
        'justification': fields.text('Justificación',
                                    required=True,
                                    readonly=True, states=STATES),
        'general_objective': fields.text('Objetivo General',
                                        required=True,
                                        readonly=True,
                                        states=STATES),
        'specific_objectives': fields.text('Objetivos Específicos',
                                          required=True,
                                          readonly=True,
                                          states=STATES),
        'type_id': fields.many2one('project.type', 'Tipo de Proyecto',
                                    required=True,
                                    readonly=True,
                                    states=STATES)                                          
        }
