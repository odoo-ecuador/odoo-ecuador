import requests

WS_TEST_RECEIV = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
WS_TEST_AUTH = 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'
WS_RECEIV = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantes?wsdl'
WS_AUTH = 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl'

def check_service(env='prueba'):
    if env == 'prueba':
        URL = WS_TEST_RECEIV
    else:
        URL = WS_RECEIV

    for i in [1, 2, 3]:
        try:
            res = requests.head(URL, timeout=3)
            print res.status_code
        except requests.exceptions.RequestException, e:
            print "Error", e
            break
    print i

check_service('prueba')
check_service('a')
