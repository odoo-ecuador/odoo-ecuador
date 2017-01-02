# -*- coding: utf-8 -*-

import time
import datetime

STD_FORMAT = '%Y-%m-%d'

XSD_MSG = 'El XML generado no se validó' \
            '\nEerrores mas comunes son:\n' \
            '* RUC,Cédula o Pasaporte contiene caracteres no válidos.' \
            'DETALLE DE ERROR %s'


def convertir_fecha(fecha):
    """
    fecha: '2012-12-15'
    return: '15/12/2012'
    """
    f = fecha.split('-')
    date = datetime.date(int(f[0]), int(f[1]), int(f[2]))
    return date.strftime('%d/%m/%Y')


def get_date_value(date, t='%Y'):
    return time.strftime(t, time.strptime(date, STD_FORMAT))
