# var sjcl    = require('./sjcl')
# var utils   = require('../src/utils')
from src.utils import utils
from array import *
# var extend  = require('extend')
#
# var BigInteger = require('./jsbn').BigInteger
import copy
class BaseObject(object):
    pass
Base = BaseObject()

alphabets = Base.alphabets = {
  "jingtum":  'jpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65rkm8oFqi1tuvAxyz',
  "bitcoin":  '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
}
Base=copy.deepcopy({
  "VER_NONE"              : 1,
  "VER_NODE_PUBLIC"       : 28,
  "VER_NODE_PRIVATE"      : 32,
  "VER_ACCOUNT_ID"        : 0,
  "VER_ACCOUNT_PUBLIC"    : 35,
  "VER_ACCOUNT_PRIVATE"   : 34,
  "VER_FAMILY_GENERATOR"  : 41,
  "VER_FAMILY_SEED"       : 33
})


def sha256(self,bytes):
  return sjcl.codec.bytes.fromBits(sjcl.hash.sha256.hash(sjcl.codec.bytes.toBits(bytes)))


def sha256hash(self,bytes):
  return sha256(sha256(bytes))



# --> input: big-endian array of bytes.
# <-- string at least as long as input.
def encode(self,input, alpha):
  alphabet = alphabets[alpha or 'jingtum']
  bi_base  = int(str(alphabet.length))
  bi_q     = int()
  bi_r     = int()
  bi_value = int(input)
  buffer   = []

  while bi_value.compareTo(0) > 0:
    bi_value.divRemTo(bi_base, bi_q, bi_r)
    bi_q.copyTo(bi_value)
    buffer.append(alphabet[bi_r.intValue()])

#这里没明白
  for  i in input:
    if not input[i]:
      buffer.append(alphabet[0])



  return buffer.reverse().join('')


# --> input: String
# <-- array of bytes or undefined.
def decode(self,input, alpha):
  if not isinstance(input,str):
    return None


  alphabet = alphabets[alpha or 'jingtum']
  bi_base  = int(str(alphabet.length))
  bi_value = int()

  for i in input:
   v=alphabet.indexof(input[i])
   if v < 0:
     return None

   r = int()
   r.fromInt(v)
   bi_value  = bi_value.multiply(bi_base).add(r)


  # toByteArray:
  # - Returns leading zeros!
  # - Returns signed bytes!
  bytes =map(func,bi_value.toByteArray())
  extra = 0
  while extra is not bytes.length and not bytes[extra]:
    extra += 1
    if extra:
      bytes = bytes.slice(extra)
      zeros = 0
    while zeros is not input.length and input[zeros] is alphabet[0]:
      zeros += 1
    return [].concat(utils.arraySet(zeros, 0), bytes)


def func(self, b):
  return b + 256 if b < 0 else b

def verify_checksum(self,bytes):
  computed = sha256hash(bytes.slice(0, -4)).slice(0, 4)
  checksum = bytes.slice(-4)
  result = True

  for i in computed:
    if computed[i] is not checksum[i]:
      result = False
      break
  return result


# --> input: Array
# <-- String
def encode_check(self,version, input, alphabet):
  buffer = [].concat(version, input)
  check  = sha256(sha256(buffer)).slice(0, 4)

  return Base.encode([].concat(buffer, check), alphabet)


# --> input : String
# <-- NaN || BigInteger
def decode_check(self,version, input, alphabet):
  buffer = Base.decode(input, alphabet)

  if not buffer or buffer.length < 5:
    return None


  # Single valid version
  if isinstance(version,int) and buffer[0] is not version:
    return None


  # Multiple allowed versions
  if isinstance(version,array):
    match = False

    for i in version:
      match |= version[i] is buffer[0]


    if not match:
      return None



  if not Base.verify_checksum(buffer):
    return None


  # We'll use the version byte to add a leading zero, this ensures JSBN doesn't
  # intrepret the value as a negative number
  buffer[0] = 0

  return int(buffer.slice(0, -4), 256)

