<html>
  <head>
    <meta charset="UTF-8">
    <style>
      body {
        font-family: helvetica, helvetica bold, Arial Bold;
        font-size: 12px;
      }
      div.container {
      }
      div.left, div.right {
        float: left;
      }
      div.left {
        padding-right: 10px;
        width: 49%;
      }
      div.right {
        width: 49%;
      }
      div.logo {
        padding-top_ 10px;
        padding-bottom: 10px;
        text-align: center;
      }
      div.companyinfo {
        border: 1px solid #000000;
        border-radius: 10px 10px 10px 10px;
        -moz-border-radius: 10px 10px 10px 10px;
        -webkit-border-radius: 10px 10px 10px 10px;
      }
      div.invoiceinfo {
        border: 1px solid #000000;
        border-radius: 10px 10px 10px 10px;
        -moz-border-radius: 10px 10px 10px 10px;
        -webkit-border-radius: 10px 10px 10px 10px;
      }
      div.customer {
        width: 99%;
        border: 1px solid #000000;
      }
      div.espacio {
        clear: both;
        height: 10px;
      }
      div.details {
        width: 99%;
      }
      div.details {
      }
      table.content {
        border-collapse: collapse;
      }
      table.content th, table.content td {
        border: 1px solid #000000;
      }
      div.fot1, div.fot2 {
        float: left;
      }
      div.fot1 {
        width: 62%;
        margin: 10px;
        border: 1px solid #000000;
      }
      div.fot2 {
        width: 34%;
        margin-top: -1px;
      }
      .amount {
        text-align: right;
      } 
    </style>
  </head>
  %for o in objects:
  <body>
    <div cass="container">
      <div class="left">
        <div class="logo">
          ${helper.embed_image('png', o.company_id.logo, 180, 75) | n}
        </div>
        <div class="espacio">
        </div>
        <div class="companyinfo">
          <table>
            <tbody>
              <tr>
                <td colspan="3" style="font-size: 14px">
                  <b>${o.company_id.name}</b>
                </td>
              </tr>
              <tr>
                <td colspan="3">
                  ${o.company_id.tradename or ''}
                </td>
              </tr>
              <tr>
                <td><br/><br/><br/><br/></td>
              </tr>
              <tr>
                <td width="20%"><b>Dirección Matriz:</b></td>
                <td width="70%" colspan="2">${o.company_id.street}</td>
              </tr>
              <tr>
                % if o.company_id.street2:
                <td><b>Dirección Sucursal:</b></td>
                <td colspan="2">${o.company_id.street2}</td>
                % else:
                <td></td>
                <td></td>
                % endif
              </tr>
              <tr>
                % if o.company_id.company_registry:
                <td colspan="2"><b>Contribuyente Especial Nro.</b></td>
                <td>${o.company_id.company_registry}</td>
                % else:
                <td></td>
                <td></td>
                %endif
              </tr>
              <tr>
                <td colspan="2"><b>OBLIGADO A LLEVAR CONTABILIDAD</b></td>
                <td width="30%">SI</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="right">
        <div class="invoiceinfo">
          <table>
            <tbody>
              <tr>
                <td colspan="2" style="font-size: 14px">
                  <b>R.U.C.:</b> ${o.company_id.partner_id.ced_ruc}
                </td>
              </tr>
              <tr>
                <td colspan="2" style="font-size: 14px">
                  <b>COMPROBANTE DE RETENCIÓN</b>
                </td>
              </tr>
              <tr>
                <td colspan="2">
                  <b>No. ${o.name[0:3]}-${o.name[3:6]}-${o.name[6:15]}</b>
                </td>
              </tr>
              <tr>
                <td colspan="2">
                  <b>NÚMERO DE AUTORIZACIÓN</b>
                </td>
              </tr>
              <tr>
                <td colspan="2">
                  <b>${o.authorization_number or 'NO ENVIADO'}</b>
                </td>
              </tr>
              <tr>
                <td>FECHA Y HORA DE AUTORIZACIÓN:</td>
                <td>${formatLang(o.authorization_date or '', date_time=True)}</td>
              </tr>
              <tr>
                <td colspan="2">
                  <b>AMBIENTE:</b> PRODUCCIÓN
                </td>
              </tr>
              <tr>
                <td colspan="2">
                  <b>EMISIÓN:</b> NORMAL
                </td>
              </tr>
              <tr>
                <td colspan="2"><b>CLAVE DE ACCESO</b></td>
              </tr>
              <tr>
                <td colspan="2">
                  ${ helper.barcode(o.access_key or '123', htmlAttrs={'width': '350px', 'height': '30px;'}) }
                </td>
              </tr>
              <tr>
                <td colspan="2" style="text-align: center">
                  <b>${o.access_key or '123'}</b>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="espacio">
      </div>
      <div class="customer">
        <table>
          <tbody>
            <tr>
              <td colspan="2"><b>Razón Social / Apellidos y Nombres:</b></td>
              <td>${o.partner_id.name}</td>
              <td><b>Identificación:</b></td>
              <td>${o.partner_id.ced_ruc}</td>
            </tr>
            <tr>
              <td><b>Fecha Emisión:</b></td>
              <td>${o.date}</td>
              <td></td>
              <td></td>
              <td></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="espacio">
      </div>
      <div class="details">
        <table width="100%" class="content">
          <thead>
            <tr>
              <th>Comprobante</th>
              <th>Número</th>
              <th>Fecha Emisión</th>
              <th>Ejercicio Fiscal</th>
              <th>Base Imponible para la Retención</th>
              <th>IMPUESTO</th>
              <th>Porcentaje Retención</th>
              <th>Valor Retenido</th>
            </tr>
          </thead>
          <tbody>
            %for line in o.tax_ids:
            <tr>
              <td style="text-align: center">
                ${line.invoice_id.auth_inv_id.type_id.name}
              </td>
              <td style="text-align: center">
                ${o.num_document[0:3]}-${o.num_document[3:6]}-${o.num_document[6:15]}
              </td>
              <td style="text-align: center">
                ${line.invoice_id.date_invoice}
              </td>
              <td style="text-align: center">
                ${o.period_id.name}
              </td>
              <td class="amount">
                ${formatLang(line.base,digits=2)}
              </td>
              <td style="text-align: center">
                ${line.tax_group in ('ret_vat_b','ret_vat_srv') and 'IVA' or 'RENTA'}
              </td>
              <td style="text-align: center">
                ${line.percent}
              </td>
              <td class="amount">
                ${formatLang(abs(line.amount),digits=2)}
              </td>
            </tr>
            %endfor
          </tbody>
        </table>
      </div>
      <div class="fot1">
        <b style="padding-left: 40px">Información Adicional</b>
        <table>
          <tbody>
            <tr>
              <td>Dirección:</td>
              <td>${o.partner_id.street}, ${o.partner_id.city.name} - ${o.partner_id.state_id.name}</td>
            </tr>
            <tr>
              <td>Teléfono:</td>
              <td>${o.partner_id.phone or ''}</td>
            </tr>
            <tr>
              <td>Correo Electrónico:</td>
              <td>${o.partner_id.email or ''}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </body>
  %endfor
</html>
