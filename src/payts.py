# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 支付与设置关系模块
"""
from src.config import Config
fee = Config.FEE or 10000

def stringToHex(s):
    result = ''
    for c in s:
        d = hex(ord(c)).replace('0x', '')
        if ord(c) > 16:
            result += ''.join(d)
        else:
            result += ''.join(d)
    return result

class Transaction:
    def __init__(self, remote):
        self._remote = remote
        self.tx_json = {"Flags": 0, "Fee": fee}
        # self._filter = filter or function(v) {return v};
        self._secret = 0;

    """
     * set secret
     * @param secret
     * come from transaction.js
     * 传入密钥
    """
    def setSecret(self, secret):
        self._secret = secret

    """
     * just only memo data
     * @param memo
     * 设置备注
    """
    def addMemo(self, memo):
        if not isinstance(memo, str):
            self.tx_json.memo_type = Exception('invalid memo type')
            return self
        if (len(memo) > 2048):
            self.tx_json.memo_len = Exception('memo is too long')
            return self
        _memo = {}
        _memo.MemoData = stringToHex(memo.encode('utf-8'))
        self.tx_json.Memos = self.tx_json.Memos + _memo

    """
     * submit request to server
     * @param callback
     * 提交支付
    """
    def submitblob(self, callback):
        if Exception:
            return callback('sign error: ', Exception)
        else:
            data = {
                "tx_blob": self.tx_json.blob
            }
            self._remote.submit('submit', data, self._filter, callback)

    def submit(self, callback):
        for key in self.tx_json:
            if isinstance(self.tx_json[key], Exception):
                return callback(self.tx_json[key].message)

        data = {}
        if self._remote._local_sign:  # 签名之后传给底层
            self.sign(Transaction.submitblob(self, callback))
        elif self.tx_json.TransactionType == 'Signer':  # 直接将blob传给底层
            data = {
                "tx_blob": self.tx_json.blob
            };
            self._remote.submit('submit', data, self._filter, callback)
        else:  # 不签名交易传给底层
            data = {
                "secret": self._secret,
                "tx_json": self.tx_json
            }
            self._remote.submit('submit', data, self._filter, callback)