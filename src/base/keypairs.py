"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/7/5
 * Time: 14:35
 * Description: 密钥对keypairs文件，对应jslib中keypars
"""
import base58
from ecdsa import SigningKey, VerifyingKey, SECP256k1

from jingtum_python_baselib.src import utils


def deriveKeyPair(secret):
    """
    由secret生成keypairs
    :param secret: {string} secret
    :return: {{privateKey: string, publicKey: *}}
    """
    prefix = '00'
    entropy = base58.b58decode(secret)[1, -4]
    privateKey = prefix + hex(derivePrivateKey(entropy)).replace('0x', '').upper()
    # 此处未完成
    publicKey = utils.bytesToHex(VerifyingKey.from_string(privateKey[2], SECP256k1, 'sha3_512'))
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
