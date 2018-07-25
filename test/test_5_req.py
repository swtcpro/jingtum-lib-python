# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/21
 * Time: 11:25
 * Description: 测试模块
"""
import unittest

from src.remote import Remote

class RequestTest(unittest.TestCase):
    def test_selectLedger(self):
        remote = Remote(local_sign=True)

        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_info({'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8'})
            req.select_ledger(838796)
            s=req.submit()
            result = req.parse_ledger(s)
            print('test_selectLedger result is', result)

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
