<html>
  <head>
    <meta charset="UTF-8">
    <style>

     h3 {
       text-align: center;
     }

     body {
       font-family:helvetica, helvetica bold, Arial Bold;
       font-size:12px;
       height: 260mm;
       width: 210mm
     }

     div.container {
       margin: 15px;
     }

     div.left, div.right {
       float: left;
     }

     div.left {
       padding-right: 21px;
     }
     div.right {
       border: 1px solid gray;
     }

     div.logo {
       height: 130px;
       width: 350px;
       padding-top: 10px;
       padding-botton: 10px;
       border: 1px solid gray;
       text-align: center;
     }

     div.companyinfo {
       height: 170px;
       width: 350px;
       border: 1px solid gray;
     }

     div.invoiceinfo {
       height: 310px;
       width: 370px;
       border: 1px solid gray;
       font-size: 14px;
     }

     div.customer {
       clear: both;
       height: 80px;
       padding-top: 10px;
       width: 745px;
       border: 1px solid gray;
     }

     div.details {
       width: 745px;
       padding-top: 10px;
       border: 1px solid gray;
     }

     table.content {
       text-align: center;
     }

     div.footer {
       margin: 15px;
       width: 905px;
     }

     div.fot1, div.fot2 {
       float: left;
     }

     div.fot1 {
       width: 395px;
       float: left;
     }

     div.fot2 {
       width: 350px;
       float: left;
       border: 1px solid gray;
     }

     .label {
       text-align: left;
       padding: 4px;
     }

     .amount {
       text-align: right;
       padding: 4px;
     }

     td {
       padding: 5px;
     }

     div.info {
       padding: 5px;
       text-align: center;
     }

    </style>
  </head>
  %for o in objects:
  <body>
    <div class="main">
      <div class="container">
	<div class="left">
	  <div class="logo">
	     ${helper.embed_logo_by_name('company_logo')|safe}
	  </div>
	  <div class="companyinfo">
	    <div class="info">
	      <td>
		<h3> ${o.company_id.name.upper()} </h3>
	      </td>
	    </div>
	    <div class="info">
	      <td>
		<strong>DIRECCION</strong> ${ o.company_id.street } ${ o.company_id.street2 }
	      </td>
	    </div>
	    <div>
	    </div>
	    <div class="info">
	    </div>
	    <div class="info">
	      <td>
		Obligado a llevar contabilidad:
	      </td>
	      <td>
		SI
	      </td>
	    </div>
	  </div>
	</div>
	<div class="right">
	  <div class="invoiceinfo">
	    <div class="info">
	      <b>RUC:</b>
	      ${o.company_id.partner_id.ced_ruc}
	    </div>
	    <div class="info" style="text-align: center;">
	      <div style="text-align: center;">
		<b>RETENCION</b>
	      </div>
	      <div>
		No. ${ o.name[:3] }-${ o.name[3:6] }-${ o.name[-9:] }
	      </div>
	    </div>
	    <div class="info" style="text-align: center;">
	      <b>NUMERO AUTORIZACION</b>
	    </div>
	    <div class="info" style="text-align: center;">
	      ${ o.numero_autorizacion }
	    </div>
	    <div class="info" style="text-align: left;">
	      <b>FECHA AUTORIZACION: </b>${ o.fecha_autorizacion }
	    </div>
	    <div class="info" style="text-align: left;">
	      <div class="info" style="text-align: left;">
		<b>AMBIENTE</b>
		${ o.company_id.env_service=='1' and 'PRUEBAS' or 'PRODUCCION' }
	      </div>
	      <div class="info" style="text-align: left;">
		<b>EMISION:</b>
		EMISION ${ o.company_id.emission_code }
	      </div>
	      <div style="text-align: center;">
		<b>CLAVE DE ACCESO</b>
	      </div>
	      <div style="text-align: center;">
		${ helper.barcode(o.clave_acceso, htmlAttrs={'width': '350px', 'height': '30px;'}) | safe}
	      </div>
	      <div style="font-size: 11px !important; text-align: center;">
		${ o.clave_acceso }
	      </div>
	    </div>
	  </div>
	</div>
	<div class="customer">
	  <table style="border: none !important;">
	    <tr>
	      <td style="width: 15%; font-size:14px;">
		<b>PROVEEDOR:</b>
	      </td>
	      <td style="width: 40%;font-size:14px;">
		${ o.partner_id.name.upper() }
	      </td>
	      <td style="width: 15%; font-size:14px;">
		<b>RUC/CI:</b>
	      </td>
	      <td style="width: 10%; font-size:14px;">
		${ o.partner_id.ced_ruc }
	      </td>
	    </tr>
	    <tr>
	      <td style="font-size:14px;">
		<b>FECHA DE EMISION:</b>
	      </td>
	      <td>
		${ o.date }
	      </td>
	      <td>
	      </td>
	    </tr>
	  </table>
	</div>
	<div class="details">
	  <table class="content">
	    <tr>
	      <th style="width: 10%">
		COMPROBANTE
	      </th>
	      <th style="width: 20%">
		NUMERO
	      </th>
	      <th style="width: 15%">
		FECHA EMISION
	      </th>
	      <th style="width: 10%">
		EJER. FISCAL
	      </th>
	      <th style="width: 10%">
		BASE IMPONIBLE
	      </th>
	      <th style="width: 10%">
		IMPUESTO
	      </th>
	      <th style="width: 10%">
		PORCENTAJE
	      </th>
	      <th style="width: 10%">
		VALOR RETENIDO
	      </th>
	    </tr>
	    %for line in o.tax_ids:
	    <tr>
	      <td>
                ${ line.invoice_id.type in ['out_invoice','in_invoice'] and 'FACTURA' or 'LIQ. COMPRA' }
	      </td>
	      <td>
                ${ line.invoice_id.invoice_number }
	      </td>
	      <td>
                ${ line.invoice_id.date_invoice }
	      </td>
	      <td>
                ${ line.fiscal_year }
	      </td>
	      <td>
		${ line.base  }
	      </td>
	      <td>
                ${ line.tax_group in ['ret_vat_srv','ret_vat_b'] and 'IVA' or 'RENTA' }
	      </td>
	      <td>
                ${ line.percent } ${ '%' }
	      </td>
	      <td>
                ${ line.amount * -1 }
	      </td>
	    </tr>
	    %endfor
	  </table>
	</div>
        <br>
        <div id="extrainfo">
          <table>
            <tr>
              <td>INFORMACION ADICIONAL</td>
            </tr>
            <tr>
              <td>DIRECCION:</td>
              <td>${ o.partner_id.street } </td>
            </tr>
            <tr>
              <td>EMAIL:</td>
              <td>${ o.partner_id.email }</td>
            </tr>
            <tr>
              <td>TELEF:</td>
              <td>${ o.partner_id.phone }</td>
            </tr>
          </table>
        </div>
      </div>
  </body>
  %endfor
</html>
