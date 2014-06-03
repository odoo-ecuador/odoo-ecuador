<html>
<head>
    <style type="text/css">
        ${css}
        body {
        font-family:arial, san serif;
        font-size:9;
        }
        .header_invoice {
        position:relative;
        left:100px;
        top:-10px;
        font-size:11;
        }
	.invoice_total {
        position:relative;
        left:671px;
        top:300px;
        font-size:11;
        }        
        .invoice_line {
        font-size:11;
        }               
    </style>  
</head>
<body>
  %for o in objects:
  <table class="header_invoice">
    <tr><td style="font-size:12;">${o.user_id.name or ''}</td></tr>	
    <tr><td style="font-size:12;">${o.partner_id.name or  ''}</td></tr>
    <tr>
	<td width="260" style="font-size:12;">${o.address_invoice_id.street or ''} ${o.address_invoice_id.street2 or ''}</td>
        <td width="100" style="font-size:12;">${o.date_invoice or ''}</td>	
    </tr>
    <tr>
	<td style="font-size:12;">${o.partner_id.ced_ruc or '##########'}</td>	
        <td style="font-size:12;">${o. address_invoice_id and o.address_invoice_id.city or ''}</td>	

    </tr>
  </table>
  <br><br>
  <table width="80%" class="invoice_line">
    %for line in o.invoice_line :
    <tbody>
    <tr >
      <td width="10%" style="text-align:left">${line.quantity or ''}</td>
      <td width="25%" style="text-align:left">${line.product_id.name or ''}</td>
      <td width="10%" style="text-align:right">${formatLang(line.price_unit, digits=get_digits(dp='Purchase Price')) }</td>
      <td width="10%" style="text-align:right">${formatLang(line.price_subtotal, digits=get_digits(dp='Purchase Price')) }</td>
    </tr>
    %endfor      
    </tbody>
    <br>
  </table>
  <table  class="invoice_total">
    <tr>
	<td style="text-align:right">${o.amount_vat_cero or '0,00'}</td>
    </tr>
    <tr><td style="text-align:right">${o.amount_vat or '0,00'}</td></tr>
    <tr><td style="text-align:right">${o.amount_tax or '0,00'}</td></tr>
    <tr><td style="text-align:right">${o.amount_total or '0.00'}</td></tr>
  </table-->    
  %endfor
</html>
