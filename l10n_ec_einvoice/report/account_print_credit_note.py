# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw


class account_credit_note(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_credit_note, self).__init__(cr, uid, name, context=context)  # noqa
        self.localcontext.update({
            'time': time,
            'get_number_invoice': self.get_number_invoice,
            'get_date_invoice': self.get_date_invoice,
            'get_amount_invoice': self.get_amount_invoice,
        })

    def get_number_invoice(self, object):
        invoice = self.pool.get('account.invoice')
        invoice_ids = invoice.search(
            self.cr,
            self.uid,
            [('number', '=', object.name)])
        return invoice.browse(
            self.cr,
            self.uid,
            invoice_ids)[0].supplier_invoice_number

    def get_date_invoice(self, object):
        invoice = self.pool.get('account.invoice')
        invoice_ids = invoice.search(
            self.cr,
            self.uid,
            [('number', '=', object.name)])
        return invoice.browse(self.cr, self.uid, invoice_ids)[0].date_invoice

    def get_amount_invoice(self, object):
        invoice = self.pool.get('account.invoice')
        invoice_ids = invoice.search(
            self.cr,
            self.uid,
            [('number', '=', object.name)])
        return invoice.browse(
            self.cr, self.uid,
            invoice_ids, context=self.context).amount_pay

report_sxw.report_sxw(
    'report.account.credit_note',
    'account.invoice',
    'addons/l10n_ec_e-invoice/report/account_print_credit_note.rml',
    parser=account_credit_note
)
