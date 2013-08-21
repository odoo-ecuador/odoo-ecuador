# -*- coding: utf-8 -*-
##############################################################################
#
#    Account Module - Ecuador
#    Copyright (C) 2010 GnuThink Software All Rights Reserved
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

import time

from osv import osv, fields


class AccountAtsDoc(osv.osv):
    _name = 'account.ats.doc'
    _description = 'Tipos Comprobantes Autorizados'

    _columns = dict(
        code = fields.char('Código', size=2, required=True),
        name = fields.char('Tipo Comprobante', size=64, required=True),
        )

AccountAtsDoc()


class AccountAtsSustento(osv.osv):
    _name = 'account.ats.sustento'
    _description = 'Sustento del Comprobante'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        res = []
        reads = self.browse(cr, uid, ids, context=context)
        for record in reads:
            name = '%s - %s' % (record.code, record.type)
            res.append((record.id, name))
        return res

    _rec_name = 'type'
    
    _columns = dict(
        code = fields.char('Código', size=2, required=True),
        type = fields.char('Tipo de Sustento', size=64, required=True),
        )

AccountAtsSustento()
    

class AccountTaxAts(osv.osv):

    _name = 'account.ats'

    _columns = dict(
        period_id = fields.many2one('account.period', string='Periodo'),
        document_id = fields.many2one('account.ats.doc', string='Tipos Comprobantes Autorizados'),
        )

AccountTaxAts()
