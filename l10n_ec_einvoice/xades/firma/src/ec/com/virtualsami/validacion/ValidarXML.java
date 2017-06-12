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

import java.io.File;
import java.io.IOException;
import javax.xml.transform.Source;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

/**
 * ValidarXML
 *
 * Descripción:
 *
 * @author Alcides Rivera <alcides@virtualsami.com.ec>
 * @version 0.1
 */
public class ValidarXML {

    public void validar(String rutaXML, String rutaXSD)
            throws IOException {
        Source xmlFile = new StreamSource(new File(rutaXML));

        File schemaLocation = new File(rutaXSD);

        SchemaFactory schemaFactory = SchemaFactory.newInstance("http://www.w3.org/2001/XMLSchema");
        try {
            Schema schema = schemaFactory.newSchema(schemaLocation);

            Validator validator = schema.newValidator();
            validator.validate(xmlFile);
            System.out.println(xmlFile.getSystemId() + " es valido!");
        } catch (SAXParseException e) {
            System.out.println(xmlFile.getSystemId() + " NO es válido!");
            System.out.println("Razón\t\t: " + e.getLocalizedMessage());
            System.out.println("Número de linea \t: " + e.getLineNumber());
            System.out.println("Número de columna\t: " + e.getColumnNumber());
            System.out.println("Id Público\t: " + e.getPublicId());
        } catch (SAXException e) {
            System.out.println(xmlFile.getSystemId() + " NO es válido");
            System.out.println("Razón\t: " + e.getLocalizedMessage());
        }
    }
}
