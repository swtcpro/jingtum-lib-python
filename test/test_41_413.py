"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/6/15
 * Time: 0:27
 * Description: 
"""
import unittest

from jingtum_python_lib.logger import logger
from jingtum_python_lib.remote import Remote


class RemoteTest(unittest.TestCase):
    def test_conn(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            result = remote.get_connect_info()
            logger.info(result)

    def test_conn_close(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.disconnect()

    def test_server_info(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.request_server_info()
            result = remote.parse_server_info(req.submit())
            logger.info(result)

    def test_ledger_closed(self):
        remote = Remote(local_sign=True)
        if not isinstance(remote.connect(), Exception):
            req = remote.request_ledger_closed()
            result = remote.parse_ledger_closed(req.submit())
            logger.info(result)

    def test_ledger(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.request_ledger({'ledger_index': '943501','transactions': True})
            temp = req.submit()
            result = remote.parse_ledger(temp, req)
            logger.info(result)

            req = remote.request_ledger({'ledger_hash': '1F91E2FBCF7BCF26D02024657460FE3718F701D2497F12F54C24D56521912E61'})
            temp = req.submit()
            result = remote.parse_ledger(temp, req)
            logger.info(result)

            req = remote.request_ledger({'transactions': True})
            temp = req.submit()
            result = remote.parse_ledger(temp, req)
            logger.info(result)

    def test_transaction(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.request_tx({'hash': 'BDE5FAA4F287353E65B3AC603F538DE091F1D8F4723A120BD7D930C5C4668FE2111'})
            result = remote.parse_transaction(req.submit())
            logger.info(result)

    def test_request_account_info(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.request_account_info({'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK111'})
            result = remote.parse_account_info(req.submit())
            logger.info(result)

    def test_request_account_tums(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.request_account_tums({'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK'})
            result = remote.parse_account_tums(req.submit())
            logger.info(result)

    def test_request_account_relations(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.request_account_relations({'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ123',
                                                    'type': 'trust'})
            result = remote.parse_request_account_relations(req.submit())
            logger.info(result)

            req = remote.request_account_relations({'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK',
                                                    'type': 'authorize'})
            result = remote.parse_request_account_relations(req.submit())
            logger.info(result)

            req = remote.request_account_relations({'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK',
                                                    'type': 'freeze'})
            result = remote.parse_request_account_relations(req.submit())
            logger.info(result)

    def test_request_account_offers(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.request_account_offers({'account': 'jJvkUPnBNQ4Wy5QGBKwMa8ftS5s9EDYXER888'})
            result = remote.parse_request_account_offers(req.submit())
            logger.info(result)

    def test_request_account_tx(self):
        remote = Remote()
        if not isinstance(remote.connect(), Exception):
            req = remote.request_account_tx({'account': 'jsMwaJ7EA4y7QgdvQzaD2CqzQQN4v7vLFK123',
                                             'limit': 1})
            temp = req.submit()
            result = remote.parse_account_tx_info(temp, req)
            logger.info(result)

    def test_request_orderbook(self):
        remote = Remote(local_sign=True)
        if not isinstance(remote.connect(), Exception):
            req = remote.request_order_book({'gets': {'currency': '1SWT', 'issuer': ''},
                'pays': {'currency': 'CNY', 'issuer': 'jBciDE8Q3uJjf111VeiUNM775AMKHEbBLS'},
                'limit': 1})
            temp = req.submit()
            result = remote.parse_orderbook_info(temp)
            logger.info(result)


if __name__ == '__main__':
    unittest.main()
