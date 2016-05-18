# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class AccountVoucher(osv.osv):
    _inherit = 'account.voucher'

    def action_print_report(self, cr, uid, ids, context):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        data['voucher_id'] = ids
        voucher = self.browse(cr, uid, ids, context)[0]
        datas = {
            'ids': [voucher.move_id.id],
            'model': 'account.move',
            'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.move',
            'model': 'account.move',
            'datas': datas,
            'nodestroy': True,
            }

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):  # noqa
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id and journal.default_credit_account_id  # noqa
        if (context.get('extra_type') and
                context.get('extra_type') in ['advances', 'advances_custom']):
            return {'value': {'account_id': account_id.id}}
        else:
            res = super(AccountVoucher, self).onchange_journal(
                cr, uid, ids, journal_id, line_ids,
                tax_id, partner_id, date, amount,
                ttype, company_id, context)
            return res

    _columns = dict(
        extra_type=fields.char('Tipo Anticipos', size=32),
        thirdparty_name=fields.char('A nombre de', size=64),
        thirdparty=fields.boolean('Girado a otra persona ?'),
        )

    def _get_ext(self, cr, uid, context):
        return context.get('extra_type', 'ninguno')

    _defaults = dict(
        extra_type=_get_ext
        )
