# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 钱包依赖的模块
"""
import hashlib
import os
import time
from binascii import hexlify, unhexlify
from random import randint
from ecdsa import curves, SigningKey
from ecdsa.util import sigencode_der

from jingtum_python_baselib.utils import *
from jingtum_python_baselib.base58 import base58

SEED_PREFIX = 33
ACCOUNT_PREFIX = 0
ALPHABET = 'jpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65rkm8oFqi1tuvAxyz'

def hash256(data):
    """
        operation twice
    """
    one256 = unhexlify(hashlib.sha256(data).hexdigest())
    return hashlib.sha256(one256).hexdigest()

def hash512(data):
    """
        operation once
    """
    return unhexlify(hashlib.sha512(data).hexdigest())

def sha256(bytes):
    hash = hashlib.sha256()
    hash.update(bytes)
    return hash.digest()

"""
 * decode encoded input,
 * too small or invalid checksum will throw exception
 * @param {integer} version
 * @param {string} input
 * @returns {buffer}
 * @private
"""
def decode_address(version, input):
    s = base58(ALPHABET)
    bytes = s.decode(input)
    if not bytes or bytes[0] != version or len(bytes) < 5:
        raise Exception('invalid input size')
    computed = sha256(sha256(bytearray(bytes[0:-4])))[0:4]
    checksum = bytes[-4:]
    i = 0
    #print('computed[0] is ', computed[0])
    while i != 4:
        if (computed[i] != checksum[i]):
            raise Exception('invalid checksum')
        i += 1
    return bytes[1:-4]

def get_str(l):
    sss = ""
    while l>0:
        try:
            l, b = divmod(l, 58)
            sss +=  ALPHABET[b:b+1]
        except Exception:
            print("get_str error[%s]."%str(b))
            return None
    return sss[::-1]

"""
 * generate random bytes and encode it to secret
 * @returns {string}
"""
def get_secret(extra="FSQF5356dsdsqdfEFEQ3fq4q6dq4s5d"):
    """
        get a random secret
    """
    try:
        rnd = hexlify(os.urandom(256))
        tim = time.time()
        data = "%s%s%s%s"%(rnd, tim, randint(100000000000, 1000000000000), extra)
        res = int(hash256(data.encode("utf8")), 16)
        seed = '21' + str(res)[:32]
        secretKey = hash256(unhexlify(seed))[:8]
        l = int(seed + secretKey, 16)
    except Exception as e:
        print("get_secret error[%s]."%str(e))
        return None

    return get_str(l)


def root_key_from_seed(seed):
    """This derives your master key the given seed.
    """
    seq = 0
    while True:
        private_gen = from_bytes(first_half_of_sha512(
            b''.join([seed, to_bytes(seq, 4)])))
        seq += 1
        if curves.SECP256k1.order >= private_gen:
            break

    public_gen = curves.SECP256k1.generator * private_gen

    # Now that we have the private and public generators, we apparently
    # have to calculate a secret from them that can be used as a ECDSA
    # signing key.
    secret = i = 0
    public_gen_compressed = ecc_point_to_bytes_compressed(public_gen)
    while True:
        secret = from_bytes(first_half_of_sha512(
            b"".join([
                public_gen_compressed, to_bytes(0, 4), to_bytes(i, 4)])))
        i += 1
        if curves.SECP256k1.order >= secret:
            break
    secret = (secret + private_gen) % curves.SECP256k1.order

    # The ECDSA signing key object will, given this secret, then expose
    # the actual private and public key we are supposed to work with.
    key = SigningKey.from_secret_exponent(secret, curves.SECP256k1)
    # Attach the generators as supplemental data
    key.private_gen = private_gen
    key.public_gen = public_gen
    return key

def first_half_of_sha512(*bytes):
    """As per spec, this is the hashing function used."""
    hash = hashlib.sha512()
    for part in bytes:
        hash.update(part)
    return hash.digest()[:256//8]

def ecc_point_to_bytes_compressed(point, pad=False):
    """
    Also implemented as ``KeyPair.prototype._pub_bits``, though in
    that case it explicitly first pads the point to the bit length of
    the curve prime order value.
    """
    header = b'\x02' if point.y() % 2 == 0 else b'\x03'
    bytes = to_bytes(
        point.x(),
        curves.SECP256k1.order.bit_length()//8 if pad else None)
    return b"".join([header, bytes])


class SecretErrException(Exception):
    pass

def parse_seed(secret):
    """Your Jingtum secret is a seed from which the true private key can
    be derived.
    """
    if not secret[0] == 's':
        raise SecretErrException
    return JingtumBaseDecoder.decode(secret)

def get_jingtum_from_pubkey(pubkey):
    """Given a public key, determine the Jingtum address.
    """
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hashlib.sha256(pubkey).digest())
    return JingtumBaseDecoder.encode(ripemd160.digest())

def get_jingtum_publickey(key):
    """Another helper. Returns the jingtum publickey from the key."""
    pubkey = ecc_point_to_bytes_compressed(key.privkey.public_key.point, pad=True)
    return fmt_hex(pubkey)

def get_jingtum_from_key(key):
    """Another helper. Returns the first jingtum address from the key."""
    pubkey = ecc_point_to_bytes_compressed(key.privkey.public_key.point, pad=True)
    return get_jingtum_from_pubkey(pubkey)

def ecdsa_sign(key, signing_hash, **kw):
    """Sign the given data. The key is the secret returned by
    :func:`root_key_from_seed`.

    The data will be a binary coded transaction.
    """
    r, s = key.sign_number(int(signing_hash, 16), **kw)
    r, s = ecdsa_make_canonical(r, s)
    # Encode signature in DER format
    der_coded = sigencode_der(r, s, None)
    return der_coded

def ecdsa_make_canonical(r, s):
    """Make sure the ECDSA signature is the canonical one.
    """
    # For a canonical signature we want the lower of two possible values for s
    # 0 < s <= n/2
    N = curves.SECP256k1.order
    if not N / 2 >= s:
        s = N - s
    return r, s

def jingtum_sign(key, message):
    return hexlify(ecdsa_sign(key, message, k=3))
