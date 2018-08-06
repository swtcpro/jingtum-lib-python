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


class RemoteTest(unittest.TestCase):

    def test_server_info(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_server_info()
            result = remote.parse_server_info(req.submit())
            logger.info(result)

    def test_ledger_closed(self):
        remote = Remote(local_sign=True)
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_ledger_closed()
            result = remote.parse_ledger_closed(req.submit())
            logger.info(result)

    def test_ledger(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_ledger({'ledger_index': '943501'})
            temp = req.submit()
            result = remote.parse_ledger(temp, req)
            logger.info(result)

            req = remote.request_ledger({'ledger_hash': '944960C0816D716FE962AABED9F2FF8B9EF4584AF7DA16EFBB3F461A5A720969'})
            temp = req.submit()
            result = remote.parse_ledger(temp, req)
            logger.info(result)

            req = remote.request_ledger({'transactions': True})
            temp = req.submit()
            result = remote.parse_ledger(temp, req)
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
            req = remote.request_account_relations({'account': 'jEkffY8XtkEtkUKyYQT1Fv7MDp3grAtwdH',
                                                    'type': 'trust'})
            result = remote.parse_request_account_relations(req.submit())
            logger.info(result)

            req = remote.request_account_relations({'account': 'jEkffY8XtkEtkUKyYQT1Fv7MDp3grAtwdH',
                                                    'type': 'authorize'})
            result = remote.parse_request_account_relations(req.submit())
            logger.info(result)

            req = remote.request_account_relations({'account': 'jEkffY8XtkEtkUKyYQT1Fv7MDp3grAtwdH',
                                                    'type': 'freeze'})
            result = remote.parse_request_account_relations(req.submit())
            logger.info(result)

    def test_request_account_offers(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_offers({'account': 'jJvkUPnBNQ4Wy5QGBKwMa8ftS5s9EDYXER'})
            result = remote.parse_request_account_offers(req.submit())
            logger.info(result)

    def test_request_account_tx(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_account_tx({'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK',
                                             'limit': 9})
            temp = req.submit()
            # logger.info(temp)
            result = remote.parse_account_tx_info(temp, req)
            logger.info(result)


if __name__ == '__main__':
    unittest.main()
