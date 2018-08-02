# # coding=gbk
#
# import sys
# from src.logger import logger
#
# sys.path.append("..\src")
# from src.remote import Remote
#
# def CheckErr(err, result):
#     if (err):
#         print('err:', err)
#     elif result:
#         print('res:', result)
#
# def test(err, callback):
#     if err:
#         return print('err:', err)
#     options = {
#         'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
#         'type': 'property'
#     }
#
#     tx = remote.buildAccountSetTx(options)
#     tx.setSecret('sn37nYrQ6KPJvTFmaBYokS3FjXUWd')
#     # tx.addMemo('设置账户属性')  # 可选
#     tx.submit(CheckErr)
#
# remote = Remote({'server': 'ws://ts5.jingtum.com:5020', 'local_sign': True})
# result = remote.connect(None)
# test(None, None)
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

    # def test_buildPaymentTx(self):
    #     remote = Remote()
    #     if not isinstance(remote.connect(None), Exception):
    #         req = remote.buildAccountSetTx({'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8','type': 'property'})
    #         req.setSecret('ssTkYQLLYiZs7Sosp12sB43TocUbd')
    #         result = remote.parse_server_info(req.submit())
    #         logger.info(result)
    def test_requestAccountTx(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.requestAccountTx({'account': 'j9fE48ebcvwnKSGnPdtN6jGNM9yVBMVaH8eee'})
            temp= req.submit()
            result = remote.parse_AccountTx_info(temp)
            logger.info(result)

    def test_requestOrderBook(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.requestOrderBook({'gets': {'currency': 'SWT', 'issuer': ''},
                  'pays': {'currency': 'CNY', 'issuer': 'jBciDE8Q3uJjf111VeiUNM775AMKHEbBLS'}})
            temp = req.submit()
            result = remote.parse_OrderBook_info(temp)
            logger.info(result)

    def test_getAccount(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.buildOfferCancelTx({
                    'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
                    'sequence': 688
                    })
            temp=req.getAccount()
            logger.info(temp)
    def test_getTransactionType(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.buildOfferCancelTx({
                    'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
                    'sequence': 688
                    })
            temp=req.getTransactionType()
            logger.info(temp)







if __name__ == '__main__':
    unittest.main()

