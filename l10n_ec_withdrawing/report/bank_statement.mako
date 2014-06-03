<html>
    <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
        <script>
            function subst() {
            var vars={};
            var x=document.location.search.substring(1).split('&');
            for(var i in x) {var z=x[i].split('=',2);vars[z[0]] = unescape(z[1]);}
            var x=['frompage','topage','page','webpage','section','subsection','subsubsection'];
            for(var i in x) {
            var y = document.getElementsByClassName(x[i]);
            for(var j=0; j<y.length; ++j) y[j].textContent = vars[x[i]];
                }
            }
        </script>
        <style type="text/css">
            ${css}
        </style>
    </head>
    <body style="border:0; margin: 0;" onload="subst()">
        <table class="header" style="border-bottom: 0px solid black; width: 100%">
            <tr>
                <td>${helper.embed_logo_by_name('camptocamp_logo')|n}</td>
                <td style="text-align:right"> </td>
            </tr>
            <tr>
                <td><br/></td>
                <td style="text-align:right"> </td>
            </tr>
            <tr>
                <td>${company.partner_id.name |entity}</td>
                <td/>
            </tr>
            <tr>
                <td >${company.partner_id.address and company.partner_id.address[0].street or ''|entity}</td>
                <td/>
            </tr>
            <tr>
                <td>Phone: ${company.partner_id.address and company.partner_id.address[0].phone or ''|entity} </td>
                <td/>
            </tr>
            <tr>
                <td>Mail: ${company.partner_id.address and company.partner_id.address[0].email or ''|entity}<br/></td>
            </tr>
        </table> ${_debug or ''|n} </body>
</html>


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
        left: 50px;
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
    <tr>
      <td><b>Número:</b></td><td>${ o.name }</td>
      <td><b>Fecha:</b></td><td>${ o.date }</td>
      <td><b>Banco:</b></td><td>${ o.journal_id.name }</td>
    </tr>
    <tr>
      <td><b>Periodo:</b></td><td>${ o.period_id.name }</td>
      <td><b>Saldo Inicial:</b></td><td style="text-align:right">${ formatLang(o.balance_start, digits=2) }</td>
      <td><b>Saldo Final:</b></td><td style="text-align:right"> ${ formatLang(o.balance_end_real, digits=2) }</td>
    </tr>
  </table>
  <br>
  <table width="80%" class="invoice_line">
      <tr>
        <td style="text-align:center"><b>Fecha Vigencia</b></td>
        <td style="text-align:center"><b>Referencia</b></td>
        <td style="text-align:center"><b>Empresa</b></td>
        <td style="text-align:center"><b>Debe</b></td>
        <td style="text-align:center"><b>Haber</b></td>
      </tr>
    %for line in o.move_line_ids :
    <tbody>
    <tr >
      <td style="text-align:center">${line.date or ''}</td>
      <td style="text-align:center">${line.ref or ''}</td>
      <td style="text-align:center">${line.partner_id.name or ''}</td>
      <td style="text-align:right">${formatLang(line.debit or 0.00, digits=2) }</td>
      <td style="text-align:right">${formatLang(line.credit or 0.00, digits=2) }</td>
    </tr>
    %endfor      
    </tbody>
    <br>
    <br>
    <br>
    <br>
    <tfooter width="100%" class="invoice_line">
      <tr><br></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr></tr>
      <tr>
        <td style="text-align:right">Realizado por: ${ get_user(o) }</td>
        <td style="text-align:right">Revisado por:</td>
        <td style="text-align:right">Aprobador por:</td>
      </tr>
    </tfooter>    
  </table>
  %endfor
</html>
