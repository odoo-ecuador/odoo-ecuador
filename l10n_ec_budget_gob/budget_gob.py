# -*- coding: utf-8 -*-

import logging
import time

from osv import osv, fields
import openerp.addons.decimal_precision as dp


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
        


class BudgetCertificate(osv.Model):
    """
    This class implement certificate budget to make sure
    the process in al budget levels.
    """
    
    _name = 'budget.certificate'
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
            elif r.state == 'compromised':
                number = r.number
            texto = ' '.join([number,' ', r.notes])
            texto = texto[:64]
            res.append((r.id, texto))
        return res

    def unlink(self, cr, uid, ids, context):
        for obj in self.browse(cr, uid, ids, context):
            if obj.state not in ['draft']:
                raise osv.except_osv('Error', 'No se permite eliminar registros.')
        return super(CrossoveredBudgetCertificate, self).unlink(cr, uid, ids, context)

    def create(self, cr, uid, vals, context=None):
        """
        Redefinición de metodo create de objeto para
        asignar una secuencia al documento
        """
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        seq_num = seq_obj.get(cr, uid, 'budget.certificate')
        if not seq_num:
            raise osv.except_osv('Error', 'No ha configurado la secuencia para este documento.')
        vals['name'] = seq_num
        res_id = super(CrossoveredBudgetCertificate, self).create(cr, uid, vals, context)
        return res_id

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
                res[obj.id]['amount_commited'] += line.amount_compromised
        return res

    def _get_invoices(self, cr, uid, ids, context):
        result = {}
        for obj in self.pool.get('account.invoice').browse(cr, uid, ids, context):
            result[obj.certificate_id.id] = True
        return result.keys()

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
                 'budget.certificate.line': (_get_certificate_lines,
                                                         ['amount','amount_certified','amount_compromised','budget_line_id','state'], 10)}
    STORE_INV = {'account.invoice': (_get_invoices, ['state'], 10),
                 'budget.certificate': (lambda self, cr, uid, ids, c=None: ids, ['invoice_ids'], 10)}

    _columns = dict(
        name = fields.char('Codigo', size=32, required=True,
                           readonly=True),
        number = fields.char('Número de Compromiso', readonly=True, size=16),
        notes = fields.char('Descripción', size=128, required=True,
                            readonly=True, states=STATES_VALUE),
        certificate_number = fields.char(string='Número',
                                         size=32,
                                         readonly=True),
        user_id = fields.many2one('res.users', string='Solicitante',
                                  required=True, readonly=True),
        department_id = fields.many2one('hr.department', 'Dirección / Coordinación',
                                        required=True, readonly=True),
        description = fields.text('Detalle',
                                  readonly=True, states=STATES_VALUE),
        justification = fields.text('Justificación', readonly=True), 
        state = fields.selection([('draft', 'Borrador'),
                                  ('request', 'Solicitado'),
                                  ('certified', 'Certificado'),
                                  ('compromised', 'Compromiso'),
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
        date_compromised = fields.date('Fecha de Compromiso',
                                       readonly=True, states={'certified': [('readonly',False)]}),
        amount_accured = fields.function(_compute_budget, method=True, string='Devengado',
                                         digits_compute=DP, multi='budget', store=STORE_INV),
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
            if obj.state == 'compromised' and not obj.employee_id and not obj.partner_id:
                raise osv.except_osv('Error', 'No ha ingresado un proveedor en el documento.')
            if obj.state=='compromised' and not obj.date_compromised:
                raise osv.except_osv('Error', 'No ha ingresado la fecha de compromiso.')
        return True

    _constraints = [(_check_requests,
                     'Los valores solicitados superan los disponibles de las partidas.',
                     ['Detalle de Presupuesto Referencial']),
                    (_check_partner,
                     'Debe asignar un proveedor para poder comprometer el presupuesto.',
                     ['Proveedor'])]

    _defaults = dict(
        name = '/',
        user_id = lambda self, cr, uid, context: uid,
        state = 'draft',
        date = time.strftime('%Y-%m-%d %H:%M:%S'),
        )    

    def action_confirm(self, cr, uid, ids, context=None):
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
            line_obj.action_confirm(cr, uid, line_ids)
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
            line_obj.write(cr, uid, line_ids, {'state': 'compromised'})
            self.write(cr, uid, obj.id, {'state': 'compromised', 'date_compromised': time.strftime('%Y-%m-%d')})
        return True        

    def action_certified(self, cr, uid, ids ,context=None):
        """
        Metodo que implementa el certificar los valores solicitados
        en las partidas presupuestarias de las actividades seleccionadas
        del proyecto.
        Cambia de estado a certified a self y a line_ids
        """
        return True

    def action_request(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            lines = [line.id for line in obj.line_ids]
            line_obj.change_state(cr, uid, lines, 'request')
        self.write(cr, uid, ids, {'state': 'request', 'date': time.strftime('%Y-%m-%d %H:%M:%S')})
        self.__logger.info("Prespuesto referencial emitido")
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        line_obj = self.pool.get('budget.certificate.line')
        for obj in self.browse(cr, uid, ids, context):
            lines = [line.id for line in obj.line_ids]
            line_obj.change_state(cr, uid, lines, 'cancel')
        self.write(cr, uid, ids, {'state': 'cancel'})
        self.__logger.info("Presupuesto referencial rechazado")
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

