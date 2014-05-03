# -*- coding: utf-8 -*-
##############################################################################
#
#    Author :  Cristian Salamea cristian.salamea@gnuthink.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import base64
import StringIO
from lxml import etree
from lxml.etree import DocumentInvalid
import os
import datetime
import logging

from osv import osv
from osv import fields

tpIdProv = {
    'ruc' : '01',
    'cedula' : '02',
    'pasaporte' : '03',
}

tpIdCliente = {
    'ruc': '04',
    'cedula': '05',
    'pasaporte': '06'
    }


class wizard_ats(osv.osv_memory):

    _name = 'wizard.ats'
    _description = 'Anexo Transaccional Simplificado'
    __logger = logging.getLogger(_name)

    def _get_period(self, cr, uid, context):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    def _get_company(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id.id

    def act_cancel(self, cr, uid, ids, context):
        return {'type':'ir.actions.act_window_close'}

    def process_lines(self, cr, uid, lines):
        """
        @temp: {'332': {baseImpAir: 0,}}
        @data_air: [{baseImpAir: 0, ...}]
        """
        data_air = []
        flag = False
        temp = {}
        for line in lines:
            if line.tax_group in ['ret_ir', 'no_ret_ir']:
                if not temp.get(line.base_code_id.code):
                    temp[line.base_code_id.code] = {'baseImpAir': 0, 'valRetAir': 0}
                temp[line.base_code_id.code]['baseImpAir'] += line.base_amount
                temp[line.base_code_id.code]['codRetAir'] = line.base_code_id.code
                temp[line.base_code_id.code]['porcentajeAir'] = line.percent and float(line.percent) or 0.00
                temp[line.base_code_id.code]['valRetAir'] += abs(line.amount)
        for k,v in temp.items():
            data_air.append(v)
        return data_air

    def convertir_fecha(self, fecha):
        """
        fecha: '2012-12-15'
        return: '15/12/2012'
        """
        f = fecha.split('-')
        date = datetime.date(int(f[0]), int(f[1]), int(f[2]))
        return date.strftime('%d/%m/%Y')

    def _get_ventas(self, cr, period_id, journal_id=False):
        sql_ventas = "SELECT sum(amount_vat+amount_vat_cero+amount_novat) AS base \
                      FROM account_invoice \
                      WHERE type = 'out_invoice' AND state IN ('open','paid') AND period_id = %s" % period_id
        if journal_id:
            where = " AND journal_id=%s" % journal_id
            sql_ventas += where
        cr.execute(sql_ventas)
        result = cr.fetchone()[0]
        return '%.2f' % (result and result or 0.00)

    def _get_ret_iva(self, invoice):
        """
        Return (valorRetServicios, valorRetServ100)
        """
        retServ = 0
        retServ100 = 0
        for tax in invoice.tax_line:
            if tax.tax_group == 'ret_vat_srv':
                if tax.percent == '100':
                    retServ100 += abs(tax.tax_amount)
                else:
                    retServ += abs(tax.tax_amount)
        return retServ, retServ100

    def act_export_ats(self, cr, uid, ids, context):
        conret = 0
        inv_obj = self.pool.get('account.invoice')
        journal_obj = self.pool.get('account.journal')
        wiz = self.browse(cr, uid, ids)[0]
        period_id = wiz.period_id.id
        ruc = wiz.company_id.partner_id.ced_ruc
        ats = etree.Element('iva')
        etree.SubElement(ats, 'TipoIDInformante').text = 'R'
        etree.SubElement(ats, 'IdInformante').text = str(ruc)
        etree.SubElement(ats, 'razonSocial').text = wiz.company_id.name
        period = self.pool.get('account.period').browse(cr, uid, [period_id])[0]
        etree.SubElement(ats, 'Anio').text = time.strftime('%Y',time.strptime(period.date_start, '%Y-%m-%d'))        
        etree.SubElement(ats, 'Mes'). text = time.strftime('%m',time.strptime(period.date_start, '%Y-%m-%d'))
        etree.SubElement(ats, 'numEstabRuc').text = wiz.num_estab_ruc.zfill(3)
        total_ventas = self._get_ventas(cr, period_id)
        etree.SubElement(ats, 'totalVentas').text = total_ventas
        etree.SubElement(ats, 'codigoOperativo').text = 'IVA'
        compras = etree.Element('compras')
        '''Facturas de Compra con retenciones '''
        inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid']),
                                            ('period_id','=',period_id),
                                            ('type','in',['in_invoice','liq_purchase']),
                                            ('company_id','=',wiz.company_id.id)])
        self.__logger.info("Compras registradas: %s" % len(inv_ids))        
        for inv in inv_obj.browse(cr, uid, inv_ids):
            detallecompras = etree.Element('detalleCompras')
            etree.SubElement(detallecompras, 'codSustento').text = inv.sustento_id.code
            if not inv.partner_id.ced_ruc:
                raise osv.except_osv('Datos incompletos', 'No ha ingresado toda los datos de %s' % inv.partner_id.name)
            etree.SubElement(detallecompras, 'tpIdProv').text = tpIdProv[inv.partner_id.type_ced_ruc]
            etree.SubElement(detallecompras, 'idProv').text = inv.partner_id.ced_ruc
            if inv.auth_inv_id:
                tcomp = inv.auth_inv_id.type_id.code
            else:
                tcomp = '03'
            etree.SubElement(detallecompras, 'tipoComprobante').text = tcomp
            etree.SubElement(detallecompras, 'fechaRegistro').text = self.convertir_fecha(inv.date_invoice)
            if inv.type == 'in_invoice':
                se = inv.auth_inv_id.serie_entidad
                pe = inv.auth_inv_id.serie_emision
                sec = '%09d' % int(inv.reference)
                auth = inv.auth_inv_id.name
            elif inv.type == 'liq_purchase':
                se = inv.journal_id.auth_id.serie_entidad
                pe = inv.journal_id.auth_id.serie_emision
                sec = inv.number[8:]
                auth = inv.journal_id.auth_id.name
            etree.SubElement(detallecompras, 'establecimiento').text = se
            etree.SubElement(detallecompras, 'puntoEmision').text = pe
            etree.SubElement(detallecompras, 'secuencial').text = sec
            etree.SubElement(detallecompras, 'fechaEmision').text = self.convertir_fecha(inv.date_invoice)
            etree.SubElement(detallecompras, 'autorizacion').text = auth
            etree.SubElement(detallecompras, 'baseNoGraIva').text = inv.amount_novat==0 and '0.00' or '%.2f'%inv.amount_novat
            etree.SubElement(detallecompras, 'baseImponible').text = '%.2f'%inv.amount_vat_cero
            etree.SubElement(detallecompras, 'baseImpGrav').text = '%.2f'%inv.amount_vat
            etree.SubElement(detallecompras, 'montoIce').text = '0.00'
            etree.SubElement(detallecompras, 'montoIva').text = '%.2f'%inv.amount_tax
            etree.SubElement(detallecompras, 'valorRetBienes').text = '%.2f'%abs(inv.taxed_ret_vatb)
            valorRetServicios, valorRetServ100 = self._get_ret_iva(inv)
            etree.SubElement(detallecompras, 'valorRetServicios').text = '%.2f'%valorRetServicios
            etree.SubElement(detallecompras, 'valRetServ100').text = '%.2f'%valorRetServ100
            pagoExterior = etree.Element('pagoExterior')
            etree.SubElement(pagoExterior, 'pagoLocExt').text = '01'
            etree.SubElement(pagoExterior, 'paisEfecPago').text = 'NA'
            etree.SubElement(pagoExterior, 'aplicConvDobTrib').text = 'NA'
            etree.SubElement(pagoExterior, 'pagExtSujRetNorLeg').text = 'NA'
            detallecompras.append(pagoExterior)
            if inv.amount_pay >= wiz.pay_limit:
                formasDePago = etree.Element('formasDePago')
                etree.SubElement(formasDePago, 'formaPago').text = '02'
                detallecompras.append(formasDePago)
            if inv.retention_ir or inv.no_retention_ir:
                air = etree.Element('air')
                data_air = self.process_lines(cr, uid, inv.tax_line)
                for da in data_air:
                    detalleAir = etree.Element('detalleAir')
                    etree.SubElement(detalleAir, 'codRetAir').text = da['codRetAir']
                    etree.SubElement(detalleAir, 'baseImpAir').text = '%.2f' % da['baseImpAir']
                    etree.SubElement(detalleAir, 'porcentajeAir').text = '%.2f' % da['porcentajeAir']
                    etree.SubElement(detalleAir, 'valRetAir').text = '%.2f' % da['valRetAir']
                    air.append(detalleAir)
                detallecompras.append(air)
            flag = False            
            if inv.retention_id and (inv.retention_ir or inv.retention_vat):
                flag = True
                etree.SubElement(detallecompras, 'estabRetencion1').text = flag and inv.journal_id.auth_ret_id.serie_entidad or '000'
                etree.SubElement(detallecompras, 'ptoEmiRetencion1').text = flag and inv.journal_id.auth_ret_id.serie_emision or '000'
                etree.SubElement(detallecompras, 'secRetencion1').text = flag and inv.retention_id.number[6:] or '%09d'%0
                etree.SubElement(detallecompras, 'autRetencion1').text = flag and inv.journal_id.auth_ret_id.name or '%010d'%0
                etree.SubElement(detallecompras, 'fechaEmiRet1').text = flag and self.convertir_fecha(inv.retention_id.date)
            ## etree.SubElement(detallecompras, 'docModificado').text = '0'
            ## etree.SubElement(detallecompras, 'estabModificado').text = '000'
            ## etree.SubElement(detallecompras, 'ptoEmiModificado').text = '000'
            ## etree.SubElement(detallecompras, 'secModificado').text = '0'
            ## etree.SubElement(detallecompras, 'autModificado').text = '0000'
            compras.append(detallecompras)
        ats.append(compras)
        if float(total_ventas) > 0:
            """VENTAS DECLARADAS"""
            ventas = etree.Element('ventas')
            inv_ids = inv_obj.search(cr, uid, [('state','in',['open','paid']),
                                               ('period_id','=',period_id),
                                               ('type','=','out_invoice'),
                                               ('company_id','=',wiz.company_id.id)])
            pdata = {}
            self.__logger.info("Ventas registradas: %s" % len(inv_ids))
            for inv in inv_obj.browse(cr, uid, inv_ids):
                if not pdata.get(inv.partner_id.id, False):
                    partner_data = {inv.partner_id.id: {'tpIdCliente': inv.partner_id.type_ced_ruc,
                                                        'idCliente': inv.partner_id.ced_ruc,
                                                        'numeroComprobantes': 0,
                                                        'basenoGraIva': 0,
                                                        'baseImponible': 0,
                                                        'baseImpGrav': 0,
                                                        'montoIva': 0,
                                                        'valorRetRenta': 0,
                                                        'valorRetIva': 0}}
                    pdata.update(partner_data)
                pdata[inv.partner_id.id]['numeroComprobantes'] += 1
                pdata[inv.partner_id.id]['basenoGraIva'] += inv.amount_novat
                pdata[inv.partner_id.id]['baseImponible'] += inv.amount_vat_cero
                pdata[inv.partner_id.id]['baseImpGrav'] += inv.amount_vat
                pdata[inv.partner_id.id]['montoIva'] += inv.amount_tax
                pdata[inv.partner_id.id]['tipoComprobante'] = inv.journal_id.auth_id.type_id.code
                if inv.retention_ir:
                    data_air = self.process_lines(cr, uid, inv.tax_line)
                    for dt in data_air:
                        pdata[inv.partner_id.id]['valorRetRenta'] += dt['valRetAir']
                pdata[inv.partner_id.id]['valorRetIva'] += abs(inv.taxed_ret_vatb) + abs(inv.taxed_ret_vatsrv)

            for k, v in pdata.items():
                detalleVentas = etree.Element('detalleVentas')
                etree.SubElement(detalleVentas, 'tpIdCliente').text = tpIdCliente[v['tpIdCliente']]
                etree.SubElement(detalleVentas, 'idCliente').text = v['idCliente']
                etree.SubElement(detalleVentas, 'tipoComprobante').text = v['tipoComprobante']
                etree.SubElement(detalleVentas, 'numeroComprobantes').text = str(v['numeroComprobantes'])
                etree.SubElement(detalleVentas, 'baseNoGraIva').text = '%.2f' % v['basenoGraIva']
                etree.SubElement(detalleVentas, 'baseImponible').text = '%.2f' % v['baseImponible']
                etree.SubElement(detalleVentas, 'baseImpGrav').text = '%.2f' % v['baseImpGrav']
                etree.SubElement(detalleVentas, 'montoIva').text = '%.2f' % v['montoIva']
                etree.SubElement(detalleVentas, 'valorRetIva').text = '%.2f' % v['valorRetIva']
                etree.SubElement(detalleVentas, 'valorRetRenta').text = '%.2f' % v['valorRetRenta']
                ventas.append(detalleVentas)
            ats.append(ventas)
        """ Ventas establecimiento """
        ventasEstablecimiento = etree.Element('ventasEstablecimiento')
        jour_ids = journal_obj.search(cr, uid, [('type','=','sale')])
        for j in journal_obj.browse(cr, uid, jour_ids):
            ventaEst = etree.Element('ventaEst')
            etree.SubElement(ventaEst, 'codEstab').text = j.auth_id.serie_emision
            etree.SubElement(ventaEst, 'ventasEstab').text = self._get_ventas(cr, period_id, j.id)
            ventasEstablecimiento.append(ventaEst)
        ats.append(ventasEstablecimiento)
        """Documentos Anulados"""
        anulados = etree.Element('anulados')
        inv_ids = inv_obj.search(cr, uid, [('state','=','cancel'),
                                            ('period_id','=',period_id),
                                            ('type','=','out_invoice'),
                                            ('company_id','=',wiz.company_id.id)])
        self.__logger.info("Ventas Anuladas: %s" % len(inv_ids))        
        for inv in inv_obj.browse(cr, uid, inv_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = inv.journal_id.auth_id.type_id.code
            etree.SubElement(detalleAnulados, 'establecimiento').text = inv.journal_id.auth_id.serie_entidad
            etree.SubElement(detalleAnulados, 'puntoEmision').text = inv.journal_id.auth_id.serie_emision
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(inv.number[8:]))
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(inv.number[8:]))
            etree.SubElement(detalleAnulados, 'autorizacion').text = inv.journal_id.auth_id.name
            anulados.append(detalleAnulados)
        liq_ids = inv_obj.search(cr, uid, [('state','=','cancel'),
                                            ('period_id','=',period_id),
                                            ('type','=','liq_purchase'),
                                            ('company_id','=',wiz.company_id.id)])
        for inv in inv_obj.browse(cr, uid, liq_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = inv.journal_id.auth_id.type_id.code
            etree.SubElement(detalleAnulados, 'establecimiento').text = inv.journal_id.auth_id.serie_entidad
            etree.SubElement(detalleAnulados, 'puntoEmision').text = inv.journal_id.auth_id.serie_emision
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(inv.number[8:]))
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(inv.number[8:]))
            etree.SubElement(detalleAnulados, 'autorizacion').text = inv.journal_id.auth_id.name
            anulados.append(detalleAnulados)
        retention_obj = self.pool.get('account.retention')
        ret_ids = retention_obj.search(cr, uid, [('state','=','cancel'),
                                                 ('in_type','=','ret_out_invoice'),
                                                 ('date','>=',wiz.period_id.date_start),
                                                 ('date','<=',wiz.period_id.date_stop)])
        for ret in retention_obj.browse(cr, uid, ret_ids):
            detalleAnulados = etree.Element('detalleAnulados')
            etree.SubElement(detalleAnulados, 'tipoComprobante').text = ret.auth_id.type_id.code
            etree.SubElement(detalleAnulados, 'establecimiento').text = ret.auth_id.serie_entidad
            etree.SubElement(detalleAnulados, 'puntoEmision').text = ret.auth_id.serie_emision
            etree.SubElement(detalleAnulados, 'secuencialInicio').text = str(int(ret.number[8:]))
            etree.SubElement(detalleAnulados, 'secuencialFin').text = str(int(ret.number[8:]))
            etree.SubElement(detalleAnulados, 'autorizacion').text = ret.auth_id.name
            anulados.append(detalleAnulados)
        ats.append(anulados)
        file_path = os.path.join(os.path.dirname(__file__), 'XSD/ats.xsd')
        schema_file = open(file_path)
        file_ats = etree.tostring(ats, pretty_print=True, encoding='iso-8859-1')
        #validata schema
        xmlschema_doc = etree.parse(schema_file)
        xmlschema = etree.XMLSchema(xmlschema_doc)
        if not wiz.no_validate:
            try:
                xmlschema.assertValid(ats)
            except DocumentInvalid as e:
                raise osv.except_osv('Error de Datos', """El sistema generó el XML pero los datos no pasan la validación XSD del SRI.
                \nLos errores mas comunes son:\n* RUC,Cédula o Pasaporte contiene caracteres no válidos.\n* Números de documentos están duplicados.\n\nEl siguiente error contiene el identificador o número de documento en conflicto:\n\n %s""" % str(e))
        buf = StringIO.StringIO()
        buf.write(file_ats)
        out=base64.encodestring(buf.getvalue())
        buf.close()
        name = "%s%s%s.XML" % ("AT", wiz.period_id.name[:2], wiz.period_id.name[3:8])
        return self.write(cr, uid, ids, {'state': 'export', 'data': out, 'name': name})        
        
    _columns = {
        'name' : fields.char('Nombre de Archivo', size=50, readonly=True),
        'period_id' : fields.many2one('account.period', 'Periodo'),
        'company_id': fields.many2one('res.company', 'Compania'),
        'num_estab_ruc': fields.char('Num. de Establecimientos', size=3, required=True),
        'pay_limit': fields.float('Limite de Pago'),
        'data' : fields.binary('Archivo XML'),
        'no_validate': fields.boolean('No Validar'),
        'state' : fields.selection((('choose', 'choose'),
                                    ('export', 'export'))),        
        }

    _defaults = {
        'state' : 'choose',
        'period_id': _get_period,
        'company_id': _get_company,
        'pay_limit': 1000.00,
        'num_estab_ruc': '001'
    }    

wizard_ats()
