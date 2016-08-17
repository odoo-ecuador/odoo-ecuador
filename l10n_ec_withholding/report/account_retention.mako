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
        left:40px;
        top:-15px;
        font-size:11;
        }
	.invoice_total {
        position:relative;
        left:537px;
        font-size:11;
        }        
        .invoice_line {
        font-size:11;
        }               
    </style>  
</head>
<body>
  %for o in objects:
  <table class="header_invoice" >
    <tr>
      <td> </td><td></td><td></td>
    </tr>
    <tr>
      <td> </td><td></td><td></td>
    </tr>
    <tr>
      <td> </td><td></td><td></td>
    </tr>
    <tr>
      <td> </td><td></td><td></td>
    </tr>
    <tr>
	<td width="80%" style="font-size:12;text-align:left;">${o.partner_id.name or  ''}</td>
	<td></td>
	<td width="20%" style="font-size:12;">${o.date or ''}</td>
    </tr>	
    <tr>
      <td></td><td></td><td></td>
    </tr>
    <tr>
	<td style="font-size:12;">${o.partner_id.ced_ruc or '##########'}</td>	
	<td></td>
	<td style="font-size:12;text-align:center;">${(o.type == 'in_invoice') and 'Factura' or ''} ${(o.type == 'liq_purchase') and 'Liq. de Compra' or ''} </td>	
    </tr>	
    <tr>
      <td></td><td></td><td></td>
    </tr>
    <tr>
	<td style="font-size:10;">${ o.partner_id.street } ${ o.partner_id.street2 }</td>
	<td></td>
	<td style="font-size:12;text-align:left;">${o.num_document or ''}</td>
    </tr>
  </table>
  <br><br>
  <table width="100%" class="invoice_line">
    %for line in o.tax_ids:
    <tbody>
    <tr>
      <td width="10%" style="text-align:left">${line.fiscal_year or ''}</td>
      <td width="25%" style="text-align:center">${formatLang(line.base, digits=2) or ''}</td>
      <td width="25%" style="text-align:left">${line.tax_group in ['ret_vat_b','ret_vat_srv'] and 'RET. IVA' or 'RET. RENTA'}</td>
      <td width="15%" style="text-align:left">${line.tax_group in ['ret_vat_b','ret_var_srv'] and line.tax_code_id.code or line.tax_code_id.code }</td>
      <td width="15%" style="text-align:left">${line.percent or '0.00'}%</td>
      <td width="10%" style="text-align:right">${formatLang(abs(line.amount), digits=2) or ''}</td>
    </tr>
    %endfor      
    </tbody>
    <tfoot>
      <tr>
	<td></td><td></td><td></td><td></td>
        <td style="text-align:left;font-size:8;">TOTAL RETENIDO:</td>
        <td style="text-align:right">${formatLang(o.amount_total, digits=2)}</td>
    </tr>
    </tfoot>
    <br>
  </table>
  %endfor
</html>
