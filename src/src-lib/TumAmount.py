# Represent amounts and currencies objects
# in Jingtum.
# - Numbers in hex are big-endian.

# var extend = require('extend')
# var base_wallet = require('jingtum-base-lib').Wallet
# var BigInteger = require('bn.js')
# var isTumCode = require('./DataCheck').isTumCode
import copy
import re
#
# Amount class in the style of Java's BigInteger class
# https://docs.oracle.com/javase/7/docs/api/java/math/BigInteger.html
#

consts = {
    "currency_xns": 0,
    "currency_one": 1,
    "xns_precision": 6,

    # BigInteger values prefixed with bi_.
    "bi_5": 5,  # new BigInteger('5'),
    "bi_7": 7,  # new BigInteger('7'),
    "bi_10": 10,  # new BigInteger('10'),
    "bi_1e14": 1e14,  # new BigInteger(String(1e14)),
    "bi_1e16": 1e16,  # new BigInteger(String(1e16)),
    "bi_1e17": 1e17,  # new BigInteger(String(1e17)),
    "bi_1e32": 1e32,  # new BigInteger('100000000000000000000000000000000'),
    "bi_man_max_value": 9999999999999999,  # new BigInteger('9999999999999999'),
    "bi_man_min_value": 1e15,  # new BigInteger('1000000000000000'),
    "bi_xns_max": 9e18,  # new BigInteger('9000000000000000000'), # Json wire limit.
    "bi_xns_min": -9e18,  # new BigInteger('-9000000000000000000'),# Json wire limit.
    "bi_xns_unit": 1e6,  # new BigInteger('1000000'),

    "cMinOffset": -96,
    "cMaxOffset": 80,

    # Maximum possible amount for non-SWT currencies using the maximum mantissa
    # with maximum exponent. Corresponds to hex 0xEC6386F26FC0FFFF.
    "max_value": '9999999999999999e80',
    # Minimum possible amount for non-SWT currencies.
    "min_value": '-1000000000000000e-96'
}
class Amount:
    # Json format:
    #  integer : SWT
    #  { 'value' : ..., 'currency' : ..., 'issuer' : ...}
    def __init__(self, remote):
        self._value = int() # NaN for bad value. Always positive.
        self._offset = 0 # Always 0 for SWT.
        self._is_native = True # Default to SWT. Only valid if value is not NaN.
        self._is_negative = False
        self._currency = None#new stintr
        self._issuer = None#new str

        # Add constants to Amount class
        copy.deepcopy(Amount, consts)







    def from_json(self,j):
        return (Amount()).parse_json(j)


#Only check the value of the Amount
#
    def is_valid(self,j):
        #print("TODO: decide if the input is a valid amount obj")
        return True



    def currency(self):
        return self._currency



    def is_native(self):
        return self._is_native


    #Remove check of NaN
    def is_negative(self):
        return self._is_negative


    def is_positive(self):
        return not self.is_zero() and not self.is_negative()


    def is_zero(self):
        return self._value.isZero()



    def issuer(self):
        return self._issuer


#
# Only set the issuer if the input is
 # a valid address.
#
    def parse_issuer(self,issuer):
        if base_wallet.isValidAddress(issuer):
            self._issuer = issuer

        return self



# <-> j
#
 # Convert the input JSON data into
 # a valid Amount object
# Amount should have 3 properties
 # value
 # issuer/counterparty
 # currency
 # Amount:
 # number: 123456
 # string: "123456"
 # obj:    {"value": 129757.754575,
  #      "issuer":" ",
  #      "currency":"USD"}
