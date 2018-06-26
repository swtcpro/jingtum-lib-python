'use strict'

#BN = require('bn.js')

#elliptic = require('../../elliptic')
#utils = elliptic.utils
import math
import utils

def Signature(self, options, enc):
    if isinstance(options, Signature):
        return options

    if self._importDER(options, enc):
        return

    assert options.r and options.s, 'Signature without r or s'
    self.r = BN(options.r, 16)
    self.s = BN(options.s, 16)
    if (not options.recoveryParam):
        self.recoveryParam = None
    else:
        self.recoveryParam = options.recoveryParam

def Position(self):
    self.place = 0

def getLength(buf, p):
    p.place += 1
    initial = buf[p.place]
    if not(initial & 0x80):
        return initial
    octetLen = initial & 0xf
    val = 0
    i = 0
    off = p.place
    while i < octetLen:
        val <<= 8
        val |= buf[off]
        i +=1
        off += 1

    p.place = off
    return val

def rmPadding(buf):
    i = 0
    len = buf.length - 1
    while (not buf[i] and not(buf[i + 1] & 0x80) and i < len):
        i += 1
    if (i == 0):
        return buf
    return buf.slice(i)

def _importDER(data, enc):
    data = utils.toArray(data, enc)
    p = Position()
    p.place += 1
    if (data[p.place] != 0x30):
        return False
    len = getLength(data, p)
    if ((len + p.place) != len(data)):
        return False
    p.place += 1
    if (data[p.place] != 0x02):
        return False
    rlen = getLength(data, p)
    r = data.slice(p.place, rlen + p.place)
    p.place += rlen
    p.place += 1
    if (data[p.place] != 0x02):
        return False
    slen = getLength(data, p)
    if (data.length != slen + p.place):
        return False
    s = data.slice(p.place, slen + p.place)
    if (r[0] == 0 and (r[1] & 0x80)):
        r = r.slice(1)
    if (s[0] == 0 and (s[1] & 0x80)):
        s = s.slice(1)
    
    self.r = BN(r)
    self.s = BN(s)
    self.recoveryParam = None

    return True

def constructLength(arr, len):
    if (len < 0x80):
        arr.push(len)
        return
    octets = 1 + (math.log(len) / math.log(2) >> 3)
    arr.push(octets | 0x80)
    octets -= 1
    while True:
        arr.push((len >> (octets << 3)) & 0xff)
        octets -= 1
    arr.push(len)

def toDER(self, enc):
    r = self.r.toArray()
    s = self.s.toArray()

    # Pad values
    if (r[0] & 0x80):
        r = [0].concat(r)
    # Pad values
    if (s[0] & 0x80):
        s = [0].concat(s)

    r = rmPadding(r)
    s = rmPadding(s)

    while (not s[0] and not(s[1] & 0x80)):
        s = s.slice(1)
    arr = [0x02]
    constructLength(arr, r.length)
    arr = arr.concat(r)
    arr.push(0x02)
    constructLength(arr, s.length)
    backHalf = arr.concat(s)
    res = [0x30]
    constructLength(res, backHalf.length)
    res = res.concat(backHalf)
    return utils.encode(res, enc)
