# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2009 GnuThink Software All Rights Reserved
#    info@gnuthink.com
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


from openerp.osv import osv, fields

class VoucherThirdParty(osv.osv_memory):
    
    _name = 'account.voucher.third'

    def _get_partner(self, cr, uid, context=None):
        if context is None:
            raise osv.except_osv('Alerta', 'Volver a abrir el asistente.')
        active_id = self.pool.get('')

    _columns = dict(
        partner_id = fields.many2one('res.partner', 'A nombre de'),
        thirdparty = fields.char('A nombre de'),
        change_name = fields.boolean('Cambiar portador ?'),
        )

    _defaults = dict(
        partner_id = _get_partner
        )

    def change_name(self, cr, uid, ids, context=None):
        if context is None:
            raise osv.except_osv('Alerta', 'Volver a abrir el asistente.')
        

VoucherThirdParty()