#
def parse_json(self,in_json):
    if isinstance(in_json,int):
        self.parse_swt_value(in_json.toString())
    elif isinstance(in_json,str):
        #only allow
        self.parse_swt_value(in_json)
    elif isinstance(in_json,object):
        if not isTumCode(in_json.currency):
            raise Exception('Amount.parse_json: Input JSON has invalid Tum info!')
        else:
            #AMOUNT could have a field named either as 'issuer'or as 'counterparty' for SWT, this can be Unset
            if not in_json.currency == 'SWT':
                self._currency = in_json.currency
                self._is_native = False
                if not isinstance(in_json.issuer,'undefined') and not in_json.issuer:
                    if base_wallet.isValidAddress(in_json.issuer):
                        self._issuer = in_json.issuer
                        #TODO, need to find a better way for extracting the exponent and digits
                        vpow = int(in_json.value)
                        vpow = str(vpow.toExponential(16))
                        vpow = int(vpow.substr(vpow.lastIndexOf("e") + 1))
                        offset = 15 - vpow
                        factor = 10 ** offset
                        newvalue = in_json.value * factor
                        self._value = int(newvalue, 10)
                        self._offset = -1 * offset
                    else:
                        raise Exception('Amount.parse_json: Input JSON has invalid issuer info!')


                else:
                    raise Exception('Amount.parse_json: Input JSON has invalid issuer info!')

            else:
                self.parse_swt_value(in_json.value.toString())

    else:
        raise Exception('Amount.parse_json: Unsupported JSON type!')
    return self



#
# For SWT, only keep as the integer
# with precision
#
#
def parse_swt_value(self,j):
    m=None
    if isinstance(j,str):
        m=re.match('/^(-?)(\d*)(\.\d{0,6})?$/',j)
    if m:
        if m[3] == None:
            # Integer notation
            #Changed to agree with floating, values multiplied by 1,000,000.
            self._value = m[2] * 1e6;#int(m[2])
        else:
            # Float notation : values multiplied by 1,000,000.
            #only keep 6 digits after the decimal point.
            self._value = (m[2] + m[3]) * 1e6;#int_part+fraction_part;#int_part.add(fraction_part)


        self._is_native = True
        self._offset = 0
        self._is_negative = not not m[1] and self._value is not 0

        if self._value > Amount.bi_xns_max:
            self._value = None

    else:
        self._value = None


    return self


# Parse a non-native Tum value for the json wire format.
# Requires _currency not as SWT!
def parse_tum_value(self,j):
    self._is_native = False
    if isinstance(j,int):
        self._is_negative = j < 0
        self._value = int(abs(j))
        self._offset = 0
        self.canonicalize()
    elif isinstance(j,str):

            i = re.match('/^(-?)(\d+)$/',j)
            d = not i and re.match('/^(-?)(\d*)\.(\d*)$/',j)
            e = not d and re.match('/^(-?)(\d*)e(-?\d+)$/',j);#? not e

            if e:
                # e notation
                self._value = e[2];#new BigInteger(e[2])
                self._offset = int(e[3])
                self._is_negative = not not e[1]
            elif d:
                # float notation
                precision = d[3].length
                self._value =self._offset = -precision
                self._is_negative = not not d[1]
            elif i:
                # integer notation
                self._value = i[2];#new BigInteger(i[2])
                self._offset = 0
                self._is_negative = not not i[1]

            else:
                self._value = None


    else:
        self._value = None


    return self


#
# Convert the internal obj to JSON
#
def to_json(self):
    result=None

    if self._is_native:
        result = self.to_text()
    else:
        amount_json = {
            "value": self._value,
            "currency": self._currency
        }

        if self._issuer.is_valid():
            amount_json.issuer = self._issuer
        result = amount_json


    return result


#
# Convert the internal Tum Code
#  to byte array
# for serialization.
# Input: a string represents the Tum.
# Output: Bytes array of size 20 (UINT160).
#
#
def tum_to_bytes(self):
    currencyData = [20]

    for i in 20:
        currencyData[i] = 0


    #Only handle the currency with correct symbol
    if self._currency.length is 3:
        currencyCode = self._currency.toUpperCase()

        currencyData[12] = currencyCode.charCodeAt(0) & 0xff
        currencyData[13] = currencyCode.charCodeAt(1) & 0xff
        currencyData[14] = currencyCode.charCodeAt(2) & 0xff
    elif self._currency.length is 40:
        #for TUM code start with 8
        #should be HEX code
        if re.match('/^[0-9A-F]/i',self._currency):
            currencyData = int(self._currency, 16).toArray(None, 20)
        else:
            raise Exception('Invalid currency code.')


    else:
        raise Exception('Incorrect currency code length.')


    return currencyData



