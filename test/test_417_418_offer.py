# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/21
 * Time: 11:25
 * Description: 测试模块
"""
import unittest
from numbers import Number

#from src.logger import logger
from src.remote import Remote

class OfferTest(unittest.TestCase):
    def test_build_offer_create(self):
        remote = Remote()
        options = {
            'type': 'Sell',
            'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
            'taker_gets': {
                'value': '0.01',
                'currency': 'CNY',
                'issuer': 'jBciDE8Q3uJjf111VeiUNM775AMKHEbBLS'
            },
            'taker_pays': {
                'value': '1',
                'currency': 'SWT',
                'issuer': ''
            }
        }

        if not isinstance(remote.connect(None), Exception):
            tx = remote.buildOfferCreateTx(options)
            tx.setSecret('sn37nYrQ6KPJvTFmaBYokS3FjXUWd')
            s=tx.submit()
            result=remote.parse_payment(s)
            print('test_build_offer_create result is', result)

    def test_build_offer_cancel(self):
        remote = Remote()
        options = {
            'sequence': 1777,
            'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
        }

        if not isinstance(remote.connect(None), Exception):
            tx = remote.buildOfferCancelTx(options)
            tx.setSecret('sn37nYrQ6KPJvTFmaBYokS3FjXUWd')
            s=tx.submit()
            result=remote.parse_payment(s)
            print('test_build_offer_cancel result is', result)


if __name__ == '__main__':
    unittest.main()
