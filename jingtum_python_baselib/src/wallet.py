# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/17
 * Time: 11:25
 * Description: 钱包模块
"""
import hashlib

# from utils import utils

# from src.lib import keypair


# var hashjs = require('hash.js');
# from hash import hashpy
# ec = elliptic.ec

def hash(message):
    return hashlib.sha512().update(message).digest().slice(0, 32)


class Wallet:
    def __init__(self, secret):
        try:
            self._keypairs = keypair.deriveKeyPair(secret)
            self._secret = secret
        except Exception:
            self._keypairs = None
            self._secret = None

    """
     * static funcion
     * generate one wallet
     * @returns {{secret: string, address: string}}
    """

    @staticmethod
    def generate():
        secret = keypair.generateSeed()
        keypair = keypair.deriveKeyPair(secret)
        address = keypair.deriveAddress(keypair.publicKey)
        return {secret: secret, address: address}

    """
     * static function
     * generate one wallet from secret
     * @param secret
     * @returns {*}
    """

    @staticmethod
    def fromSecret(secret):
        try:
            keypair = keypairs.deriveKeyPair(secret)
            address = keypairs.deriveAddress(keypair.publicKey)
            return {'secret': secret, 'address': address}
        except Exception:
            return None

    """
     * static function
     * check if address is valid
     * @param address
     * @returns {boolean}
    """

    @staticmethod
    def isValidAddress(address):
        return keypairs.checkAddress(address)

    """
     * static function
     * check if secret is valid
     * @param secret
     * @returns {boolean}
    """

    @staticmethod
    def isValidSecret(secret):
        try:
            keypairs.deriveKeyPair(secret)
            return True
        except Exception:
            return False

    """
     * sign message with wallet privatekey
     * @param message
     * @returns {*}
    """

    def sign(self, message):
        if not message or len(message) == 0:
            return None
        if not self._keypairs:
            return None
        privateKey = self._keypairs.privateKey;
        return utils.bytesToHex(ec.sign(hash(message), utils.hexToBytes(privateKey), {'canonical': True}).toDER());

    """
     * verify signature with wallet publickey
     * @param message
     * @param signature
     * @returns {*}
    """

    def verify(self, message, signature):
        if not self._keypairs:
            return None
        publicKey = self._keypairs.publicKey
        return ec.verify(hash(message), signature, utils.hexToBytes(publicKey))

    """
     * get wallet address
     * @returns {*}
    """

    def address(self):
        if not self._keypairs:
            return None
        address = keypairs.deriveAddress(self._keypairs.publicKey)
        return address

    """
     * get wallet secret
     * @returns {*}
    """

    def secret(self):
        if not self._keypairs:
            return None
        return self._secret

    def toJson(self):
        if not self._keypairs:
            return None
        return {
            'secret': self.secret(),
            'address': self.address()
        }
