/*
 *  Copyright (C) 2015 VirtualSAMI Cia. Ltda. <amanda@virtualsami.com.ec>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package ec.com.virtualsami.validacion;

/**
 * ValidarModulo11
 *
 * Descripción:
 *
 * @author Alcides Rivera <alcides@virtualsami.com.ec>
 * @version 0.1
 */
public class ValidarModulo11 {

    public int validarModulo(String cadena) {
        return obtenerSumaPorDigitos(invertirCadena(cadena));
    }

    private int obtenerSumaPorDigitos(String cadena) {
        int pivote = 2;
        int longitudCadena = cadena.length();
        int cantidadTotal = 0;
        int b = 1;
        for (int i = 0; i < longitudCadena; i++) {
            if (pivote == 8) {
                pivote = 2;
            }
            int temporal = Integer.parseInt("" + cadena.substring(i, b));
            b++;
            temporal *= pivote;
            pivote++;
            cantidadTotal += temporal;
        }
        cantidadTotal = 11 - cantidadTotal % 11;
        return cantidadTotal;
    }

    private String invertirCadena(String cadena) {
        return new StringBuilder(cadena).reverse().toString();
    }
}
