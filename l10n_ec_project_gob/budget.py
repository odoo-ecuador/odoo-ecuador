# -*- coding: utf-8 -*-

from osv import osv, fields


class BudgetItem(osv.osv):
    _inherit = 'budget.item'

    _columns = {
        'task_id': fields.many2one('project.task',
                                   string='Actividad',
                                   required=True),
        }


class ProjectTask(osv.osv):
    _inherit = 'project.task'

    _columns = {
        'budget_ids': fields.one2many('budget.item',
                                      'task_id',
                                      string='Presupuesto')
        }

        
