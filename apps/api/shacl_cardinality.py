"""Exact SHACL count input contract shared with the browser; no RDF coercion."""
import re
from rdflib import Literal, XSD

COUNT_LIMIT = 10000
# XML Schema integer-derived datatype value spaces (inclusive bounds).
COUNT_TYPES = {
    'integer': (None, None), 'nonNegativeInteger': ('0', None),
    'positiveInteger': ('1', None), 'nonPositiveInteger': (None, '0'),
    'negativeInteger': (None, '-1'), 'long': ('-9223372036854775808', '9223372036854775807'),
    'int': ('-2147483648', '2147483647'), 'short': ('-32768', '32767'), 'byte': ('-128', '127'),
    'unsignedLong': ('0', '18446744073709551615'), 'unsignedInt': ('0', '4294967295'),
    'unsignedShort': ('0', '65535'), 'unsignedByte': ('0', '255'),
}

class CardinalityError(ValueError):
    def __init__(self, code, message):
        super().__init__(message); self.code = code

def _decimal(value):
    digits = value.lstrip('+-').lstrip('0') or '0'
    return value.startswith('-') and digits != '0', digits

def _compare(left, right):
    ln, ld = _decimal(left); rn, rd = _decimal(right)
    if ln != rn:return -1 if ln else 1
    order = (len(ld)>len(rd))-(len(ld)<len(rd)) or (ld>rd)-(ld<rd)
    return -order if ln else order

def read_count(term, default=None):
    if term is None:return default
    datatype = str(term.datatype) if isinstance(term, Literal) else ''
    name = datatype[len(str(XSD)):] if datatype.startswith(str(XSD)) else ''
    if not isinstance(term, Literal) or name not in COUNT_TYPES:
        raise CardinalityError('CARDINALITY_TERM', 'Määrärajoite tarvitsee XSD-kokonaislukuliteraalin (esimerkiksi xsd:int tai xsd:integer), ei merkkijonoa tai muuta RDF-termiä.')
    lexical = str(term).strip(' \t\r\n')
    if re.fullmatch(r'[+-]?[0-9]+', lexical) is None:
        raise CardinalityError('CARDINALITY_LEXICAL', 'Virheellinen kokonaisluvun kirjoitusasu; desimaaliosaa tai eksponenttia ei hyväksytä.')
    low, high = COUNT_TYPES[name]
    if low is not None and _compare(lexical, low)<0 or high is not None and _compare(lexical, high)>0:
        raise CardinalityError('CARDINALITY_VALUE', 'Arvo ei kuulu ilmoitetun '+name+'-tietotyypin arvoavaruuteen.')
    if _compare(lexical, '0')<0:
        raise CardinalityError('CARDINALITY_VALUE', 'sh:minCount ja sh:maxCount eivät saa olla negatiivisia.')
    if _compare(lexical, str(COUNT_LIMIT))>0:
        raise CardinalityError('CARDINALITY_LIMIT', 'Kelvollinen kokonaisluku ylittää generaattorin resurssirajan 10 000.')
    return int(_decimal(lexical)[1])  # Only a verified 0..10000 value reaches conversion.
