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
package ec.com.virtualsami.xades_firma;

import adsi.org.apache.xml.security.signature.ObjectContainer;
import es.mityc.javasign.xml.resolvers.MITyCResourceResolver;
import es.mityc.javasign.xml.transform.Transform;
import java.util.ArrayList;
import java.util.List;
import org.w3c.dom.Document;

/**
 * AbstractObjectToSign
 *
 * Descripción:
 *
 * @author Alcides Rivera <alcides@virtualsami.com.ec>
 * @version 0.1
 */
public abstract class AbstractObjectToSign {

    private ArrayList<Transform> transforms = new ArrayList();

    public void addTransform(Transform t) {
        if (t != null) {
            boolean mustadd = true;
            String alg = t.getAlgorithm();
            if ((alg != null) && ("http://www.w3.org/2000/09/xmldsig#enveloped-signature".equals(alg))) {
                for (Transform trans : this.transforms) {
                    if (alg.equals(trans.getAlgorithm())) {
                        mustadd = false;
                        break;
                    }
                }
            }
            if (mustadd) {
                this.transforms.add(t);
            }
        }
    }

    public List<Transform> getTransforms() {
        return (List) this.transforms.clone();
    }

    public abstract String getReferenceURI();

    public String getType() {
        return null;
    }

    public List<ObjectContainer> getObjects(Document doc) {
        return new ArrayList();
    }

    public MITyCResourceResolver getResolver() {
        return null;
    }
}
