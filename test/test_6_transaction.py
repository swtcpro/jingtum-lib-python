# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/7/21
 * Time: 11:25
 * Description: 测试模块
"""
import unittest

from src.remote import Remote

class TransactionTest(unittest.TestCase):
    def test_get_account(self):
        remote = Remote()

        options = {
            'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
            'sequence': 6889999
        }
        if not isinstance(remote.connect(None), Exception):
            req = remote.build_offer_cancel_tx(options)
            result = req.get_account()
            print('test_get_account result is', result)

    def test_get_transaction_type(self):
        remote = Remote()
        options = {
            'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
            'sequence': 688
        }

        if not isinstance(remote.connect(None), Exception):
            req = remote.build_offer_cancel_tx(options)
            result = req.get_transaction_type()
            print('test get_transaction_type result is', result)


if __name__ == '__main__':
    unittest.main()
