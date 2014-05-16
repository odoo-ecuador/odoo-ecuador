# -*- coding: utf-8 -*-

from osv import osv, fields


class BudgetBudget(osv.osv):
    """
    Implementacion de clase de Presupuesto
    """
    _name = 'budget.budget'

    _columns = {
        'code': fields.char('Código', size=64, required=True),
        'name': fields.char('Partida', size=128, required=True),
        'department_id': fields.many2one('hr.department',
                                         string='Departamento',
                                         required=True),
        'date_start': fields.date('Fecha Inicio', required=True),
        'date_end': fields.date('Fecha Fin', required=True),
        }


class BudgetPost(osv.osv):
    """
    Catalogo de Partidas
    """
    _name = 'budget.post'

    #TODO: parent_id

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
        'code': fields.char('Código', size=64, required=True),
        'name': fields.char('Partida', size=128, required=True),
        'type': fields.selection([('view','Vista'),
                                  ('normal','Normal')],
                                 string='Tipo', required=True),       
        }

        
class BudgetItem(osv.osv):
    """
    Instancia de una Partida
    """
    _name = 'budget.item'

    _columns = {
        'code': fields.char('Código', size=16),
        'name': fields.char('Detalle', size=256, required=True),
        'state': fields.selection([('draft','Draft'),
                                   ('cancel', 'Cancelled'),
                                   ('confirm','Confirmed'),
                                   ('validate','Validated'),
                                   ('done','Done')], 'Estado',
                                   select=True,
                                   required=True,
                                   readonly=True),
        'date_start': fields.date('Fecha Inicio'),
        'date_end': fields.date('Fecha Fin'),
        'budget_post_id': fields.many2one('budget.post', string='Partida',
                                          required=True),
        'budget_id': fields.many2one('budget.budget',
                                     string='Presupuesto',
                                     ondelete='cascade',
                                     select=True),
        'planned_amount': fields.float('Monto Planificado', digits=(16,2)),
        }

    _defaults = {
        'state': 'draft'
        }
        
