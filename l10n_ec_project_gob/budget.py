# -*- coding: utf-8 -*-

from osv import osv, fields


class AccountBudgetPost(osv.osv):
    _inherit = 'account.budget.post'

    _order = 'code'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for record in self.read(cr, uid, ids, ['id', 'code', 'name'], context):
            res.append((record['id'], '%s - %s' % (record['code'], record['name'])))
        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        """
        Redefinición de método para permitir buscar por el código
        """
        ids = []
        ids = self.search(cr, uid,
                          ['|',('code',operator,name),('name',operator,name)] + args,
                          context=context,
                          limit=limit)
        return self.name_get(cr, uid, ids, context)    

    _columns = {
        'type': fields.selection([('view','Vista'),
                                  ('normal','Normal')],
                                 string='Tipo', required=True),
        }

class CrossoveredBdugetLines(osv.osv):
    _inherit = 'crossovered.budget.lines'

    _columns = {
        'task_id': fields.many2one('project.task',
                                   string='Actividad',
                                   required=True),
        'code': fields.char('Código', size=16),
        'name': fields.char('Detalle', size=256, required=True),
        'state': fields.selection([('draft','Draft'),
                                   ('cancel', 'Cancelled'),
                                   ('confirm','Confirmed'),
                                   ('validate','Validated'),
                                   ('done','Done')], 'Estado',
                                   select=True,
                                   required=True,
                                   readonly=True)
        }

    _defaults = {
        'state': 'draft'
        }


class ProjectTask(osv.osv):
    _inherit = 'project.task'

    _columns = {
        'budget_ids': fields.one2many('crossovered.budget.lines',
                                      'task_id', 'Presupuesto')
        }

        
