# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2010 GnuThink Software All Rights Reserved
#    info@gnuthink.com
#    This a complete rewrite from account_invoice_retention
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

__author__ = 'Cristian Salamea (cristian.salamea@gnuthink.com)'

from osv import osv, fields

class RetentionGrouped(osv.osv_memory):
    _name = 'wizard.retention.grouped'
    _description = 'Group the retentions by partner'

    def act_cancel(self, cr, uid, ids, context):
        return {'type':'ir.actions.act_window_close'}

    def act_generate_retention(self, cr, uid, ids, context):
        seq_obj = self.pool.get('ir.sequence')
        inv_obj = self.pool.get('account.invoice')
        ret_obj = self.pool.get('account.retention')
        invtax_obj = self.pool.get('account.invoice.tax')        
        wizard = self.browse(cr, uid, ids, context)[0]
        for inv in wizard.invoice_ids:
            if inv.retention_ir or inv.retention_vat:
                if inv.journal_id.auth_ret_id.sequence_id:
                    seq = seq_obj.browse(cr, uid, inv.journal_id.auth_ret_id.sequence_id.id)
                    ret_num = seq_obj.get(cr, uid, seq.code)
                    ret_data = {'name':ret_num,
                                'auth_id': inv.journal_id.auth_ret_id.id,
                                'partner_id': inv.partner_id.id,
                                'type': inv.type,
                                'in_type': 'ret_in_invoice',
                                'move_id': inv.move_id.id}
                    ret_id = ret_obj.create(cr, uid, ret_data)
                    for line in inv.tax_line:
                        if line.tax_group in ['ret_vat', 'ret_ir']:
                            invtax_obj.write(cr, uid, line.id, {'retention_id': ret_id, 'num_document': inv.number})
                    inv_obj.write(cr, uid, [inv.id], {'retention_id': ret_id})
                else:
                    raise osv.except_osv('Error de Configuracion',
                                         'No se ha configurado una secuencia para las retenciones en Compra')                

    _columns = {
        'partner_id': fields.many2one('res.partner','Proveedor', required=True),
        'period_id': fields.many2one('account.period', 'Periodo', required=True),
        'invoice_ids': fields.many2many('account.invoice', 'retention_grouped_rel', 'invoice_id', 'wizard_id', 'Facturas'),
        'state' : fields.selection((('choose', 'choose'),
                                    ('generate', 'generate'))),        
        }

    _defaults = {
        'state': 'choose',
        }

RetentionGrouped()
