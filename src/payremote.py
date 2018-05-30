# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 支付与设置关系模块
"""
import sys

sys.path.append("..")

# rename jingtum-python-baselib to jingtum_python_baselib as python seem can't recognize -
from jingtum_python_baselib.src.utils import utils as baselib
from payts import Transaction
from utils import utils
from bignumber import bignumber

# get from config.js
config = {
    'currency': 'SWT',
    'ACCOUNT_ZERO': 'jjjjjjjjjjjjjjjjjjjjjhoLvTp',
    'ACCOUNT_ONE': 'jjjjjjjjjjjjjjjjjjjjBZbvri',
    'fee': 10000,
};

# from为python关键词，options.from改为option.fromnow 需要修改option相关代码

"""
// ---------------------- transaction request --------------------
/**
 * return string if swt amount
 * @param amount
 * @returns {Amount}
"""


def ToAmount(amount):
    if (amount.value and int(amount.value) > 100000000000):
        # return Error('invalid amount: amount\'s maximum value is 100000000000')
        raise Exception('invalid amount: amount\'s maximum value is 100000000000')
    if (amount.currency == currency):
        # return new String(parseInt(Number(amount.value) * 1000000.00))
        return String(parseInt(bignumber(amount.value).mul(1000000.00)))
    return amount


class Remote:
    def __init__(self, options):
        self.opts = options
        self.local_sign = options.local_sign
        self.server = Server(self)
        self.status = {"ledger_index": 0}
        self.requests = {}
        self.cache = LRUCache(100)  # 100 size，为cache和path设置缓存
        self.path = LRUCache(2100)  # 2100 size

    """
     * payment
     * @param options
     *    source|from|account source account, required
     *    destination|to destination account, required
     *    amount payment amount, required
     * @returns {transaction}
     * 创建支付对象
     * come from remote.js
    """

    def buildPaymentTx(options):
        tx = Transaction(self)
        if not options:  # typeof options没有转换
            tx.tx_json.obj = Exception('invalid options type')
            return tx
        src = options.source or options.fromnow or options.account
        dst = options.destination or options.to
        amount = options.amount
        if not baselib.isValidAddress(src):
            tx.tx_json.src = Exception('invalid source address')
            return tx
        if not baselib.isValidAddress(dst):
            tx.tx_json.dst = Exception('invalid destination address')
            return tx
        if not utils.isValidAmount(amount):
            tx.tx_json.amount = Exception('invalid amount')
            return tx

        tx.tx_json.TransactionType = 'Payment'
        tx.tx_json.Account = src
        tx.tx_json.Amount = ToAmount(amount)
        tx.tx_json.Destination = dst
        return tx

    def __buildRelationSet(options, tx):
        src = options.source or options.fromnow or options.account
        des = options.target
        limit = options.limit

        if not baselib.isValidAddress(src):
            tx.tx_json.src = Exception('invalid source address')
            return tx
        if not baselib.isValidAddress(des):
            tx.tx_json.des = Exception('invalid target address')
            return tx
        if not utils.isValidAmount(limit):
            tx.tx_json.limit = Exception('invalid amount')
            return tx

        if options.type == 'unfreeze':
            tx.tx_json.TransactionType = 'RelationDel'
        else:
            tx.tx_json.TransactionType = 'RelationSet'
        tx.tx_json.Account = src
        tx.tx_json.Target = des
        if options.type == 'authorize':
            tx.tx_json.RelationType = '1'
        else:
            tx.tx_json.RelationType = '3'
        if (limit != void(0)):
            tx.tx_json.LimitAmount = limit
        return tx

    def __buildTrustSet(options, tx):
        src = options.source or options.fromnow or options.account
        limit = options.limit
        quality_out = options.quality_out
        quality_in = options.quality_in

        if not baselib.isValidAddress(src):
            tx.tx_json.src = Exception('invalid source address')
            return tx
        if not utils.isValidAmount(limit):
            tx.tx_json.limit = Exception('invalid amount')
            return tx

        tx.tx_json.TransactionType = 'TrustSet'
        tx.tx_json.Account = src
        if (limit != 0):
            tx.tx_json.LimitAmount = limit
        if quality_in:
            tx.tx_json.QualityIn = quality_in
        if quality_out:
            tx.tx_json.QualityOut = quality_out
        return tx

    """
     * add wallet relation set
     * @param options
     *    type: Transaction.RelationTypes
     *    source|from|account source account, required
     *    limit limt amount, required
     *    quality_out, optional
     *    quality_in, optional
     * @returns {Transaction}
     * 创建关系对象
    """

    def buildRelationTx(self, options):
        tx = Transaction(self)
        if not options:
            tx.tx_json.obj = Exception('invalid options type')
            return tx
        if not ~Transaction.RelationTypes.index(options.type):
            tx.tx_json.type = Exception('invalid relation type')
            return tx
        if options.type == 'trust':
            return self.__buildTrustSet(options, tx)
        elif options.type == 'authorize' or \
                options.type == 'freeze' or options.type == 'unfreeze':
            return self.__buildRelationSet(options, tx)
        tx.tx_json.msg = Exception('build relation set should not go here')
        return tx
