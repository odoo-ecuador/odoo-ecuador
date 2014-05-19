# -*- coding: utf-8 -*-

import logging

from osv import osv, fields
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProjectTask(osv.osv):
    _inherit = 'project.task'

    _columns = {
        'budget_ids': fields.one2many('budget.item',
                                      'task_id',
                                      string='Presupuesto'),
        'amount_budget': fields.float('Total Presupuesto',
                                      digits_compute=dp.get_precision('Budget'))
        }

        
