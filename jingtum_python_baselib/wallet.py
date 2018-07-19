# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/17
 * Time: 11:25
 * Description: 钱包模块
"""
import hashlib
from jingtum_python_baselib.keypairs import *


#import sys
#sys.path.append("..")

def hash(message):
    return hashlib.sha512().update(message).digest()[0:32]

class Wallet:
    def __init__(self, secret):
        try:
            self.keypairs = root_key_from_seed(parse_seed(secret))
            self.secret = secret
        except Exception:
            self.keypairs = None
            self.secret = None

    """
     * static funcion
     * generate one wallet
     * @returns {{secret: string, address: string}}
    """
    @staticmethod
    def generate():
        secret = get_secret()
        keypairs = root_key_from_seed(parse_seed(secret))
        address = get_jingtum_from_key(keypairs)
        return {'secret': secret, 'address': address}

    """
     * static function
     * generate one wallet from secret
     * @param secret
     * @returns {*}
    """
    @staticmethod
    def fromSecret(secret):
        try:
            keypairs = root_key_from_seed(parse_seed(secret))
            address = get_jingtum_from_key(keypairs)
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
        try:
            decodeAddress(ACCOUNT_PREFIX, address)
            return True
        except Exception:
            return False

    """
     * static function
     * check if secret is valid
     * @param secret
     * @returns {boolean}
    """
    @staticmethod
    def isValidSecret(secret):
        try:
            parse_seed(secret)
            return True
        except Exception:
            return False

    """
     * static function
     * check if secret is valid
     * @param secret
     * @returns {boolean}
    """
    @staticmethod
    def isValidSecret(secret):
        try:
            parse_seed(secret)
            return True
        except Exception:
            return False

    """
     * sign message with wallet privatekey
     * Export DER encoded signature in Array
     * @param message
     * @returns {*}
    """
    def sign(self, message):
        if not message or len(message) == 0:
            return None
        if not self.key:
            return None
            # Verify a correct signature is created (uses a fixed k value):
        result = jingtum_sign(self.key, message.encode())
        return result

    """
     * get wallet address
     * @returns {*}
    """
    def address(self):
        if not self.keypairs:
            return None
        address = get_jingtum_from_key(self.keypairs)
        return address

    """
     * get wallet secret
     * @returns {*}
     * not finish yet
    """
    def secret(self):
        if not self.keypairs:
            return None
        return self.secret

    def toJson(self):
        if not self.keypairs:
            return None
        return {
            'secret': self.secret(),
            'address': self.address()
        }

    def getPublicKey(self):
        if not self.keypairs:
            return None
        return get_jingtum_publickey(self.keypairs)