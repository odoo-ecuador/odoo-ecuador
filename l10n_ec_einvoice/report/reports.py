# -*- coding: utf-8 -*-

from openerp.report import report_sxw
from openerp.addons.report_webkit import webkit_report


class ReportAccountInvoice(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(ReportAccountInvoice, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_date_modified': self.get_date_modified,
            'get_num_modified': self.get_num_modified,
            'get_auth_modified': self.get_auth_modified
        })

    def get_date_modified(self, o):
        res = self.pool.get('account.invoice').search(self.cr, self.uid, [('number', '=', o.origin)], limit=1)  # noqa
        if not res:
            return
        inv = self.pool.get('account.invoice').browse(self.cr, self.uid, res)  # noqa
        return inv.date_invoice

    def get_num_modified(self, o):
        res = self.pool.get('account.invoice').search(self.cr, self.uid, [('number', '=', o.origin)], limit=1)  # noqa
        if not res:
            return
        inv = self.pool.get('account.invoice').browse(self.cr, self.uid, res)  # noqa
        number = '-'.join([inv.invoice_number[:3], inv.invoice_number[3:6], inv.invoice_number[-9:]])  # noqa
        return number

    def get_auth_modified(self, o):
        res = self.pool.get('account.invoice').search(self.cr, self.uid, [('number', '=', o.origin)], limit=1)  # noqa
        if not res:
            return
        inv = self.pool.get('account.invoice').browse(self.cr, self.uid, res)  # noqa
        return inv.numero_autorizacion


webkit_report.WebKitParser(
    'report.account_einvoice',
    'account.invoice',
    'l10n_ec_einvoice/views/report_envoice.mako',
    parser=ReportAccountInvoice
)
