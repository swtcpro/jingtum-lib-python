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
            req = remote.request_ledger({'ledger_index': 8186589})
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

    def test_request_account_tums(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_tums({'account': 'jEkffY8XtkEtkUKyYQT1Fv7MDp3grAtwdH'})
            result = remote.parse_account_tums(req.submit())
            logger.info(result)

    def test_request_account_relations(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_relations({'account': 'jEkffY8XtkEtkUKyYQT1Fv7MDp3grAtwdH', 'type': 'trust'})
            result = remote.parse_request_account_relations(req.submit())
            logger.info(result)

    def test_request_account_offers(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_offers({'account': 'jJvkUPnBNQ4Wy5QGBKwMa8ftS5s9EDYXER'})
            result = remote.parse_request_account_offers(req.submit())
            logger.info(result)

    # def test_generateSeed(self):
    #     randBytes = ''.join(random.choice(keypairs.alphabet) for _ in range(16))  # 'Buffer'+16个字节的随机数
    #     return keypairs.__encode(33, randBytes)

    def test_request_account_tx(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_tx({'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK'})
            temp = req.submit()
            # logger.info(temp)
            result = remote.parse_account_tx_info(temp, req, {'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK'})
            logger.info(result)


if __name__ == '__main__':
    unittest.main()
