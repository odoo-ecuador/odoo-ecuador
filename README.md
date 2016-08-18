![Licence](https://img.shields.io/badge/licence-AGPL--3-blue.svg) [![Build Status](https://travis-ci.org/odoo-ecuador/odoo-ecuador.svg?branch=9.0)](https://travis-ci.org/odoo-ecuador/odoo-ecuador) [![Coverage Status](https://coveralls.io/repos/github/ovnicraft/odoo-ecuador/badge.svg?branch=9.0)](https://coveralls.io/github/ovnicraft/odoo-ecuador?branch=9.0)

Localizacion de OpenERP para Ecuador
====================================

Este proyecto intenta implementar todas las funcionalidades
requeridas para que OpenERP pueda implementarse en cualquier
empresa ecuatoriana.


Iniciamos la migración a 9.0
----------------------------

En analisis de objetos contables ha terminado y podemos resumir que la migración es viable y hemos iniciado el trabajo.

Usaremos módulos de la comunidad para responder a los reportes financieros, existe un trabajo en progreso en el repositorio oca/account-financial-reporting que
nos permitirá tener una solución completa.

Estamos en pase alpha aún, esperamos a finales de Agosto 2016 terminar el trabajo.

Referencias de Implementación
-----------------------------

Es importante también recalcar que este proyecto siempre esta activo, esta versión de localización esta en producción en muchos lugares. Te invitamos a incluir en la [Wiki](https://github.com/odoo-ecuador/odoo-ecuador/wiki/Referencia-de-clientes) de referencias a tus clientes en donde has implementado estos módulos, esto lo consideramos importante para dar valor al trabajo en conjunto que se realiza por la comunidad.

Aclaratorio a la Licencia
-------------------------

Este proyecto es un trabajo derivado de AGPL v3, si utilizas este trabajo es necesario que publiques los cambios realizados, si no lo haces debes enviar un tweet con el hashtag [#SoyUnOdooTrollenEcuador](https://twitter.com/search?f=tweets&q=%23SoyUnOdooTrollEnEcuado).

Dedicado a toda esa gente linda de mi país que aplica la viveza criolla y vende este software y cambia el autor.

Estado de Módulos
-----------------


| MODULO                   | ESTADO    | OBSERVACIONES                           |
|--------------------------|-----------|-----------------------------------------|
| l10n_ec_advances         | DESCARTADO | No migrado a la v 8.0                   |
| l10n_ec_authorisation    | ESTABLE|                                         |
| l10n_ec_chart            | NO MIGRADO   |                                         |
| l10n_ec_einvoice         | NO MIGRADO   |                                         |
| l10n_ec_employee         | NO MIGRADO   |                                         |
| l10n_ec_invoice_sequence | NO MIGRADO   |                                         |
| l10n_ec_ote              | NO MIGRADO   |                                         |
| l10n_ec_partner          | ESTABLE   |                                         |
| l10n_ec_pos              | NO MIGRADO |  |
| l10n_ec_withdrawing      | EN MIGRACION   |                                         |


Objetivos principales
---------------------

- Plan de cuentas para diferentes tipos de empresas, sitio de ref: http://www.supercias.gob.ec
- Documentos contables: Retenciones, liquidaciones de compra, etc.
- Reportes tributarios, sitio de ref: http://www.sri.gob.ec
- Traducción a español (es_EC)

Uso de Módulos
--------------

Para la instalación y uso::

     $ git clone https://github.com/odoo-ecuador/odoo-ecuador.git

Ahora ejecutar odoo agregando al path de módulos::

     $ ./openerp-server --addons-path=addons,../odoo-ecuador

El comando anterior asume que odoo y odoo-ecuador estan al mismo nivel.

Para escribir pruebas unitarias revisar la [wiki](https://github.com/odoo-ecuador/odoo-ecuador/wiki/Pruebas-Unitarias)
