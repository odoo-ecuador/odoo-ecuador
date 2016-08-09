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
       height: 297mm;
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
	      <td>
		Contribuyente Especial Nro: ${o.company_id.company_registry}
	      </td>
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
		<b>FACTURA</b>
	      </div>
	      <div>
		No. ${ o.invoice_number }
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
		<b>CLIENTE:</b>
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
		${ o.date_invoice }
	      </td>
	      <td style="font-size:14px;">
		<b>GUIA DE REMISION:</b>
	      </td>
	      <td>
	      </td>
	    </tr>
	  </table>
	</div>
	<div class="details">
	  <table class="content">
	    <tr>
	      <th style="width: 15%">
		CODIGO
	      </th>
	      <th style="width: 50%">
		DESCRIPCION
	      </th>
	      <th style="width: 5%">
		CANTIDAD
	      </th>
	      <th style="width: 10%">
		PRECIO
	      </th>
	      <th style="width: 10%">
		DESCUENTO
	      </th>
	      <th style="width: 10%">
		TOTAL
	      </th>
	    </tr>
	    %for line in o.invoice_line:
	    <tr>
	      <td>
		${ line.product_id.default_code or '**' }
	      </td>
	      <td>
		${ line.product_id.name }
	      </td>
	      <td>
		${ '%.2f'%line.quantity }
	      </td>
	      <td>
		${ '%.2f'%line.price_unit }
	      </td>
	      <td>
		0.00
	      </td>
	      <td>
		${ '%.2f'%line.price_subtotal }
	      </td>
	    </tr>
	    %endfor
	  </table>
	</div>
        <div id="tres">
	  <div class="fot1">
	    <div style="padding: 5px;">
	      DETALLE:
	    </div>
	  </div>
	  <div class="fot2">
	    <div>
	      <table style="width: 100%">
	        <tr>
		  <td class="label">
		    SUBTOTAL 14%
		  </td>
		  <td class="amount">
		    ${ '%.2f'% o.amount_vat }
		  </td>
	        </tr>
	        <tr>
		  <td class="label">
		    SUBTOTAL 0%
		  </td>
		  <td class="amount">
		    ${ '%.2f'% o.amount_vat_cero }
		  </td>
	        </tr>
	        <tr>
		  <td class="label">
		    SUBTOTAL no sujeto IVA
		  </td>
		  <td class="amount">
		    ${ '%.2f'% o.amount_novat }
		  </td>
	        </tr>
	        <tr>
		  <td class="label">
		    SUBTOTAL SIN IMPUESTOS
		  </td>
		  <td class="amount">
		    ${ '%.2f'% o.amount_untaxed }
		  </td>
	        </tr>
	        <tr>
		  <td class="label">
		    DESCUENTOS
		  </td>
		  <td class="amount">
		    0.00
		  </td>
	        </tr>
	        <tr>
		  <td class="label">
		    ICE
		  </td>
		  <td class="amount">
		    0.00
		  </td>
	        </tr>
	        <tr>
		  <td class="label">
		    IVA 14%
		  </td>
		  <td class="amount">
		    ${ '%.2f'% o.amount_tax }
		  </td>
	        </tr>
	        <tr>
		  <td class="label">
		    PROPINA
		  </td>
		  <td class="amount">
		    0.00
		  </td>
	        </tr>
	        <tr>
		  <td class="label">
		    VALOR TOTAL
		  </td>
		  <td class="amount">
		    ${ '%.2f'% o.amount_pay }
		  </td>
	        </tr>
	      </table>
	    </div>
          </div>
	</div>
      </div>
  </body>
  %endfor
</html>
