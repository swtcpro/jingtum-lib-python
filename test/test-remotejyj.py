# coding=gbk

import sys
from src.logger import logger

sys.path.append("..\src")
from src.remote import Remote

def CheckErr(err, result):
    if (err):
        print('err:', err)
    elif result:
        print('res:', result)

def test(err, callback):
    if err:
        return print('err:', err)
    options = {
        'account': 'jB7rxgh43ncbTX4WeMoeadiGMfmfqY2xLZ',
        'type': 'property'
    }

    tx = remote.buildAccountSetTx(options)
    tx.setSecret('sn37nYrQ6KPJvTFmaBYokS3FjXUWd')
    # tx.addMemo('设置账户属性')  # 可选
    tx.submit(CheckErr)

remote = Remote({'server': 'ws://ts5.jingtum.com:5020', 'local_sign': True})
result = remote.connect(None)
test(None, None)
