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
        s=Wallet()
        print(Wallet.from_secret(s, 'ss2A7yahPhoduQjmG7z9BHu3uReDk'))

    def test_generate(self):
        #logger.info(
        s=Wallet()
        print(Wallet.generate(s))

    def test_get_public_key(self):
        self.assertEqual(Wallet('ss2A7yahPhoduQjmG7z9BHu3uReDk').get_public_key(), '035CDF6AAED00E4A1C68EB45B822C2F91E4B849E60B91809A2139DCA4A03A83BF5')

    def test_sign(self):
        t=Wallet()
        s = t.from_secret('saai2npGJD7GKh9xLxARfZXkkc8Bf')
        print(s)
        #print(t.address())
        MESSAGE1 = "F95EFF5A4127E68D2D86F9847D9B6DE5C679EE7D9F3241EC8EC67F99C4CDA923"
        SIGNATURE1 = '3045022100B53E6A54B71E44A4D449C76DECAE44169204744D639C14D22D941157F5A1418F02201D029783B31EE3DA88F18C56D055CF47606A9708FDCA9A42BAD9EFD335FA29FD'
        #print(list(MESSAGE1.encode()))
        #self.assertEqual(Wallet.sign(t, MESSAGE1), SIGNATURE1)
        print(t.sign(MESSAGE1))

if __name__ == '__main__':
    unittest.main()