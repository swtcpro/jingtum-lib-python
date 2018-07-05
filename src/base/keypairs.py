"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/7/5
 * Time: 14:35
 * Description: 密钥对keypairs文件，对应jslib中keypars
"""
import base58
import random
import hashlib
import _struct
from ecdsa import SigningKey, VerifyingKey, SECP256k1

from jingtum_python_baselib.src import utils

SEED_PREFIX = 33
ACCOUNT_PREFIX = 0
alphabet = 'jpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65rkm8oFqi1tuvAxyz'


# base58.alphabet = alphabet


def generateSeed():
    randBytes = ''.join(random.choice(alphabet) for _ in range(16))  # 'Buffer'+16个字节的随机数
    return __encode(SEED_PREFIX, randBytes)


def __encode(version, bytes):
    """
    :param version:
    :param bytes:
    :return:
    """
    buffer = str(version) + bytes
    checksum = sha256(sha256(buffer.encode('ascii')))[0: 4]
    ret = buffer + checksum
    return base58.b58encode(ret)


def __decode(version, input):
    """
    decode encoded input,
    too small or invalid checksum will throw exception
    :param version:
    :param input:
    :return:
    """
    bytes = base58.b58decode_int(input)
    if bytes is not None or bytes[0] != version or bytes.__len__() < 5:
        raise Exception('invalid input size')
    computed = sha256(sha256(bytes[0, -4]))[0, 4]
    checksum = bytes[-4]
    for i in range(0, 4):
        if computed[i] != checksum[i]:
            raise Exception('invalid checksum')
    return bytes[1, -4]


def sha256(bytes):
    # return hashlib.sha256().update(bytes).digest()
    return hashlib.sha256().update(bytes).digest()


def deriveKeyPair(secret):
    """
    由secret生成keypairs
    :param secret: {string} secret
    :return: {{privateKey: string, publicKey: *}}
    """
    prefix = '00'
    entropy = base58.b58decode(secret)[1: -4]
    privateKey = prefix + derivePrivateKey(entropy).upper()
    publicKey = VerifyingKey.from_string(privateKey[2:], SECP256k1, 'sha3_512')
    return {'privateKey': privateKey, 'publicKey': publicKey}


def derivePrivateKey(seed):
    """
     generate privatekey from input seed
     one seed can generate many keypairs,
     here just use the first one
    :param seed:
    :return:
    """
    return SigningKey.from_string(seed, curve=SECP256k1).to_string()


def deriveAddress(publicKey):
    """
    derive wallet address from publickey
    :param publicKey:
    :return:
    """
    bytes = utils.hexToBytes(publicKey)
    hash256 = hashlib.sha256().update(bytes).digest()
    obj = hashlib.new('ripemd160', hash256.encode('utf-8'))
    input = obj.hexdigest()
    return __encode(ACCOUNT_PREFIX, input)


def checkAddress(address):
    """
    check is address is valid
    :param address:
    :return: {boolean}
    """
    try:
        # __decode(ACCOUNT_PREFIX, address)
        base58.b58decode_check(address)
        return True
    except Exception:
        return False
