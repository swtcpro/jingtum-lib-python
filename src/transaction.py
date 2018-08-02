# coding=utf-8
import json
import math

from src.config import Config
from src.utils.utils import is_number, utils
from jingtum_python_baselib.utils import *
from jingtum_python_baselib.wallet import Wallet

fee = Config.FEE or 10000

set_clear_flags = {
    'AccountSet': {
        'asfRequireDest': 1,
        'asfRequireAuth': 2,
        'asfDisallowSWT': 3,
        'asfDisableMaster': 4,
        'asfNoFreeze': 6,
        'asfGlobalFreeze': 7
    }
}

transaction_global_flags = {
    # Universal flags can apply to any transaction type
    'Universal': {
        'FullyCanonicalSig': 0x80000000
    },

    'AccountSet': {
        'RequireDestTag': 0x00010000,
        'OptionalDestTag': 0x00020000,
        'RequireAuth': 0x00040000,
        'OptionalAuth': 0x00080000,
        'DisallowSWT': 0x00100000,
        'AllowSWT': 0x00200000
    },

    'TrustSet': {
        'SetAuth': 0x00010000,
        'NoSkywell': 0x00020000,
        'SetNoSkywell': 0x00020000,
        'ClearNoSkywell': 0x00040000,
        'SetFreeze': 0x00100000,
        'ClearFreeze': 0x00200000
    },

    'OfferCreate': {
        'Passive': 0x00010000,
        'ImmediateOrCancel': 0x00020000,
        'FillOrKill': 0x00040000,
        'Sell': 0x00080000
    },

    'Payment': {
        'NoSkywellDirect': 0x00010000,
        'PartialPayment': 0x00020000,
        'LimitQuality': 0x00040000
    },

    'RelationSet': {
        'Authorize': 0x00000001,
        'Freeze': 0x00000011
    }
}

OfferTypes = ['Sell', 'Buy']
RelationTypes = ['trust', 'authorize', 'freeze', 'unfreeze']
AccountSetTypes = ['property', 'delegate', 'signer']


def filterFun(v):
    return v


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
    if (not is_number(num)):
        return float('nan')
    if (isinstance(num, bool) and num):
        return 1
    if (isinstance(num, bool) and not num):
        return 0
    if (isinstance(num, (int, float))):
        return num
    if '.' in num:
        return float(num)
    else:
        return int(num)


def max_amount(amount):
    if (isinstance(amount, str) and is_number(amount)):
        _amount = safe_int(Number(amount) * (1.0001))
        return str(_amount)
    if (isinstance(amount, dict) and utils.is_valid_amount(amount)):
        _value = Number(amount['value']) * (1.0001)
        amount['value'] = str(_value)
        return amount
    return Exception('invalid amount too max')


