Localizacion de OpenERP para Ecuador
====================================

Este proyecto intenta implementar todas las funcionalidades
requeridas para que OpenERP pueda implementarse en cualquier
empresa ecuatoriana.

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