# Localizacion de OpenERP para Ecuador (Fábrica de Software Libre)

Este proyecto es un derivado del proyecto odoo-ecuador, en el mismo se desarrollan y modifican los módulos con los cuales nuestra empresa aporta a la comunidad para que luego sean integrados a la rama oficial.

A diferencial de proyecto base, nosotros solo desarrollamos para la versión 8 y posteriores.

# Aclaratorio a la Licencia

"Este proyecto es un trabajo derivado de AGPL v3, si utilizas este trabajo es necesario que publiques los cambios realizados, si no lo haces debes enviar un tweet con el hashtag [#SoyUnOdooTrollenEcuador](https://twitter.com/search?f=tweets&q=%23SoyUnOdooTrollEnEcuado).

Dedicado a toda esa gente linda de mi país que aplica la viveza criolla y vende este software y cambia el autor." Proyecto odoo-ecuador.


# Criterios de desarrollo.

1.- La instalación de módulos va a realizarse a través de el módulo l10n_ec_config, que siempre será actualizado para permitir a los usuarios nuevos saber lo que existe y poder instalarlo con facilidad.

2.- Vamos a tratar de utilizar el código nativo de Odoo o módulos desarrollados para otras localizaciones antes de crear un módulo propio (no hay para que re-inventar la rueda).

3.- Vamos a desarrollar en español, dando a los módulos nombres compatibles con el estándar internacional de Odoo y manteniendo la base del proyecto odoo-ecuador, pero tratando de que sean nombres significativos y fáciles de entender en español. Igualmente, los comentarios, strings, help, placeholders y todo lo demás lo vamos a escribir en español. (Si alguien necesita la localización del Ecuador en inglés, tendrá que traducirla).

4.- Trataremos de clonar y/o copiar todos los módulos que utilizamos en el mismo repositorio a fin de evitar problemas de dependencias. 

5.- Todo el desarrollo se realizará a través de este repositorio para evitar código obsoleto.

6.- Los módulos que consideramos necesarios para la localización empiezan con l10n_ec_nombredelmodulo y los que son herramientas con ec_nombredelmodulo.

# Instalación

1.- Instalar Odoo (www.odoo.com).

2.- Clonar el repositorio y actualizar la lista de módulos locales.

3.- Instalar el módulo l10n_ec_config.

4.- Ir a: Configuraciones --> Para Ecuador.

5.- Seleccionar las opciones que se desea instalar en la localización.

6.- Aplicar.

Nota: el módulo de configuraciones está señalado para instalarse automáticamente al crear una base de datos, así que si crea la base con el módulo en el repositorio, puede saltar del paso 2 al 4.
