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
        remote = Remote(local_sign=True)
        if not isinstance(remote.connect(None), Exception):
            options =  {
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'to': 'jEmEWuLQXgtBaro86hScnBpjN3TgKSoQGD',
                'amount': {
                    "value": 0.01,
                    "currency": "SWT",
                    "issuer": ""
                }
            }
            tx = remote.buildPaymentTx(options)
            tx.setSecret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            #tx.addMemo('给jDUjqoDZLhzx4DCf6pvSivjkjgtRESY62c支付0.5swt.')  # 可选
            #tx.addMemo('给')  # 可选
            #tx.addMemo('123')
            s=tx.submit()
            result=remote.parse_payment(s)
            print('test_create_pay_object result is', result)

    def test_set_relation(self):
        remote = Remote()
        options_trust = {
                'type': 'trust',
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'target': 'jEmEWuLQXgtBaro86hScnBpjN3TgKSoQGD',
                'limit': {
                    "value": "0.5",
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
            tx = remote.buildRelationTx(options_trust)
            tx.setSecret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s=tx.submit()
            result=remote.parse_payment(s)
            print('trust result is', result)

            tx = remote.buildRelationTx(options_authorize)
            tx.setSecret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s=tx.submit()
            result=remote.parse_payment(s)
            print('authorize result is', result)

            tx = remote.buildRelationTx(options_freeze)
            tx.setSecret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s=tx.submit()
            result=remote.parse_payment(s)
            print('freeze result is', result)

    def test_buildaccount(self):
        remote = Remote()
        options_property = {
                'type': 'property',
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'set_flag': '123'
        }
        options_delegate = {
                'type': 'delegate',
                'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8',
                'delegate_key': 'jEmEWuLQXgtBaro86hScnBpjN3TgKSoQGD',
                'set_flag': '123'
        }
        if not isinstance(remote.connect(None), Exception):
            tx = remote.buildAccountSetTx(options_property)
            tx.setSecret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s=tx.submit()
            result=remote.parse_payment(s)
            print('buildAccountSetTx property result is', result)

            tx = remote.buildAccountSetTx(options_delegate)
            tx.setSecret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
            s=tx.submit()
            result=remote.parse_payment(s)
            print('buildAccountSetTx delegate result is', result)

if __name__ == '__main__':
    unittest.main()
