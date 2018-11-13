"""
 * Created with PyCharm.
 * User: 蔡正龙
 * Date: 2018/7/17
 * Time: 23:31
 * Description: 
"""
import unittest

from jingtum_python_lib.logger import logger
from jingtum_python_baselib.wallet import Wallet


class TestWallet(unittest.TestCase):
    def test_is_valid_address(self):
        self.assertTrue(Wallet.is_valid_address('jfdLqEWhfYje92gEaWixVWsYKjK5C6bMoi'))

    @staticmethod
    def test_from_secret():
        result = Wallet.from_secret('ss2A7yahPhoduQjmG7z9BHu3uReDk123')
        logger.info(result)

    @staticmethod
    def test_generate():
        result = Wallet.generate()
        logger.info(result)


if __name__ == '__main__':
    unittest.main()

