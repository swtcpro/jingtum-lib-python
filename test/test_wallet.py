"""
 * Created with PyCharm.
 * User: 蔡正龙
 * Date: 2018/7/17
 * Time: 23:31
 * Description: 
"""
import unittest

#from src.logger import logger
from jingtum_python_baselib.wallet import Wallet

class TestWallet(unittest.TestCase):
    def test_is_valid_address(self):
        self.assertTrue(Wallet.is_valid_address('jfdLqEWhfYje92gEaWixVWsYKjK5C6bMoi'))

    def test_from_secret(self):
        #logger.info
        s=Wallet.from_secret('ss2A7yahPhoduQjmG7z9BHu3uReDk')
        print(s)

    def test_generate(self):
        #logger.info(
        s=Wallet.generate()
        print(s)

if __name__ == '__main__':
    unittest.main()