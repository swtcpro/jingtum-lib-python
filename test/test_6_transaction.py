# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/7/21
 * Time: 11:25
 * Description: 测试模块
"""
import unittest

from jingtum_python_lib.remote import Remote
from jingtum_python_lib.logger import logger


class TransactionTest(unittest.TestCase):
    @staticmethod
    def test_get_account():
        remote = Remote()

        options = {
            'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
            'sequence': 6889999
        }
        if not isinstance(remote.connect(), Exception):
            req = remote.build_offer_cancel_tx(options)
            result = req.get_account()
            logger.info(result)

    @staticmethod
    def test_get_transaction_type():
        remote = Remote()
        options = {
            'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
            'sequence': 688
        }

        if not isinstance(remote.connect(), Exception):
            req = remote.build_offer_cancel_tx(options)
            result = req.get_transaction_type()
            logger.info(result)


if __name__ == '__main__':
    unittest.main()
