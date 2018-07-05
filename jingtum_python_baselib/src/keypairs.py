# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 钱包依赖的模块
"""
# from brorand import brorand
# from secp256k1 import secp256k1
# from brorand import brorand

# from brorand import brorand
# from secp256k1 import secp256k1
# from brorand import brorand
import hashlib
import random
import base58

from jingtum_python_baselib.src import secp256k1
# from elliptic import ec
# from secp256k1 import secp256k1
from jingtum_python_baselib.src import utils

# ec = EC('secp256k1')

SEED_PREFIX = 33
ACCOUNT_PREFIX = 0
alphabet = 'jpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65rkm8oFqi1tuvAxyz'


def sha256(bytes):
    return hashlib.sha256().update(bytes).digest()


"""
 * concat an item and a buffer
 * @param {integer} item1, should be an integer
 * @param {buffer} buf2, a buffer
 * @returns {buffer} new Buffer
"""


def bufCat0(item1, buf2):
    buf = Buffer(1 + buf2.length)
    buf[0] = item1
    buf2.copy(buf, 1)
    return buf


"""
 * concat one buffer and another
 * @param {buffer} item1, should be an integer
 * @param {buffer} buf2, a buffer
 * @returns {buffer} new Buffer
"""


def bufCat1(buf1, buf2):
    buf = Buffer(buf1.length + buf2.length)
    buf1.copy(buf)
    buf2.copy(buf, buf1.length)
    return buf


"""
 * encode use jingtum base58 encoding
 * including version + data + checksum
 * @param {integer} version
 * @param {buffer} bytes
 * @returns {string}
 * @private
"""


def __encode(self, version, bytes):
    buffer = self.bufCat0(version, bytes)
    checksum = Buffer(sha256(sha256(buffer)).slice(0, 4))
    ret = self.bufCat1(buffer, checksum)
    return base58.b58encode(ret)


"""
 * decode encoded input,
 * too small or invalid checksum will throw exception
 * @param {integer} version
 * @param {string} input
 * @returns {buffer}
 * @private
"""


def __decode(version, input):
    bytes = base58.b58decode(input)
    if not bytes or bytes[0] != version or len(bytes) < 5:
        raise Exception('invalid input size')
    computed = sha256(sha256(bytes.slice(0, -4))).slice(0, 4)
    checksum = bytes.slice(-4)
    i = 0
    while i != 4:
        if computed[i] != checksum[i]:
            raise Exception('invalid checksum')
        i += 1
    return bytes.slice(1, -4)


"""
 * generate random bytes and encode it to secret
 * @returns {string}
"""


def generateSeed():
    randBytes = ''.join(random.choice(alphabet) for _ in range(16))  # 'Buffer'+16个字节的随机数
    return __encode(SEED_PREFIX, randBytes)


"""
 * generate privatekey from input seed
 * one seed can generate many keypairs,
 * here just use the first one
 * @param {buffer} seed
 * @returns {buffer}
"""


def derivePrivateKey(seed):
    order = ec.curve.n
    privateGen = secp256k1.ScalarMultiple(seed)
    publicGen = ec.g.mul(privateGen)
    return secp256k1.ScalarMultiple(publicGen.encodeCompressed(), 0).add(privateGen).mod(order)


"""
 * derive keypair from secret
 * @param {string} secret
 * @returns {{privateKey: string, publicKey: *}}
"""


def deriveKeyPair(self, secret):
    prefix = '00'
    entropy = self.__decode(SEED_PREFIX, secret)
    entropy = base58.b58decode(secret).slice(1, -4)
    privateKey = prefix + self.derivePrivateKey(entropy).toString(16, 64).toUpperCase()
    publicKey = utils.bytesToHex(ec.keyFromPrivate(privateKey.slice(2)).getPublic().encodeCompressed())
    return {privateKey: privateKey, publicKey: publicKey}


"""
 * devive keypair from privatekey
"""


def deriveKeyPairWithKey(key):
    privateKey = key
    publicKey = utils.bytesToHex(ec.keyFromPrivate(key).getPublic().encodeCompressed())
    return {privateKey: privateKey, publicKey: publicKey}


"""
 * derive wallet address from publickey
 * @param {string} publicKey
 * @returns {string}
"""


def deriveAddress(self, publicKey):
    bytes = utils.hexToBytes(publicKey)
    hash256 = hashlib.sha256().update(bytes).digest()
    input = Buffer(hashlib.ripemd160().update(hash256).digest())
    return self.__encode(ACCOUNT_PREFIX, input)


"""
 * check is address is valid
 * @param address
 * @returns {boolean}
"""


def checkAddress(self, address):
    try:
        self.__decode(ACCOUNT_PREFIX, address)
        return True
    except Exception:
        return False
