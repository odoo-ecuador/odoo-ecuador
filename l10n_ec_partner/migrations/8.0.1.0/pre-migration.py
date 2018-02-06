# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

__name__ = (
    u'Elimina la restricción de indentificador único a nivel de SGDB y'
    ' mueve el contenido de la columna "ced_ruc" a "vat".')


def test_column_exists(cr, table, column):
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name=%s AND column_name=%s""", (table, column))
    return cr.fetchone()


def fix_ced_ruc(cr):
    if test_column_exists(cr, 'res_partner', 'ced_ruc'):
        _logger.info('Moviendo contenido de "ced_ruc" a "vat"...')
        cr.execute("""UPDATE res_partner SET vat = ced_ruc
                      WHERE COALESCE(ced_ruc, '') != ''""")
        _logger.info('Eliminando la columna "ced_ruc"...')
        cr.execute("ALTER TABLE res_partner DROP COLUMN ced_ruc")


def fix_vat_unique(cr):
    _logger.info('Eliminando resticción de unicidad del identificador...')
    cr.execute("""ALTER TABLE res_partner
                  DROP CONSTRAINT IF EXISTS res_partner_partner_unique""")


def migrate(cr, version):
    fix_ced_ruc(cr)
    fix_vat_unique(cr)
