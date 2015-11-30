# -*- coding: utf-8 -*-
from urllib import urlretrieve
import requests

def validate_from_sri():
    captcha_url == "https://declaraciones.sri.gob.ec/facturacion-internet/images/jcaptcha.jpg"
    SRI_URL = "https://declaraciones.sri.gob.ec/facturacion-internet/consultas/publico/ruc-datos1.jspa"
    payload = {
        'texto': '0103893954001',
        'opcion': '1',
        'j_captcha_response': 
    }
    res = requests.post(SRI_URL, params=payload)
    import pdb
    pdb.set_trace()
    print res.text
    print res.status_code

validate_from_sri()
