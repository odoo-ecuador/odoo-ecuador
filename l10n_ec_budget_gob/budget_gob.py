# -*- coding: utf-8 -*-

import logging
import time

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

DP = dp.get_precision('Budget')


class BudgetBudget(osv.osv):
    """
    Implementacion de clase de Presupuesto
    """
    _name = 'budget.budget'
    _order = 'code'

    _columns = {
        'code': fields.char('Código', size=64, required=True),
        'name': fields.char('Presupuesto', size=128, required=True),
        'department_id': fields.many2one('hr.department',
                                         string='Departamento',
                                         required=True),
        'date_start': fields.date('Fecha Inicio', required=True),
        'date_end': fields.date('Fecha Fin', required=True),
        'state': fields.selection(
            [('draft','Borrador'),
            ('open','Ejecución'),
            ('close','Cerrado')],
            string='Estado',
            required=True,
            readonly=True
        ),
        'budget_lines': fields.one2many('budget.item', 'budget_id', 'Detalle de Presupuesto')
        }

    _defaults = {
        'state': 'draft'
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
                                   ('confirmed','Confirmed'),
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
        'task_id': fields.many2one('project.task',
                                   string='Actividad',
                                   required=True),                                     
        'planned_amount': fields.float('Asignación Inicial', digits_compute=DP),
        }

    _defaults = {
        'state': 'draft'
        }
        


