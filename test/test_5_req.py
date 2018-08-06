# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/7/21
 * Time: 11:25
 * Description: 测试模块
"""
import unittest

from src.remote import Remote

class RequestTest(unittest.TestCase):
    def test_selectLedger(self):
        remote = Remote(local_sign=True)

        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_info({'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8000'})
            req.select_ledger(838796)
            result =req.submit()
            #result = remote.parse_payment(s)
            print('test_selectLedger result is', result)

    def test_submit(self):
        remote = Remote(local_sign=True)

        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_info({'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8'})
            result =req.submit()
            #result = remote.parse_payment(s)
            print('test request_account_info result is', result)


if __name__ == '__main__':
    unittest.main()
