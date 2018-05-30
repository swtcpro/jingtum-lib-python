# coding=utf-8
from src.config import Config
import math
from src.utils.utils import is_number, utils

fee = Config.FEE or 10000


def filterFun(v):
    return v


def __hexToString(h):
    a = []
    i = 0
    strLength = len(h)

    if (strLength % 2 == 0):
        a.extend(unichr(int(h[0: 1], 16)))
        i = 1

    for index in range(i, strLength, 2):
        a.extend(unichr(int(h[index: index+2]), 16))

    return ''.join(a)


def __stringToHex(s):
    result = ''
    for c in s:
        b = ord(c)
        # 转换成16进制的ASCII码
        if b < 16:
            result += '0'+hex(b).replace('0x', '')
        else:
            result += hex(b).replace('0x', '')

    return result


def safe_int(num):
    try:
        return int(num)
    except ValueError:
        result = []
        for c in num:
            if not ('0' <= c <= '9'):
                break
            result.append(c)
        if len(result) == 0:
            return 0
        return int(''.join(result))


def Number(num):
    if(not is_number(num)):
        return float('nan')
    if(isinstance(num, bool) and num):
        return 1
    if(isinstance(num, bool) and not num):
        return 0
    if(isinstance(num, (int, float))):
        return num
    if '.' in num:
        return float(num)
    else:
        return int(num)


def MaxAmount(amount):
    if (isinstance(amount, str) and is_number(amount)):
        _amount = safe_int(Number(amount) * (1.0001))
        return str(_amount)
    if (isinstance(amount, dict) and utils.isValidAmount(amount)):
        _value = Number(amount['value']) * (1.0001)
        amount['value'] = str(_value)
        return amount
    return Exception('invalid amount to max')


class Transaction:
    def __init__(self, remote, filter):
        # TODO(zfn):事件驱动注册待实现
        self._remote = remote
        self.tx_json = {"Flags": 0, "Fee": fee}
        self._filter = filter or filterFun
        self._secret = 0

    set_clear_flags = {
        'AccountSet': {
            'asfRequireDest':    1,
            'asfRequireAuth':    2,
            'asfDisallowSWT':    3,
            'asfDisableMaster':  4,
            'asfNoFreeze':       6,
            'asfGlobalFreeze':   7
        }
    }

    flags = {
        # Universal flags can apply to any transaction type
        'Universal': {
            'FullyCanonicalSig':  0x80000000
        },

        'AccountSet': {
            'RequireDestTag':     0x00010000,
            'OptionalDestTag':    0x00020000,
            'RequireAuth':        0x00040000,
            'OptionalAuth':       0x00080000,
            'DisallowSWT':        0x00100000,
            'AllowSWT':           0x00200000
        },

        'TrustSet': {
            'SetAuth':            0x00010000,
            'NoSkywell':          0x00020000,
            'SetNoSkywell':       0x00020000,
            'ClearNoSkywell':     0x00040000,
            'SetFreeze':          0x00100000,
            'ClearFreeze':        0x00200000
        },

        'OfferCreate': {
            'Passive':            0x00010000,
            'ImmediateOrCancel':  0x00020000,
            'FillOrKill':         0x00040000,
            'Sell':               0x00080000
        },

        'Payment': {
            'NoSkywellDirect':    0x00010000,
            'PartialPayment':     0x00020000,
            'LimitQuality':       0x00040000
        },

        'RelationSet': {
            'Authorize':          0x00000001,
            'Freeze':             0x00000011
        }
    }

    OfferTypes = ['Sell', 'Buy']
    RelationTypes = ['trust', 'authorize', 'freeze', 'unfreeze']
    AccountSetTypes = ['property', 'delegate', 'signer']

    def parseJson(self, val):
        self.tx_json = val
        return self

    def getAccount(self):
        return self.tx_json['Account']

    def getTransactionType(self):
        return self.tx_json['TransactionType']

    def setSecret(self, secret):
        self._secret = secret

    """
    * just only memo data
    * @param memo
    """

    def addMemo(self, memo):
        if (isinstance(memo, str)):
            self.tx_json['memo_type'] = TypeError('invalid memo type')
            return self
        if (len(memo) > 2048):
            self.tx_json['memo_len'] = TypeError('memo is too long')
            return self
        _memo = {}
        _memo['MemoData'] = __stringToHex(memo.encode("UTF-8"))
        self.tx_json['Memos'] = (self.tx_json['Memos']
                                 or []).append({'Memo': _memo})

    def setFee(self, fee):
        _fee = safe_int(fee)
        if (math.isnan(_fee)):
            self.tx_json['Fee'] = TypeError('invalid fee')
            return self
        if (fee < 10):
            self.tx_json['Fee'] = TypeError('fee is too low')
            return self
        self.tx_json['Fee'] = _fee
