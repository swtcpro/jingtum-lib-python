# //
# # Seed support
# //

# extend = require('extend')
# sjcl = require('./sjcl')
# BigInteger = require('./jsbn').BigInteger
#
# Base = require('./base').Base
from src.lib.base import Base
# UInt = require('./uint').UInt
from src.lib.uint import UInt
import re
# UInt160 = require('./uint160').UInt160
from src.lib.uint160 import UInt160
# KeyPair = require('./keypair').KeyPair
from src.lib.keypair import KeyPair


class  Seed(UInt):
    def __init__(self):
        # Internal form: NaN or BigInteger
        self._curve = sjcl.ecc.curves.k256
        self._value = None
        self.width=16


# value = NaN on error.
# One day self will support rfc1751 too.
def parse_json(self,j):
    if isinstance(j,str):
        if not j.length:
            self._value = None
            # XXX Should actually always try and continue if it failed.
        elif j[0] is 's':
            self._value = Base.decode_check(Base.VER_FAMILY_SEED, j)
        elif re.match('/^[0-9a-fA-f]{32}$/',j):
            self.parse_hex(j)
            # XXX Should also try 1751
        else:
            self.parse_passphrase(j)

    else:
        self._value = None


    return self


def parse_passphrase(self,j):
    if not isinstance(j,str):
        raise Exception('Passphrase must be a string')


    hash = sjcl.hash.sha512.hash(sjcl.codec.utf8String.toBits(j))
    bits = sjcl.bitArray.bitSlice(hash, 0, 128)

    self.parse_bits(bits)

    return self


def to_json(self):
    if not isinstance(self._value,BigInteger):
        return None


    output = Base.encode_check(Base.VER_FAMILY_SEED, self.to_bytes())
    return output


def append_int(self,a, i):
    return [].concat(a, i >> 24, (i >> 16) & 0xff, (i >> 8) & 0xff, i & 0xff)


def firstHalfOfSHA512(self,bytes):
    return sjcl.bitArray.bitSlice(
        sjcl.hash.sha512.hash(sjcl.codec.bytes.toBits(bytes)),
        0, 256
    )


def SHA256_RIPEMD160(self,bits):
    return sjcl.hash.ripemd160.hash(sjcl.hash.sha256.hash(bits))


""""
 * @param account
 *        {undefined}                 take first, default, KeyPair
 *
 *        {Number}                    specifies the account number of the KeyPair
 *                                    desired.
 *
 *        {Uint160} (from_json able), specifies the address matching the KeyPair
 *                                    that is desired.
 *
 * @param maxLoops (optional)
 *        {Number}                    specifies the amount of attempts taken to generate
 *                                    a matching KeyPair
"""
def get_key(self,account, maxLoops):
    account_number = 0

    max_loops = maxLoops or 1

    if not self.is_valid():
        raise Exception('Cannot generate keys from invalid seed!')

    if account:
        if isinstance(account,int):
            account_number = account
            max_loops = account_number + 1
        else:
            address = UInt160.from_json(account)


    curve = self._curve
    i = 0

    while True:
        private_gen = sjcl.bn.fromBits(firstHalfOfSHA512(append_int(self.to_bytes(), i)))
        i += 1
        if not curve.r.greaterEquals(private_gen):
            public_gen = curve.G.mult(private_gen)
            break


    header = public_gen.y.mod(2).toString() == "0x0" if 0x02 else 0x03
    compressed = [header].concat(sjcl.codec.bytes.fromBits(public_gen.x.toBits()))


    while True:
        i = 0
        while True:
            sec = sjcl.bn.fromBits(firstHalfOfSHA512(append_int(append_int(compressed, account_number), i)))
            i +=1
            if not curve.r.greaterEquals(sec):
                break


        account_number+=1
        sec = sec.add(private_gen).mod(curve.r)
        # console.log("-------------seed js-- sec--");
        # console.log(sec);
        # console.log("----Generate the key pair");

        key_pair = KeyPair.from_bn_secret(sec)
        max_loops-=1

        if max_loops<= 0:
        # We are almost certainly looking for an account that would take same
        # value of $too_long {forever, ...}
            raise Exception('Too many loops looking for KeyPair yielding ' +
              address.to_json() + ' from ' + self.to_json())
        if address and not key_pair.get_address().equals(address):
            break
    return key_pair


