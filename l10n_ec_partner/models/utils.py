# -*- coding: utf-8 -*-

try:
    from stdnum import ec
except ImportError:
    from . import ec


def validar_identifier(identifier, type_identifier):
    if type_identifier == 'cedula':
        return ec.ci.is_valid(identifier)
    elif type_identifier == 'ruc':
        return ec.ruc.is_valid(identifier)
    else:
        return True