class BudgetCertificate(osv.Model):
    """
    This class implement certificate budget to make sure
    the process in al budget levels.
    """
    _name = 'budget.certificate'
    _inherit = ['mail.thread']    
    _description = 'Certificados Presupuestarios'
    
    __logger = logging.getLogger(_name)    
    _order = 'date DESC'
    
    DP = dp.get_precision('Budget')
    STATES_VALUE = {'draft': [('readonly', False)]}

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        for r in self.browse(cr, uid, ids, context):
            number = '/'
            if r.state in ['request','certified']:
                number = r.name
            elif r.state == 'commited':
                number = r.number
            res.append((r.id, number))
        return res

    def unlink(self, cr, uid, ids, context):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state not in ['draft']:
                raise osv.except_osv('Error', 'No se permite eliminar registros.')
        return super(BudgetCertificate, self).unlink(cr, uid, ids, context)

    def set_sequence(self, cr, uid, ids, sequence='request'):
        """
        Asigna el numero de secuencia para el documento.
        """
        seq_obj = self.pool.get('ir.sequence')
        number = seq_obj.get(cr, uid, 'budget.certificate.%s'%sequence)
        field = 'name'
        if not number:
            raise osv.except_osv('Error', 'No ha configurado la secuencia para este documento.')
        if sequence == 'commited':
            field = 'number'
        self.write(cr, uid, ids, {field: number})
        return True

    def _get_user(self, cr, uid, context=None):
        return uid

    def _get_certificate_lines(self, cr, uid, ids, context):
        res = {}
        for obj in self.pool.get('budget.certificate.line').browse(cr, uid, ids, context):
            res[obj.certificate_id.id] = True
        return res.keys()

    def _amount_total(self, cr, uid, ids, fields, args, context):
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'amount_total': 0,
                           'amount_certified': 0,
                           'amount_commited': 0}
            for line in obj.line_ids:
                res[obj.id]['amount_total'] += line.amount
                res[obj.id]['amount_certified'] += line.amount_certified
                res[obj.id]['amount_commited'] += line.amount_commited
        return res

    def _compute_budget(self, cr, uid, ids, fields, args, context):
        """
        Metodo de calculo de total devengado para el compromiso
        presupuestario utilizado en las facturas 'invoice_ids'
        """
        res = {}
        for obj in self.browse(cr, uid, ids, context):
            res[obj.id] = {'amount_accured': 0,
                           'amount_paid': 0}
            for inv in obj.invoice_ids:
                res[obj.id]['amount_accured'] += inv.amount_pay
        return res

    STORE_VAR = {'budget.certificate': (lambda self, cr, uid, ids, c={}: ids, ['line_ids'], 10),
                 'budget.certificate.line': (
                     _get_certificate_lines,
                    ['amount','amount_certified','amount_commited','budget_id','state'],
                     10)}

    _columns = dict(
        name = fields.char('Nro. de Solicitud',
                           size=32, required=True,
                           readonly=True),
        number = fields.char('Número de Compromiso', readonly=True, size=16),
        notes = fields.text('Notas',
                            readonly=True, states=STATES_VALUE),
        user_id = fields.many2one('res.users', string='Solicitante',
                                  required=True, readonly=True),
        department_id = fields.many2one('hr.department', 'Dirección / Coordinación',
                                        required=True, readonly=False),
        state = fields.selection([('draft', 'Borrador'),
                                  ('request', 'Solicitado'),
                                  ('certified', 'Certificado'),
                                  ('commited', 'Comprometido'),
                                  ('anulado', 'Anulado'),                                  
                                  ('cancel', 'Rechazado')],
                                 string='Estado',
                                 required=True),
        budget_type = fields.selection([('corriente','CORRIENTE'),
                                   ('inversion','INVERSION'),
                                   ('general','GENERAL'),
                                   ('ogastos','OTROS GASTOS (CORRIENTE)'),
                                   ('opublica','OBRAS PUBLICAS (INVERSION)'),
                                   ('ginversion', 'GASTOS DE INVERSION'),
                                   ('tranf','TRANSF. DE INVERSION'),
                                   ('bienesld','BIENES DE LARGA DURACION (INVERSION)')],
                                  string='Aplicacion Presupuestaria.'),
        date = fields.datetime('Fecha de Emisión', required=True,
                               readonly=True),
        date_confirmed = fields.date('Fecha de Certificación',
                                     readonly=True),
        date_commited = fields.date('Fecha de Compromiso',
                                    readonly=True, states={'certified': [('readonly',False)]}),
        project_id = fields.many2one('project.project',
                                     string='Proyecto',
                                     required=True,
                                     readonly=True,
                                     states=STATES_VALUE),
        partner_id = fields.many2one('res.partner', 'Proveedor',
                                     domain=[('supplier','=',True)],
                                     readonly=False, states={'certified': [('readonly', False)]}),
        line_ids = fields.one2many('budget.certificate.line',
                                   'certificate_id', 'Detalle'),
        amount_total = fields.function(_amount_total, string='Total Solicitado', method=True,
                                       digits_compute=DP, multi='request', store=STORE_VAR),
        amount_certified = fields.function(_amount_total, string='Total Certificado', method=True,
                                       digits_compute=DP, multi='request', store=STORE_VAR),
        amount_commited = fields.function(_amount_total, string='Total Comprometido', method=True,
                                       digits_compute=DP, multi='request', store=STORE_VAR),
        )

    def _check_requests(self, cr, uid, ids, context=None):
        """
        Validacion de montos solicitados
        {'partida': monto, 'disponible': monto}
        """
        for obj in self.browse(cr, uid, ids, context):
            if obj.project_id.type_budget == 'ingreso':
                return True
            if not obj.state == 'draft':
                return True
            lista = []
            res = []
            budget = False
            for line in obj.line_ids:
                budget_id = line.budget_line_id.id
                if budget_id != budget:
                    res = [0,line.budget_line_id.available_amount]
                    lista.append(res)
                    budget = budget_id
                res[0] += line.amount
        return True

    def _check_partner(self, cr, uid, ids):
        """
        Verifica que el documento tenga asignado un proveedor
        """
        for obj in self.browse(cr, uid, ids):
            if obj.project_id.type_budget == 'ingreso':
                return True
            if obj.state == 'commited' and not obj.employee_id and not obj.partner_id:
                raise osv.except_osv('Error', 'No ha ingresado un proveedor en el documento.')
            if obj.state=='commited' and not obj.date_commited:
                raise osv.except_osv('Error', 'No ha ingresado la fecha de compromiso.')
        return True

    _defaults = dict(
        name = '/',
        user_id = lambda self, cr, uid, context: uid,
        state = 'draft',
        date = time.strftime('%Y-%m-%d %H:%M:%S'),
        )

    def action_request(self, cr, uid, ids, context=None):
        """
        TODO:
        """
        if context is None:
            context = {}
        line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            lines = [line.id for line in obj.line_ids]
            if not lines:
                raise osv.except_osv('Alerta', 'No ha ingresado el detalle del documento.')
            line_obj.write(cr, uid, lines, {'state': 'request'})
        self.set_sequence(cr, uid, ids, sequence='request')
        self.write(cr, uid, ids, {'state': 'request', 'date': time.strftime('%Y-%m-%d %H:%M:%S')})
        self.__logger.info("Prespuesto referencial emitido")
        return True    

    def action_certified(self, cr, uid, ids, context=None):
        """
        Accion de confirmación de la solicitud de presupuesto
        referencial
        """
        line_obj = self.pool.get('budget.certificate.line')
        if context is None:
            context = {}        
        data = {'state': 'certified',
                'date_confirmed': time.strftime('%Y-%m-%d')}
        for obj in self.browse(cr, uid, ids, context):
            line_ids = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, line_ids, {'state': 'certified'})
        self.write(cr, uid, ids, data)
        return True

    def action_print_report(self, cr, uid, ids, context=None):
        """
        :action to print report
        """
        if context is None:
            context = {}
        report_name = 'crossovered.request'
        certificate = self.browse(cr, uid, ids, context)[0]
        datas = {'ids': [certificate.id], 'model': 'budget.certificate'}
        if context.get('reprint'):
            datas.update({'watermark': True})
        if context.get('compromiso'):
            report_name = 'crossovered.compromise'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'model': 'crossovered.budget.certificate',
            'datas': datas,
            'nodestroy': True,                        
            }

    def action_commited(self, cr, uid, ids, context=None):
        """
        Metodo que compromete el presupuesto referencial
        """
        line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            line_ids = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, line_ids, {'state': 'commited'})
            self.write(cr, uid, obj.id, {'state': 'commited', 'date_commited': time.strftime('%Y-%m-%d')})
        return True        

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            lines = [line.id for line in obj.line_ids]
            line_obj.write(cr, uid, lines, {'state':'cancel'})
        self.write(cr, uid, ids, {'state': 'cancel'})
        self.__logger.info("Presupuesto referencial anulado")
        return True

    def action_anular(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            lines = [line.id for line in obj.line_ids]
            line_obj.change_state(cr, uid, lines, 'anulado')
        self.write(cr, uid, ids, {'state': 'anulado'})            
        return True


class BudgetCertificateLine(osv.osv):

    _name = 'budget.certificate.line'

    _columns = {
        'certificate_id': fields.many2one(
            'budget.certificate',
            string='Certificado',
            ondelete='cascade'
        ),
        'project_id': fields.many2one(
            'project.project',
            string='Proyecto',
            required=True
        ),
        'task_id': fields.many2one(
            'project.task',
            string='Actividad',
            required=True
        ),
        'budget_id': fields.many2one(
            'budget.item',
            string='Partida',
            required=True
        ),
        'amount': fields.float('Monto Solicitado',
                               digits_compute=DP),
        'amount_certified': fields.float('Monto Certificado',
                                         digits_compute=DP),
        'amount_commited': fields.float('Monto Comprometido',
                                        digits_compute=DP),
        'state':  fields.selection(
            [('draft', 'Borrador'),
            ('request', 'Solicitado'),
            ('certified', 'Certificado'),
            ('commited', 'Comprometido'),
            ('anulado', 'Anulado'),                                  
            ('cancel', 'Rechazado')],
            string='Estado',
            required=True
        ),
        }

    _defaults = {
        'state': 'draft'
        }

