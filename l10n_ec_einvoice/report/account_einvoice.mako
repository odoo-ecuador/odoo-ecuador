<html>
  <head>
    <meta charset="UTF-8">
    <style>

      div.container {
      margin: 15px;   
      }
      
      div.left, div.right {    
      float: left;
      }
      
      div.left {
      padding-right: 20px;
      }
      div.right {
      background-color: yellow;    
      }

      div.logo {
      height: 130px;
      width: 300px;
      background-color: green;
      padding-bottom: 20px;
      }

      div.companyinfo {
      height: 170px;
      width: 300px;
      }

      div.invoiceinfo {
      height: 320px;
      width: 350px;
      }

      div.center {
      clear: both;
      height: 130px;
      width: 700px;
      padding-top: 10px;
      }

      div.details {
      width: 700px;
      padding-top: 10px;
      }

      table.content {
      text-align: center;
      }

      div.footer {
      margin: 15px;
      }

      div.fot1 {
      width: 400px;
      float: left;
      }

      div.fot2 {
      width: 300px;
      float: left;
      }

      .label {
      text-align: left;
      padding: 4px;
      }

      .amount {
      text-align: right;
      padding: 4px;      
      }

    </style>
  </head>
  %for o in objects:
  <body>
    <div class="main">
      <div class="container">
	<div class="left">
	  <div class="logo">
	  </div>
	  <div class="companyinfo">
	    <table>
	      <tr>
		<td>
		  ${o.company_id.name.upper()}
		</td>
	      </tr>
	      <tr>
		<td>
		  ${ o.company_id.street } ${ o.company_id.street2 }
		</td>
	      </tr>
	      <tr>
		<td>
		  <br>
		</td>
	      </tr>	    
	      <tr>
		<td>
		  Constribuyente Especial Nro: ${o.company_id.company_registry}
		</td>
	      </tr>
	      <tr>
		<td>
		  Obligado a llevar contabilidad: SI
		</td>
	      </tr>	    
	    </table>
	  </div>	
	</div>
	<div class="right">
	  <div class="invoiceinfo">
	    <table>
	      <tr>
		<td>
		  RUC: ${o.company_id.partner_id.ced_ruc}
		</td>
	      </tr>
	      <tr>
		<td>
		  FACTURA
		</td>
	      </tr>
	      <tr>
		<td>
		  No. ${ obj.number }
		</td>
	      </tr>
	      <tr>
		<td>
		  Numero de Autorización
		</td>
	      </tr>
	      <tr>
		<td>
		  ${ obj.numero_autorizacion }
		</td>
	      </tr>
	      <tr>
		<td>
		  Fecha y Hora de Autorizacion: 07/06/2015 14:20:05
		</td>
	      </tr>
	      <tr>
		<td>
		  AMBIENTE: Producción
		</td>
	      </tr>
	      <tr>
		<td>
		  EMISION: Emisión Normal
		</td>
	      </tr>	    
	    </table>
	  </div>
	</div>
      </div>
      <div class="center">
	<div>
	  <table>
	    <tr>
	      <td>
		Razón Social / nombres y apellidos:
	      </td>
	      <td>
		Cristian Gonzalo Salamea Maldonado
	      </td>
	      <td>
		RUC/CI:
	      </td>
	      <td>
		0103893954
	      </td>
	    </tr>
	    <tr>
	      <td>
		Fecha de Emisión:
	      </td>
	      <td>
		04/01/2015
	      </td>	      
	      <td>
		Guía de Remisión:
	      </td>
	      <td>
		001001000000001
	      </td>
	    </tr>
	  </table>
	</div>
      </div>
      <div class="details">
	<table class="content">
	  <tr>
	    <td>
	      Cód. Principal
	    </td>
	    <td>
	      Cantidad
	    </td>
	    <td>
	      Descripción
	    </td>
	    <td>
	      Precio Unitario
	    </td>
	    <td>
	      Descuento
	    </td>
	    <td>
	      Precio total
	    </td>
	  </tr>
	  <tr>
	    <td>
	      00001011
	    </td>
	    <td>
	      12.00
	    </td>
	    <td>
	      Telefonia ETAPA
	    </td>
	    <td>
	      6.00
	    </td>
	    <td>
	      0.00
	    </td>
	    <td>
	      60.00
	    </td>
	  </tr>	  
	</table>
      </div>
      <div class="footer">
	<div class="fot1">
	  <table>
	    <tr>
	      <td>
		INFORMACION ADICIONAL
	      </td>
	    </tr>
	  </table>
	</div>
	<div class="fot2">
	  <table class="taxes">
	    <tr>
	      <td class="label">
		SUBTOTAL 12%
	      </td>
	      <td>
		60.00
	      </td>	      
	    </tr>
	    <tr>
	      <td class="label">
		SUBTOTAL 0%
	      </td>	      
	      <td class="amount">
		0.00
	      </td>
	    </tr>
	    <tr>
	      <td class="label">
		SUBTOTAL no sujeto IVA
	      </td>	      
	      <td class="amount">
		0.00
	      </td>
	    </tr>
	    <tr>
	      <td class="label">
		SUBTOTAL SIN IMPUESTOS
	      </td>	      
	      <td class="amount">
		0.00
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
		IVA 12%
	      </td>	      
	      <td class="amount">
		7.20
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
		67.20
	      </td>
	    </tr>	    
	  </table>
	</div>	
      </div>
    </div>
  </body>
  %endfor
</html>
