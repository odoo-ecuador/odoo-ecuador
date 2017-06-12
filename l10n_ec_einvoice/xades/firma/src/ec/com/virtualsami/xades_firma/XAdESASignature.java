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
import es.mityc.firmaJava.role.SimpleClaimedRole;
import es.mityc.javasign.EnumFormatoFirma;
import es.mityc.javasign.certificate.ocsp.OCSPLiveConsultant;
import es.mityc.javasign.trust.TrustAbstract;
import es.mityc.javasign.trust.TrustFactory;
import es.mityc.javasign.xml.refs.InternObjectToSign;
import es.mityc.javasign.xml.refs.ObjectToSign;
import org.w3c.dom.Document;

/**
 * XAdESASignature
 *
 * Descripción:
 *
 * @author Alcides Rivera <alcides@virtualsami.com.ec>
 * @version 0.1
 */
public class XAdESASignature extends GenericXMLSignature {

    private static final String RESOURCE_TO_SIGN = "/firmas/factura.xml";
    private static final String SIGN_FILE_NAME = "XAdES-A-Sign.xml";
    private static final String URL_TSA = "http://localhost:41280/tsa";
    private static final String URL_OCSP = "http://ocsp.ctpa.mityc.es";

    public static void main(String[] args) {
        XAdESASignature signature = new XAdESASignature();
        signature.execute();
    }

    protected DataToSign createDataToSign() {
        DataToSign dataToSign = new DataToSign();

        TrustFactory tf = TrustFactory.getInstance();
        TrustAbstract truster = tf.getTruster("mityc");

        dataToSign.setCertStatusManager(new OCSPLiveConsultant("http://ocsp.ctpa.mityc.es", truster));

        dataToSign.setXadesFormat(EnumFormatoFirma.XAdES_XL);

        dataToSign.setEsquema(XAdESSchemas.XAdES_132);

        dataToSign.setXMLEncoding("UTF-8");

        dataToSign.addClaimedRol(new SimpleClaimedRole("Rol de firma"));

        dataToSign.setEnveloped(true);

        dataToSign.addObject(new ObjectToSign(new InternObjectToSign("contenido"), "Documento de ejemplo", null, "text/xml", null));
        dataToSign.setParentSignNode("titulo");

        Document docToSign = getDocument("/firmas/factura.xml");
        dataToSign.setDocument(docToSign);
        return dataToSign;
    }

    protected String getSignatureFileName() {
        return "XAdES-A-Sign.xml";
    }
}
