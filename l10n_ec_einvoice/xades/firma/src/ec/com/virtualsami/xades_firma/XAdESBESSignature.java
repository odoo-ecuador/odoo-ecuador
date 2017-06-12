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

import es.mityc.firmaJava.libreria.xades.DataToSign;
import es.mityc.firmaJava.libreria.xades.XAdESSchemas;
import es.mityc.javasign.EnumFormatoFirma;
import es.mityc.javasign.xml.refs.InternObjectToSign;
import es.mityc.javasign.xml.refs.ObjectToSign;
import org.w3c.dom.Document;

/**
 * XAdESBESSignature
 *
 * Descripción:
 *
 * @author Alcides Rivera <alcides@virtualsami.com.ec>
 * @version 0.1
 */
public class XAdESBESSignature extends GenericXMLSignature {

    private String resourceToSign;

    public XAdESBESSignature(String docAfirmar, String firma, String clave) {
        super(firma, clave);
        this.resourceToSign = docAfirmar;
    }

    public Document firmarDocumento() {
        return execute();
    }

    protected DataToSign createDataToSign() {
        DataToSign dataToSign = new DataToSign();
        dataToSign.setXadesFormat(EnumFormatoFirma.XAdES_BES);
        dataToSign.setEsquema(XAdESSchemas.XAdES_132);
        dataToSign.setXMLEncoding("UTF-8");

        dataToSign.setEnveloped(true);

        dataToSign.addObject(new ObjectToSign(new InternObjectToSign("comprobante"), "contenido comprobante", null, "text/xml", null));

        Document docToSign = getDocument(this.resourceToSign);
        dataToSign.setDocument(docToSign);
        return dataToSign;
    }

    protected String getSignatureFileName() {
        return this.resourceToSign;
    }

    public String getResourceToSign() {
        return this.resourceToSign;
    }

    public void setResourceToSign(String resourceToSign) {
        this.resourceToSign = resourceToSign;
    }
}
