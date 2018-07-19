"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/6/15
 * Time: 0:27
 * Description: 
"""
import unittest

from src.logger import logger
from src.remote import Remote


# import random
# from jingtum_python_baselib.src import keypairs


class RemoteTest(unittest.TestCase):

    def test_server_info(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_server_info()
            result = remote.parse_server_info(req.submit())
            logger.info(result)

    def test_ledger_closed(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_ledger_closed()
            result = remote.parse_ledger_closed(req.submit())
            logger.info(result)

    def test_ledger(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_ledger({'ledger_index': 8182274})
            result = remote.parse_ledger(req.submit())
            logger.info(result)

    def test_transaction(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_tx({'hash': '82C2C652431B63179E7CC775C3C1DBEC7AF1A6E91CC5A2671B195C19C76D701C'})
            result = remote.parse_transaction(req.submit())
            logger.info(result)

    def test_request_account_info(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_info({'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK'})
            result = remote.parse_account_info(req.submit())
            logger.info(result)

    # def test_generateSeed(self):
    #     randBytes = ''.join(random.choice(keypairs.alphabet) for _ in range(16))  # 'Buffer'+16个字节的随机数
    #     return keypairs.__encode(33, randBytes)


if __name__ == '__main__':
    unittest.main()
