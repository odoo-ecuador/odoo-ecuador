# -*- coding: utf-8 -*-

from openerp import models


class MailTemplate(models.Model):

    _inherit = 'mail.template'

    def generate_email_batch(self, cr, uid, template_id,
                             res_ids, context=None, fields=None):
        res = super(MailTemplate, self).generate_email_batch(
            cr, uid, template_id, res_ids, context, fields)
        res[res_ids[0]]['attachment_ids'] = res[res_ids[0]]['attachment_ids'] + context.get('attachment_ids', [])  # noqa
        return res
