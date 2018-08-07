# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/21
 * Time: 11:25
 * Description: 测试模块
"""
import unittest

from src.logger import logger
from src.remote import Remote


class RemoteTest(unittest.TestCase):
    @staticmethod
    def test_create_pay_object():
        remote = Remote(local_sign=True)
        if not isinstance(remote.connect(None), Exception):
            options = {
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'to': 'jEmEWuLQXgtBaro86hScnBpjN3TgKSoQGD',
                'amount': {
                    "value": 0.01,
                    "currency": "SWT",
                    "issuer": ""
                }
            }
            tx = remote.build_payment_tx(options)
            tx.set_secret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            tx.add_memo('给jDUjqoDZLhzx4DCf6pvSivjkjgtRESY62c支付0.5swt.')  # 可选
            tx.add_memo('给')  # 可选
            s = tx.submit()
            result = remote.parse_payment(s)
            logger.info(result)

    @staticmethod
    def test_set_relation():
        remote = Remote()
        options_trust = {
                'type': 'trust',
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'target': 'jEmEWuLQXgtBaro86hScnBpjN3TgKSoQGD',
                'limit': {
                    "value": "600000000000",
                    "currency": "CCA",
                    "issuer": "js7M6x28mYDiZVJJtfJ84ydrv2PthY9W9u"
                }
        }
        options_authorize = {
                'type': 'authorize',
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'target': 'jEmEWuLQXgtBaro86hScnBpjN3TgKSoQGD',
                'limit': {
                    "value": "0.5",
                    "currency": "CCA",
                    "issuer": "js7M6x28mYDiZVJJtfJ84ydrv2PthY9W9u"
                }
        }
        options_freeze = {
            'type': 'freeze',
            'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
            'target': 'jEmEWuLQXgtBaro86hScnBpjN3TgKSoQGD',
            'limit': {
                "value": "0.5",
                "currency": "CCA",
                "issuer": "js7M6x28mYDiZVJJtfJ84ydrv2PthY9W9u"
            }
        }
        if not isinstance(remote.connect(None), Exception):
            tx = remote.build_relation_tx(options_trust)
            tx.set_secret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s = tx.submit()
            result = remote.parse_payment(s)
            logger.info(result)

            tx = remote.build_relation_tx(options_authorize)
            tx.set_secret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s = tx.submit()
            result = remote.parse_payment(s)
            logger.info(result)

            tx = remote.build_relation_tx(options_freeze)
            tx.set_secret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s = tx.submit()
            result = remote.parse_payment(s)
            logger.info(result)

    @staticmethod
    def test_build_account():
        remote = Remote()
        options_property = {
                'type': 'property',
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'set_flag': '2'
        }
        options_delegate = {
                'type': 'delegate',
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'delegate_key': 'jEmEWuLQXgtBaro86hScnBpjN3TgKSoQGD',
                'set_flag': '123'
        }
        if not isinstance(remote.connect(None), Exception):
            tx = remote.build_account_set_tx(options_property)
            tx.set_secret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s = tx.submit()
            result = remote.parse_payment(s)
            logger.info(result)

            tx = remote.build_account_set_tx(options_delegate)
            tx.set_secret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s = tx.submit()
            result = remote.parse_payment(s)
            logger.info(result)

if __name__ == '__main__':
    unittest.main()
