"""
 * Created with PyCharm.
 * User: 蔡正龙
 * Date: 2018/7/17
 * Time: 23:31
 * Description: 
"""
import unittest

from src.logger import logger
from jingtum_python_baselib.wallet import Wallet

class TestWallet(unittest.TestCase):
    def test_isValidAddress(self):
        self.assertTrue(Wallet.isValidAddress('jfdLqEWhfYje92gEaWixVWsYKjK5C6bMoi'))

    def test_fromSecret(self):
        logger.info(Wallet.fromSecret('snDenehKWkWy4QNsYwhjV2xk31V6B'))

    def test_generate(self):
        logger.info(Wallet.generate())

if __name__ == '__main__':
    unittest.main()