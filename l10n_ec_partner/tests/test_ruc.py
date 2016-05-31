# -*- coding: utf-8 -*-

import requests


def validate_from_sri():
    captcha_url = "https://declaraciones.sri.gob.ec/facturacion-internet/images/jcaptcha.jpg"  # noqa
    SRI_URL = "https://declaraciones.sri.gob.ec/facturacion-internet/consultas/publico/ruc-datos1.jspa"  # noqa
    payload = {
        'texto': '0103893954001',
        'opcion': '1',
        'j_captcha_response': 0
    }
    res = requests.post(SRI_URL, params=payload)
    capt_res = requests.get(captcha_url)
    return res, capt_res


validate_from_sri()
