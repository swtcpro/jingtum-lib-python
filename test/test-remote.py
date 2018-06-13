# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/21
 * Time: 11:25
 * Description: 测试模块
"""
import sys
from src.logger import logger

sys.path.append("..\src")
from src.remote import Remote


def CheckErr(err, result):
    if (err):
        print('err:', err)
    elif result:
        print('res:', result)


remote = Remote()


def test(err, callback):
    if err:
        return print('err:', err)
    tx = remote.buildPaymentTx({
        'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
        'to': 'jDUjqoDZLhzx4DCf6pvSivjkjgtRESY62c',
        'amount': {
            "value": 0.5,
            "currency": "SWT",
            "issuer": ""
        }
    })
    tx.setSecret('sn37nYrQ6KPJvTFmaBYokS3FjXUWd')
    tx.addMemo('给jDUjqoDZLhzx4DCf6pvSivjkjgtRESY62c支付0.5swt.')  # 可选
    tx.submit(CheckErr)
    logger.info(callback)


remote.connect(None)
test(None, None)
