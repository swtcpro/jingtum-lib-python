# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/17
 * Time: 11:25
 * Description: 钱包模块
"""
from jingtum_python_baselib.keypairs import *

class Wallet:
    def __init__(self, secret=None):
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
    def generate(self):
        self.secret = get_secret()
        self.keypairs = root_key_from_seed(parse_seed(self.secret))
        address = get_jingtum_from_key(self.keypairs)
        return {'secret': self.secret, 'address': address}

    """
     * static function
     * generate one wallet from secret
     * @param secret
     * @returns {*}
    """
    #@staticmethod
    def from_secret(self, secret):
        try:
            self.keypairs = root_key_from_seed(parse_seed(secret))
            self.secret = secret
            address = get_jingtum_from_key(self.keypairs)
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
    def is_valid_address(address):
        try:
            decode_address(ACCOUNT_PREFIX, address)
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
    def is_valid_secret(secret):
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
        if not self.keypairs:
            return None
            # Verify a correct signature is created (uses a fixed k value):
        #result = jingtum_sign(self.keypairs, message.encode()) original py,has issue
        result = jingtum_sign(self.keypairs, message).decode()
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
        if not self.secret:
            return None
        return self.secret

    def toJson(self):
        if not self.keypairs:
            return None
        return {
            'secret': self.secret(),
            'address': self.address()
        }

    def get_public_key(self):
        if not self.keypairs:
            return None
        return get_jingtum_publickey(self.keypairs)