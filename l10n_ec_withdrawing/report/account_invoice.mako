<html>
<head>
    <style type="text/css">
        ${css}
        body {
        font-family:arial, san serif;
        }
        .header_invoice {
        left:130px;
        top:-10px;
        font-size:8;
        }
	    .invoice_total {
        position:absolute;
        font-size:8;
        top: 300px;
        right: 150px;
        }        
        .invoice_line {
        font-size:8;
        }
    </style>  
</head>
<body>
  %for o in objects:
  <table class="header_invoice" width="70%">
    <tr>
      <td width="8%"></td>
      <td width="90%">${o.date_invoice or ''}</td>
      <td width="1%"></td>
      <td width="1%"></td>
    </tr>
    <tr>
      <td width="8%"></td>
      <td colspan="3">${o.partner_id.name or  ''}</td>
    </tr>
    <tr>
      <td width="8%"></td>
	  <td width="80%" colspan="2">${o.address_invoice_id.street or ''} ${o.address_invoice_id.street2 or ''}</td>
	  <td width="12%" >${o.address_invoice_id.phone or ''}</td>
    </tr>
    <tr>
      <td width="8%"></td>
	  <td colspan="3">${o.partner_id.ced_ruc or '##########'}</td>	
    </tr>
  </table>
  <br><br>
  <table width="70%" class="invoice_line">
    %for line in o.invoice_line :
    <tbody>
    <tr >
      <td width="10%" style="text-align:left">${line.quantity or ''}</td>
      <td width="70%" style="text-align:left">${line.note or ''}</td>
      <td width="10%" style="text-align:left">${formatLang(line.price_unit, digits=2) }</td>
      <td width="10%" style="text-align:right">${formatLang(line.price_subtotal, digits=2) }</td>
    </tr>
    %endfor      
    </tbody>
    <br>
  </table>
  <table width="70%" class="invoice_total">
    <tr>
	<td width="70%" style="text-align:right">${formatLang(o.amount_untaxed or 0.00, digits=2)}</td>
    </tr>
    <tr><td width="70%" style="text-align:right">${formatLang(o.amount_vat_cero or 0.00, digits=2)}</td></tr>
    <tr><td width="70%" style="text-align:right">${formatLang(o.amount_tax, digits=2)}</td></tr>
    <tr><td width="70%" style="text-align:right">${formatLang(o.amount_total, digits=2)}</td></tr>
  </table-->    
  %endfor
</html>
