# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from odoo.cli.command import Command


class update_nui(Command):
    """Actualiza los partners desde el registro civil"""
    def run(self, args):
        print args
        partners = self.env['res.partners'].search()
        for partner in partners:
            print partner.identifier
