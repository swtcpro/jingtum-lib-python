"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/7/4
 * Time: 16:18
 * Description: wallet类，对应baseLib的wallet钱包类
"""
from src.base import keypairs
from src.logger import logger

class Wallet:

    def __init__(self, secret):
        try:
            self._secret = secret
            self._keypairs = keypairs.deriveKeyPair(secret)
        except RuntimeError as err:
            self._secret = None
            self._keypairs = None

    @staticmethod
    def generate():
        """
        generate one wallet
        :return:  {{secret: string, address: string}}
        """
        secret = keypairs.generateSeed()
        keypair = keypairs.deriveKeyPair(secret)
        address = keypairs.deriveAddress(keypair['publicKey'])
        return {'secret': secret, 'address': address}

    @staticmethod
    def fromSecret(secret):
        """
        generate one wallet from secret
        :param secret:
        :return: {{secret: string, address: string}}
        """
        try:
            keypair = keypairs.deriveKeyPair(secret)
            address = keypairs.deriveAddress(keypair.publicKey)
            return {'secret': secret, 'address': address}
        except Exception as e:
            logger(e)
            return None

    @staticmethod
    def isValidAddress(address):
        """
        check if address is valid
        :param address:
        :return:    {boolean}
        """
        return keypairs.checkAddress(address)
