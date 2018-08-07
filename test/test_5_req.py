# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/7/21
 * Time: 11:25
 * Description: 测试模块
"""
import unittest

from src.remote import Remote
from src.logger import logger


class RequestTest(unittest.TestCase):
    @staticmethod
    def test_select_ledger():
        remote = Remote(local_sign=True)

        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_info({'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8'})
            req.select_ledger(838796)
            result = req.submit()
            logger.info(result)

    @staticmethod
    def test_submit():
        remote = Remote(local_sign=True)

        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_info({'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8'})
            result = req.submit()
            logger.info(result)

if __name__ == '__main__':
    unittest.main()
