# -*- coding: utf-8 -*-

import requests


tipoDocumento = {
    '01': '01',
    '04': '04',
    '05': '05',
    '06': '06',
    '07': '07',
    '18': '01',
}

tipoIdentificacion = {
    'ruc': '04',
    'cedula': '05',
    'pasaporte': '06',
    'venta_consumidor_final': '07',
    'identificacion_exterior': '08',
    'placa': '09',
}

codigoImpuesto = {
    'vat': '2',
    'vat0': '2',
    'ice': '3',
    'other': '5'
}

tabla17 = {
    'vat': '2',
    'vat0': '2',
    'ice': '3',
    'irbpnr': '5'
}

tabla18 = {
    '0': '0',
    '12': '2',
    '14': '3',
    'novat': '6',
    'excento': '7'
}

tabla20 = {
    'ret_ir': '1',
    'ret_vat_b': '2',
    'ret_vat_srv': '2',
    'ret_isd': '6'
}

tabla21 = {
    '10': '9',
    '20': '10',
    '30': '1',
    '50': '11',
    '70': '2',
    '100': '3'
}

codigoImpuestoRetencion = {
    'ret_ir': '1',
    'ret_vat_b': '2',
    'ret_vat_srv': '2',
    'ice': '3',
}

tarifaImpuesto = {
    'vat0': '0',
    'vat': '2',
    'novat': '6',
    'other': '7',
}

MSG_SCHEMA_INVALID = u"El sistema generó el XML pero"
" el comprobante electrónico no pasa la validación XSD del SRI."

SITE_BASE_TEST = 'https://celcer.sri.gob.ec/'
SITE_BASE_PROD = 'https://cel.sri.gob.ec/'
WS_TEST_RECEIV = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl'  # noqa
WS_TEST_AUTH = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'  # noqa
WS_RECEIV = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl'  # noqa
WS_AUTH = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl'  # noqa


def check_service(env='prueba'):
    flag = False
    if env == 'prueba':
        URL = WS_TEST_RECEIV
    else:
        URL = WS_RECEIV

    for i in [1, 2, 3]:
        try:
            res = requests.head(URL, timeout=3)
            flag = True
        except requests.exceptions.RequestException:
            return flag, False
    return flag, res