class Transaction:
    def __init__(self, remote, filter):
        # TODO(zfn):事件驱动注册待实现
        self.remote = remote
        self.tx_json = {"Flags": 0, "Fee": fee}
        self._filter = filter or filterFun
        self._secret = None

    def parseJson(self, val):
        self.tx_json = val
        return self

    def get_account(self):
        return self.tx_json['Account']

    def get_transaction_type(self):
        return self.tx_json['TransactionType']

    """
     * set secret
     * @param secret
     * 传入密钥
    """
    def set_secret(self, secret):
        if not Wallet.is_valid_secret(secret):
            self.tx_json._secret = Exception('valid secret')
            return
        self._secret = secret

    """
    * just only memo data
    * @param memo
    """
    def add_memo(self, memo):
        if (not isinstance(memo, str)):
            self.tx_json['memo_type'] = TypeError('invalid memo type')
            return self
        if (len(memo) > 2048):
            self.tx_json['memo_len'] = TypeError('memo is too long')
            return self
        _memo = {}
        _memo['MemoData'] = bytes_to_hex(memo.encode('utf8')).lower()
        if 'Memos' in self.tx_json:
            self.tx_json['Memos'].append({'Memo': _memo})
        else:
            self.tx_json['Memos'] = [{'Memo': _memo}]

    def set_fee(self, fee):
        _fee = safe_int(fee)
        if (math.isnan(_fee)):
            self.tx_json['Fee'] = TypeError('invalid fee')
            return self
        if (fee < 10):
            self.tx_json['Fee'] = TypeError('fee is too low')
            return self
        self.tx_json['Fee'] = _fee

    """
    * set a path to payment
    * this path is repesented as a key, which is computed in path find
    * so if one path you computed self is not allowed
    * when path set, sendmax is also set.
    * @param path
    """
    def set_path(self, key):
        # sha1 string
        if (not isinstance(key, str) and len(key) != 40):
            return Exception('invalid path key')

        item = self.remote._paths.get(key)
        if (item is not None):
            return Exception('non exists path key')

        if (item['path'] == '[]'):  # 沒有支付路径，不需要传下面的参数
            return
        path = json.load(item.path)
        self.tx_json['Paths'] = path
        amount = max_amount(item['choice'])
        self.tx_json['SendMax'] = amount

    """
    * limit send max amount
    * @param amount
    """
    def set_send_max(self, amount):
        if (utils.is_valid_amount(amount) is not None):
            return Exception('invalid send max amount')
        self.tx_json['SendMax'] = amount

    """
    * transfer rate
    * between 0 and 1, type is number
    * @param rate
    """

    def set_transfer_rate(self, rate):
        if (not isinstance(rate, (int, float)) or rate < 0 or rate > 1):
            return Exception('invalid transfer rate')
        self.tx_json['TransferRate'] = (rate + 1) * 1e9

    """
    * set transaction flags
    *
     """
    def set_flags(self, flags):
        if (flags is None):
            return

        if isinstance(flags, (int, float)):
            self.tx_json['Flags'] = flags
            return

        index = self.get_transaction_type()
        if flags.index:
            transaction_flags = transaction_global_flags[index]
        else:
            transaction_flags = {}
        if (isinstance(flags, list)):
            flag_set = flags
        else:
            flag_set = [flags]

        for flag in flag_set:
            if transaction_flags.__contains__(flag):
                self.tx_json['Flags'] += transaction_flags[flag]

    def sign(self):
        if self.tx_json.__contains__('Sequence'):
            self.signing()
        else:
            req = self.remote.request_account_info({'account': self.tx_json['Account'], 'type': 'trust'})
            result=req.submit()
            data = json.loads(result['callback'])
            self.tx_json['Sequence'] = data['result']['account_data']['Sequence']
            self.signing()

    def signing(self):
        from jingtum_python_baselib.Serializer import Serializer
        self.tx_json['Fee'] = self.tx_json['Fee'] / 1000000

        # payment
        if (self.tx_json.__contains__('Amount') and '{' not in json.dumps(self.tx_json['Amount'])):
            # 基础货币
            self.tx_json['Amount'] = Number(self.tx_json['Amount']) / 1000000

        if self.tx_json.__contains__('Memos'):
            memo_list = self.tx_json['Memos']
            i = 0
            while i < len(memo_list):
                memo_list[i]["Memo"]["MemoData"] = hex_to_str(memo_list[i]["Memo"]["MemoData"])
                i += 1

        if (self.tx_json.__contains__('SendMax') and isinstance(self.tx_json['SendMax'], str)):
            self.tx_json['SendMax'] = Number(self.tx_json['SendMax']) / 1000000

        # order
        if (self.tx_json.__contains__('TakerPays') and '{' not in json.dumps(self.tx_json['TakerPays'])):
            # 基础货币
            self.tx_json['TakerPays'] = Number(self.tx_json['TakerPays']) / 1000000

        if (self.tx_json.__contains__('TakerGets') and '{' not in json.dumps(self.tx_json['TakerGets'])):
            # 基础货币
            self.tx_json['TakerGets'] = Number(self.tx_json['TakerGets']) / 1000000

        wt = Wallet(self._secret)
        self.tx_json['SigningPubKey'] = wt.get_public_key()
        prefix = 0x53545800
        serial = Serializer(None)
        hash = serial.from_json(self.tx_json).hash(prefix)
        self.tx_json['TxnSignature'] = wt.sign(hash)
        self.tx_json['blob'] = serial.from_json(self.tx_json).to_hex()
        self.local_sign = True
        return self.tx_json['blob']

    def submit(self):
        for key in self.tx_json:
            if isinstance(self.tx_json[key], Exception):
                return self.tx_json[key]

        data = {}
        if self.remote.local_sign:  # 签名之后传给底层
            self.sign()
            data = {
                'tx_blob': self.tx_json['blob']
            }
        elif self.tx_json['TransactionType'] == 'Signer':  # 直接将blob传给底层
            data = {
                "tx_blob": self.tx_json['blob']
            }
        else:  # 不签名交易传给底层
            data = {
                "secret": self._secret,
                "tx_json": self.tx_json
            }
        return self.remote.submit('submit', data)
