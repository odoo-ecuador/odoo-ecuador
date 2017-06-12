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
package ec.com.virtualsami.keystore;

import es.mityc.javasign.pkstore.IPassStoreKS;
import java.security.cert.X509Certificate;

/**
 * PassStoreKS
 *
 * Descripción:
 *
 * @author Alcides Rivera <alcides@virtualsami.com.ec>
 * @version 0.1
 */
public class PassStoreKS implements IPassStoreKS {

    private transient String password;

    public PassStoreKS(String pass) {
        this.password = new String(pass);
    }

    public char[] getPassword(X509Certificate certificate, String alias) {
        return this.password.toCharArray();
    }
}
