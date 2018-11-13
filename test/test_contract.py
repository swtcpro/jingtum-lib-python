# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/11/9
 * Time: 11:25
 * Description: 测试智能合约模块
"""
import unittest


from jingtum_python_lib.logger import logger
from jingtum_python_lib.remote import Remote
from jingtum_python_baselib.utils import str_to_hex


class ContractTest(unittest.TestCase):
    @staticmethod
    def test_deploy_contract():
        remote = Remote(local_sign=True)
        payload = 'result={}; ' + \
            'function Init(t) result=scGetAccountBalance(t) ' + \
            'return result end; ' + \
            'function foo(t) result=scGetAccountBalance(t) ' + \
            'return result end'
        options = {
            'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
            'amount': 10,
            'payload': str_to_hex(payload),
            'params': ['j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8']
        }

        if not isinstance(remote.connect(), Exception):
            tx = remote.deploy_contract_tx(options)
            tx.set_secret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s = tx.submit()
            result = remote.parse_contract(s)
            logger.info(result)

    @staticmethod
    def test_call_contract():
        remote = Remote(local_sign=True)
        options = {
            'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
            'destination': 'jD2WwwJcjh3RtzQFnXe8joq72FN6KrVuji',
            'foo': 'foo',
            'params': ['j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8']
        }

        if not isinstance(remote.connect(), Exception):
            tx = remote.call_contract_tx(options)
            tx.set_secret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s = tx.submit()
            result = remote.parse_contract(s)
            logger.info(result)


if __name__ == '__main__':
    unittest.main()
