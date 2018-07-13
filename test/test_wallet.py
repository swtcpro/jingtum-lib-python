"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/7/5
 * Time: 23:31
 * Description: 
"""
import unittest

from src.logger import logger
from src.base import wallet


class RemoteWallet(unittest.TestCase):

    def test_isValidAddress(self):
        self.assertTrue(wallet.Wallet.isValidAddress('jfdLqEWhfYje92gEaWixVWsYKjK5C6bMoi'))

    def test_fromSecret(self):
        print(wallet.Wallet.fromSecret('snDenehKWkWy4QNsYwhjV2xk31V6B'))

    def test_generate(self):
        print(wallet.Wallet.generate())
