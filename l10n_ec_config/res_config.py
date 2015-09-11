# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import models, fields

class ConfiguracionesEcuatorianas(models.TransientModel):
    _name = 'l10n_ec_config.config.settings'
    _inherit = 'res.config.settings'

    # Modulos
    module_l10n_ec_geopolitico = fields.Boolean(
        'Instalar la información geopolítica de Ecuador (provincias, cantones, parroquias)',
        help="""Instala el módulo l10n_ec_geopolitico.""")
    module_l10n_ec_partner = fields.Boolean(
        'Modificar res.partner para adaptarse a las necesidades ecuatorianas.',
        help="""Instala el módulo l10n_ec_partner.""")
    module_ec_id_unico = fields.Boolean(
        'Evitar que el número de identificación sea usado en más de una empresa.',
        help="""Instala el módulo ec_id_unico.""")
    module_l10n_ec_niif_pymes = fields.Boolean(
        'Plantilla de cuentas contables básicas para las Pymes según las Supercias.',
        help="""Instala el módulo l10n_ec_niif_pymes.""")
    module_l10n_ec_authorisation = fields.Boolean(
        'Ingresa los modelos necesarios para las autorizaciones del SRI, necesario para generar el ATS.',
        help="""Instala el módulo l10n_ec_authorisation.""")
    module_l10n_ec_advances = fields.Boolean(
        'Permitir realizar anticipos a proveedores y reconciliarlos con facturas.',
        help="""Instala el módulo l10n_ec_advances.""")