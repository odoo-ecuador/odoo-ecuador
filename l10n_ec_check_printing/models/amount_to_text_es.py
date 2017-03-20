# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)

to_19 = ('Cero',  'Uno', 'Dos',  'Tres', 'Cuatro',   'Cinco',   'Seis',
         'Siete', 'Ocho', 'Nueve', 'Diez',   'Once', 'Doce', 'Trece',
         'Catorce', 'Quince', 'Dieciseis', 'Diecisiete',
         'Dieciocho', 'Diecinueve')

tens = ('Veinte', 'Treinta', 'Cuarenta', 'Cincuenta',
        'Sesenta', 'Setenta', 'Ochenta', 'Noventa')

hundreds = ('Ciento', 'Doscientos', 'Trescientos', 'Cuatrocientos',
            'Quinientos', 'Seiscientos', 'Setecientos',
            'Ochocientos', 'Novecientos')
denom = ('',
         'Mil', 'Millon', 'Billon', 'Trillon', 'Quadrillion',
         'Quintillion', 'Sextillion', 'Septillion',
         'Octillion', 'Nonillion',
         'Decillion', 'Undecillion', 'Duodecillion',
         'Tredecillion', 'Quattuordecillion',
         'Sexdecillion', 'Septendecillion', 'Octodecillion',
         'Novemdecillion', 'Vigintillion')


def _convert_nn(val):
    """convert a value < 100 to English.
    """
    if val < 20:
        return to_19[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens)):
        if dval + 10 > val:
            if val % 10:
                if val > 20 and val < 30:
                    return "Veinti"+to_19[val % 10]
                else:
                    return dcap + ' Y ' + to_19[val % 10]
            return dcap


def _convert_nnn(val):
    """
    convert a value < 1000 to english, special cased because
    it is the level that kicks
    off the < 100 special case.
    The rest are more general.  This also allows you to
    get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if val == 100:
            word = "Cien"
        else:
            word = hundreds[rem-1]
        if mod > 0:
            word = word + ' '
    if mod > 0:
        word = word + _convert_nn(mod)
    return word


def english_number(val):
    if val < 100:
        return _convert_nn(val)
    if val < 1000:
        return _convert_nnn(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn(l) + ' ' + denom[didx]
            if r > 0:
                ret = ret + ', ' + english_number(r)
            return ret


def amount_to_text(number, currency):
    number = '%.2f' % number
    list = str(number).split('.')
    start_word = english_number(int(list[0])).upper()
    cents_number = int(list[1])
    final_result = start_word + ' con ' + '%d' % cents_number + '/100'
    return final_result


# Generic functions

_translate_funcs = {'en': amount_to_text}


# TODO: we should use the country AND language (ex: septante VS soixante dix)
def amount_to_text(nbr, lang='en', currency='euro'):
    """ Converts an integer to its textual representation,
    using the language set in the context if any.

        Example::

            1654: thousands six cent cinquante-quatre.
    """
#    if nbr > 10000000:
#        _logger.warning(_("Number too large '%d', can not translate it"))
#        return str(nbr)

    if lang not in _translate_funcs:
        _logger.warning(_("no translation function found for lang: '%s'"), lang)  # noqa
        # TODO: (default should be en) same as above
        lang = 'en'
    return _translate_funcs[lang](abs(nbr), currency)


if __name__ == '__main__':
    lang = 'en'
    amount = 30670.30
    text = amount_to_text(amount, lang)
