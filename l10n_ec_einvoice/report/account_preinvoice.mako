<html>
	<head>
		<style>
			${css}
			body {
				font: 8px arial;
				margin-right: 0cm; 
			}
			.titulo {
				text-align: center;
				font-size: 9px;
				font-weight: bold;
			}
                        .texto_justificado {
				text-align: justify;
			}
			.centrado {
				text-align: center;
			}
			.titulo_campo {
				font-weight: bold;
			}
			.titulo_totales {
				font-weight: bold;
				text-align: right;
			}
			.cantidades {
				text-align: center;
			}
			.totales {
				text-align: right;
			}
		</style>
	</head>
	<body>
		%for o in objects:
                <center>
                <img src="data:image/jpeg;base64,${o.company_id.logo}" width="200" />
                </center>
                <p class="titulo">
		${o.company_id.name or ''}<br/>
                RUC: ${o.company_id.partner_id.ced_ruc or ''}<br/>
		${o.company_id.street2}<br/>
		</p>
		<p class="text_justificado">Dando cumplimiento al Reglamento de Facturación Electrónica del Ecuador según resolución No. NAC-DGERCGC13-00236 emitido el 
                   6 de mayo del 2013 y al ser contribuyente Especial No. ${o.company_id.company_registry}, tiene como obligación emitir comprobantes electrónicos a partir 
                   del 01 de enero de 2015.</p>
		<p class="centrado">**SIN VALIDEZ TRIBUTARIA**</p>
                <p class="titulo">FACTURA ELECTRÓNICA Nro. ${o.supplier_invoice_number or ''}</p>
                <table>
			<tr>
                                <td class="titulo_campo">Fecha:</td>
                                <td>${o.date_invoice or  ''}</td>
                        </tr>
			<tr>
				<td class="titulo_campo">Cédula/RUC:</td>
				<td>${o.partner_id.ced_ruc or  ''}</td>
			</tr>
			<tr>
				<td class="titulo_campo">Razón Social:</td>
				<td>${o.partner_id.name or ''}</td>
			</tr>
			<tr>
				<td class="titulo_campo">Dirección:</td>
				<td>${o.partner_id.street or ''}, ${o.partner_id.city.name or ''} - ${o.partner_id.state_id.name}</td>
			<tr>
			<tr> 
                                <td class="titulo_campo">Teléfono/Celular:</td>
                                <td>${o.partner_id.phone or ''}, ${o.partner_id.mobile or ''}</td>
                        </tr>
		</table>
		<p>==========================================</p>
		<table width="100%">
			<tr>
				<th>DESCRIPCIÓN</th>
				<th>CANT</th>
				<th>P. UNIT</th>
				<th>TOTAL</th>
			</tr>
                        %for line in o.invoice_line :
			<tr>
				<td width="65%">${line.product_id.name[0:25] or ''}</td>
				<td width="5%" class="cantidades">${line.quantity or ''}</td>
				<td width="15%" class="totales">${formatLang(line.price_unit, digits=4) }</td>
				<td width="15%" class="totales">${formatLang(line.price_subtotal, digits=2) }</td>
			</tr>
			%endfor
		</table>
		<table width="100%">
			<tr>
				<td width="85%" class="titulo_totales">SUBTOTAL 12%</td>
				<td width="15%" class="totales">${formatLang(o.amount_vat or 0.00, digits=2)}</td>
			</tr>
			<tr>
				<td class="titulo_totales">SUBTOTAL 0%</td>
				<td class="totales">${formatLang(o.amount_vat_cero or 0.00, digits=2)}</td>
			</tr>
			<tr>
				<td class="titulo_totales">DESCUENTO</td>
				<td class="totales">${formatLang(o.discount_total or 0.00, digits=2)}</td>
			</tr>
			<tr>
				<td class="titulo_totales">IVA 12%</td>
				<td class="totales">${formatLang(o.amount_tax or 0.00, digits=2)}</td>
			</tr>
			<tr>
				<td class="titulo_totales">TOTAL</td>
				<td class="totales">${formatLang(o.amount_pay or 0.00, digits=2)}</td>
			</tr>
		</table>
		<p class="texto_justificado">
			USTED FUE ATENDIDO POR: ${o.user_id.partner_id.name}<br/>
			Consulte su documento electrónico en la bandeja de entrada o spam de su correo electrónico: ${o.partner_id.email}.<br/>
                </p>
		<p><b>Clave de Acceso:</b></p>
		<p style="font-size: 9px">${o.clave_acceso}</p>
		<p><b>Número de Autorización:</b></p>
		<p style="font-size: 9px">${o.numero_autorizacion}</p>
		<p class="titulo">Fue un placer atenderlo!!!</p>
		%endfor
	</body>
</html>
