# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/21
 * Time: 11:25
 * Description: 测试模块
"""
import unittest

#from src.logger import logger
from src.remote import Remote

class RemoteTest(unittest.TestCase):
    def test_create_pay_object(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            tx = remote.buildPaymentTx({
                'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
                'to': 'jDUjqoDZLhzx4DCf6pvSivjkjgtRESY62c',
                'amount': {
                    "value": 0.5,
                    "currency": "SWT",
                    "issuer": ""
                }
            })
            tx.setSecret('sn37nYrQ6KPJvTFmaBYokS3FjXUWd')
            tx.addMemo('给jDUjqoDZLhzx4DCf6pvSivjkjgtRESY62c支付0.5swt.')  # 可选
            tx.addMemo('123')
            s=tx.submit()
            print('result is', s)

if __name__ == '__main__':
    unittest.main()
