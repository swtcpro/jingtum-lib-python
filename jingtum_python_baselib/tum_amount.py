# Represent amounts and currencies objects
# in Jingtum.
# - Numbers in hex are big - endian.

import math,re
from jingtum_python_baselib.wallet import Wallet
from jingtum_python_baselib.utils import hexToBytes
from jingtum_python_baselib.datacheck import isTumCode,isCurrency


bi_xns_max = 9e18


class Amount:
    def __init__(self):
        # Json format:
        # integer: SWT
        # {'value': ..., 'currency': ..., 'issuer': ...}

        #self._value = BigInteger() # None for bad value.Always positive.
        self._offset = 0 # Always 0 for SWT.
        self._is_native = True # Default to SWT.Only valid if value is not None.
        self._is_negative = False
        self._currency = None #  String
        self._issuer = None #  String


    def from_json(j):
        amount=Amount()
        return amount.parse_json(j)

    # Only check the value of the Amount
    #
    def is_valid(j):
        return True

    def currency(self):
        return self._currency

    def is_native(self):
        return self._is_native

    # Remove check of None
    def is_negative(self):
        return self._is_negative

    def is_positive(self):
        return not self.is_zero() and not self.is_negative()

    def is_zero(self):
        return self._value == 0

    def issuer(self):
        return self._issuer

    # Only set the issuer if the input is
    #a valid address.
    def parse_issuer(self,issuer):
        if (Wallet.isValidAddress(issuer)):
            self._issuer = issuer

        return self

    #Convert the input JSON data into
    # a valid Amount object
    # Amount should have 3 properties
    # value
    # issuer / counterparty
    # currency
    # Amount:
    #number: 123456
    # string: "123456"
    # obj:    {"value": 129757.754575,
    #"issuer": " ",
    #"currency": "USD"}
    def parse_json(self,in_json):
        if isinstance(in_json,(int,float)):
            self.parse_swt_value(str(in_json))
        elif isinstance(in_json,str):
            # only allow
            self.parse_swt_value(in_json)
        elif isinstance(in_json,object):
            if not isTumCode(in_json['currency']):
                raise Exception('Amount.parse_json: Input JSON has invalid Tum info!')
            else:
                # AMOUNT could have a field named either as 'issuer' or as 'counterparty' for SWT, self can be undefined
                if (in_json['currency'] != 'SWT'):
                    self._currency = in_json['currency']
                    self._is_native = False
                    if in_json.__contains__('issuer') and in_json['issuer'] is not None:
                        if (Wallet.isValidAddress(in_json['issuer'])):
                            self._issuer = in_json['issuer']
                            # TODO, need to find a better way for extracting the exponent and digits
                            vpow =  float(in_json['value'])
                            vpow = str("%e"%vpow)
                            vpow = vpow[vpow.rfind("e") + 1:].replace("0", "")
                            offset = 15 - int(vpow)
                            factor = math.pow(10, offset)
                            self._value = int(float(in_json['value'])*factor)
                            self._offset = -1 * offset
                        else:
                            raise Exception('Amount.parse_json: Input JSON has invalid issuer info!')
                    else:
                        raise Exception('Amount.parse_json: Input JSON has invalid issuer info!')
                else:
                    self.parse_swt_value(str(in_json['value']))
        else:
            raise Exception('Amount.parse_json: Unsupported JSON type!')
        return self

    # For SWT, only keep as the integer
    #with precision
    def parse_swt_value(self,j):
        if isinstance(j,str):
            m = re.match('^(-?)(\d*)(\.\d{0,6})?$',j)
        if m:
            if (m.group(3) is None):
                # Integer notation
                # Changed to agree with floating, values multiplied by 1, 000, 000.
                self._value = int(float(m.group(2)) * 1e6) #  BigInteger(m[2])
            else:
                # Float notation: values multiplied by 1, 000, 000.
                # only keep 6 digits after the decimal point.
                self._value = int(float(m.group(2) + m.group(3)) * 1e6) # int_part + fraction_part # int_part.add(fraction_part)

            self._is_native = True
            self._offset = 0
            self._is_negative = m.group(1) and self._value != 0

            if self._value > bi_xns_max:
                self._value = None
        else:
            self._value = None

        return self

    # Parse a non - native Tum value for the json wire format.
    # Requires _currency not as SWT!
    def parse_tum_value(self,j):
        self._is_native = False
        if isinstance(j, (int,float)):
            self._is_negative = j < 0
            self._value = math.abs(j)
            self._offset = 0
            self.canonicalize()

        elif isinstance(j, str):
            i = re.match('^ (-?)(\d +)$' ,j)
            d = not i and re.match('^(-?)(\d*)\.(\d*)$',j)
            e = not d and re.match('^(-?)(\d*)e(-?\d+)$',j) #? !e

            if (e):
                # e notation
                self._value = e[2] #  BigInteger(e[2])
                self._offset = int(e[3])
                self._is_negative = e[1]
            elif (d):
                # float notation
                precision = len(d[3])
                #self._value = # integer.multiply(Amount.bi_10.clone().pow(precision)).add(fraction)
                self._offset = -precision
                self._is_negative = d[1]
            elif (i):
                # integer notation
                self._value = i[2] #  BigInteger(i[2])
                self._offset = 0
                self._is_negative = i[1]
            else:
                self._value = None

        else:
            self._value = None

        return self

    #Convert the internal obj to JSON
    def to_json(self):
        if (self._is_native):
            result = self.to_text()
        else:
            amount_json = {
                'value': self._value,
                'currency': self._currency
            }

            if (self._issuer.is_valid()):
                amount_json.issuer = self._issuer
                result = amount_json

        return result

    # Convert the internal Tum Code
    # to byte array
    # for serialization.
    # Input: a string represents the Tum.
    # Output: Bytes array of size 20 (UINT160)
    def tum_to_bytes(self):
        currencyData = []

        i = 0
        while i < 20:
            currencyData.append(0)
            i += 1

        # Only handle the currency with correct symbol
        if isCurrency(self._currency):
            currencyData[12:15] = map(ord, self._currency)
        elif len(self._currency) == 40:
            # for TUM code start with 8
            # should be HEX code
            if re.match('^[0-9A-F]',self._currency):
                currencyData =  hexToBytes(self._currency)
            else:
                raise Exception('Invalid currency code.')

        else:
            raise Exception('Incorrect currency code length.')

        return currencyData

