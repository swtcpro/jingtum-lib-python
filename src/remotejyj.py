"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/3
 * Time: 11:25
 * Description: main handler for backend system
 * one remote object one server, not many options onfiguration Parameters:
 * {
 *   local_sign: false, // default sign tx in jingtumd
 * }
"""
import sys
sys.path.append("..")

from inspect import isfunction
from src.transaction import Transaction
from src.utils import utils
from src.config import Config

from src.server import Server
from src.request import Request
from src.utils.cache import LRUCache

LEDGER_OPTIONS = ['closed', 'header', 'current']


class Remote:
    def __init__(self, options):
        self.opts = options
        self.local_sign = options.local_sign
        self.server = Server(self)
        self.status = {"ledger_index": 0}
        self.requests = {}
        self.cache = LRUCache(100)  # 100 size，为cache和path设置缓存
        self.path = LRUCache(2100)  # 2100 size

    def submit(self, command, data, filter, callback):
        if (isfunction(callback)):
            req_id = self.server.send_message(command, data)
            self.requests[req_id] = {
                # 此处还有些代码逻辑没实现
                # 根据command, data, filter, callback生成新的request对象
            }

    # def subscribe(self, address, secret):
    #     data = {
    #         "command": "subscribe",
    #         "account": address,
    #         "secret": secret
    #     }
    #     self.send(data)
    #     return None
    #
    # def unsubscribe(self, address):
    #     data = {
    #         "command": "unsubscribe",
    #         "account": address,
    #     }
    #     self.send(data)
    #     return None

    def subscribe(self, streams):
        request = Request(self, "subscribe")
        if streams is not None:
            request.message.streams = streams if isinstance(streams, list) else [streams]

        return request
    ##设置账号属性
    def buildAccountSetTx(self,options):
        tx=Transaction(self)
        if not options:
            tx.tx_json.obj =ValueError('invalid options type')
            return tx
        if not ~Transaction.AccountSetTypes.index(options.type):
            tx.tx_json.type =ValueError('invalid account set type')
            return tx
        if options.type=='property':
            return self.__buildAccountSet(options, tx)
        elif options.type=='delegate':
            return self.__buildDelegateKeySet(options, tx)
        elif options.type=='signer':
            return self.__buildSignerSet(options.tx)
        tx.tx_json.msg=Warning('build account set should not go here')
        return tx

    def __buildAccountSet(self,options,tx):
        src = options.source or options.fromnow or options.account
        set_flag = options.set_flag or options.set
        clear_flag = options.clear_flag or options.clear
        if not utils.isValidAmount():
            pass
        tx.tx_json.TransactionType = 'AccountSet'
        tx.tx_json.Account = src
        SetClearFlags = Transaction.set_clear_flags.AccountSet
        set_flag= self.__prepareFlag(set_flag,SetClearFlags)
        if set_flag:
            tx.tx_json.SetFlag = set_flag
        clear_flag = self.__prepareFlag(clear_flag, SetClearFlags)
        if clear_flag:
            tx.tx_json.ClearFlag = clear_flag
        return tx

    def __prepareFlag(self,flag,SetClearFlags):
        if isinstance(flag,int):
            flag=SetClearFlags[flag]
        else:
            flag=SetClearFlags['asf' + flag]
        return flag

    def __buildDelegateKeySet(self,options,tx):
        src = options.source or options.account or options.fromnow
        delegate_key = options.delegate_key
        if not utils.isValidAddress(src):
            tx.tx_json.delegate_key =Exception('invalid source address')
            return tx
        if not utils.isValidAddress(delegate_key):
            tx.tx_json.delegate_key =Exception('invalid regular key address')
            return tx
        tx.tx_json.TransactionType = 'SetRegularKey'
        tx.tx_json.Account = src
        tx.tx_json.RegularKey = delegate_key
        return tx
    def __buildSignerSet(self):
        return None

    #挂单
    def buildOfferCreateTx(self,options):
        tx = Transaction(self)
        if not options:
            tx.tx_json.obj = TypeError('invalid options type')
            return tx
        offer_type = options.type
        src = options.source or options.fromnow or options.account
        taker_gets = options.taker_gets or options.pays
        taker_pays = options.taker_pays or options.gets
        if not utils.isValidAddress(src):
            tx.tx_json.src =Exception('invalid source address')
            return tx
        if not isinstance(offer_type, str)  or not ~Transaction.OfferTypes.indexOf(offer_type):
            tx.tx_json.offer_type =TypeError('invalid offer type')
            return tx
        taker_gets2, taker_pays2=any
        if  isinstance(taker_gets,str) and not int(taker_gets) and not float(taker_gets):
            tx.tx_json.taker_gets2 =Exception('invalid to pays amount')
            return tx
        if not taker_gets  and not utils.isValidAmount(taker_gets):
            tx.tx_json.taker_gets2 =Exception('invalid to pays amount object')
            return tx
        if isinstance( taker_pays,str) and not int(taker_pays) and not not float(taker_pays):
            tx.tx_json.taker_pays2 =Exception('invalid to gets amount')
            return tx
        if not taker_pays and not utils.isValidAmount(taker_pays):
            tx.tx_json.taker_pays2 =Exception('invalid to gets amount object')
            return tx
        tx.tx_json.TransactionType = 'OfferCreate'
        if offer_type is 'Sell':
            tx.setFlags(offer_type)
        tx.tx_json.Account = src
        tx.tx_json.TakerPays = taker_pays2 if taker_pays2 else self.ToAmount(taker_pays)
        tx.tx_json.TakerGets = taker_gets2 if taker_gets2 else self.ToAmount(taker_gets)
        return tx

    def ToAmount(self,amount):
        if (amount.value and int(amount.value) > 100000000000):
           return  Exception('invalid amount: amount\'s maximum value is 100000000000')
        if amount.currency is Config.currency:
        # 这段需要修改
            return str(int(amount.value).mul(1000000.00))
        return amount

    #取消挂单
    def buildOfferCancelTx(self,options):
        tx =Transaction(self)
        if not options:
            tx.tx_json.obj = Exception('invalid options type')
            return tx
        src = options.source or options.fromnow or options.account
        sequence = options.sequence
        if not utils.isValidAddress(src):
            tx.tx_json.src = Exception('invalid source address')
            return tx
        if not int(sequence) and not float(sequence):
            tx.tx_json.sequence = Exception('invalid sequence param')
            return tx
        tx.tx_json.TransactionType = 'OfferCancel'
        tx.tx_json.Account = src
        tx.tx_json.OfferSequence = int(sequence)
        return tx