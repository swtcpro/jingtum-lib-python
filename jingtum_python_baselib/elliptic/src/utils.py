# BN = require('bn.js')
# minAssert = require('minimalistic-assert')
# minUtils = require('minimalistic-crypto-utils')

# utils.toArray = minUtils.toArray
# utils.zero2 = minUtils.zero2
# utils.toHex = minUtils.toHex
# utils.encode = minUtils.encode
import re


def toArray(msg, enc=None):
    if isinstance(msg,dict):
        return msg
    if (not msg):
        return []
    res = []

    if not isinstance(msg, str):
        i = 0
        while i < len(msg):
            res.append(msg[i] | 0)
            i += 1
        return res

    if (enc == 'hex'):
        msg = re.sub(r'[^a-z0-9]+', '', msg, flags=re.I)
        if ((len(msg) % 2) != 0):
            msg = '0' + msg
        i = 0
        while i < len(msg):
            res.append(int(msg[i] + msg[i + 1], 16))
            i += 2
    else:
        i = 0
        while i < len(msg):
            c = ord(msg[i])
            hi = c >> 8
            lo = c & 0xff
            if (hi):
                res.append(hi)
                res.append(lo)
            else:
                res.append(lo)
            i += 1
    return res

def zero2(word):
    if (len(word) == 1):
        return '0' + word
    else:
        return word

def toHex(msg):
    res = ''
    i = 0
    while i < len(msg):
        res += zero2(hex(msg[i]).replace('0x', ''))
        i += 1
    return res

def encode(arr, enc=None):
    if (enc == 'hex'):
        return toHex(arr)
    else:
        return arr

# Represent num in a w-NAF form
def getNAF(num, w):
    naf = []
    ws = 1 << (w + 1)
    k = num.clone()
    while (k.cmpn(1) >= 0):
        if (k.isOdd()):
            mod = k.andln(ws - 1)
            if (mod > (ws >> 1) - 1):
                z = (ws >> 1) - mod
            else:
                z = mod
            k.isubn(z)
        else:
            z = 0
        naf.append(z)

        # Optimization, shift by word if possible
        if (k.cmpn(0) != 0 and k.andln(ws - 1) == 0):
            shift = (w + 1)
        else:
            shift = 1

        i = 1
        while i < shift:
            naf.append(0)
            i += 1
        k.iushrn(shift)

    return naf


# Represent k1, k2 in a Joint Sparse Form
def getJSF(k1, k2):
    jsf = [
        [],
        []
    ]

    k1 = k1.clone()
    k2 = k2.clone()
    d1 = 0
    d2 = 0
    while (k1.cmpn(-d1) > 0 or k2.cmpn(-d2) > 0):

        # First phase
        m14 = (k1.andln(3) + d1) & 3
        m24 = (k2.andln(3) + d2) & 3
        if (m14 == 3):
            m14 = -1
        if (m24 == 3):
            m24 = -1
        if ((m14 & 1) == 0):
            u1 = 0
        else:
            m8 = (k1.andln(7) + d1) & 7
            if ((m8 == 3 or m8 == 5) and m24 == 2):
                u1 = -m14
            else:
                u1 = m14
        jsf[0].append(u1)

        if ((m24 & 1) == 0):
            u2 = 0
        else:
            m8 = (k2.andln(7) + d2) & 7
            if ((m8 == 3 or m8 == 5) and m14 == 2):
                u2 = -m24
            else:
                u2 = m24
        jsf[1].append(u2)

        # Second phase
        if (2 * d1 == u1 + 1):
            d1 = 1 - d1
        if (2 * d2 == u2 + 1):
            d2 = 1 - d2
        k1.iushrn(1)
        k2.iushrn(1)

    return jsf

"""
def cachedProperty(self, obj, name, computer):
    key = '_' + name
    obj[name] = cachedProperty:
        if self[key]:
            return self[key]
        else:
            self[key]=computer.call(self)
            return computer.call(self)
"""

def parseBytes(bytes):
    if isinstance(bytes, str):
        return toArray(bytes, 'hex')
    else:
        return bytes

def intFromLE(bytes):
    return BN(bytes, 'hex', 'le')