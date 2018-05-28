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
from inspect import isfunction
from payts import Transaction
from utils import utils
from config import currency
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
            tx.tx_json.obj = Error('invalid options type')
            return tx
        if not ~Transaction.AccountSetTypes.index(options.type):
            tx.tx_json.type = Error('invalid account set type')
            return tx
        if options.type=='property':
            return self.__buildAccountSet(options, tx)
        elif options.type=='delegate':
            return self.__buildDelegateKeySet(options, tx)
        elif options.type=='signer':
            return self.__buildSignerSet(options.tx)
        tx.tx_json.msg=Error('build account set should not go here')
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
        if (set_flag and (set_flag = __prepareFlag(set_flag,SetClearFlags))):
            tx.tx_json.SetFlag = set_flag
        if (clear_flag and (clear_flag = __prepareFlag(clear_flag,SetClearFlags))):
            tx.tx_json.ClearFlag = clear_flag
        return tx

    def __prepareFlag(self,flag,SetClearFlags):
        if(type(flag)=='number'):
            flag=SetClearFlags[flag]
        else:
            flag=SetClearFlags['asf' + flag]
        return flag

    def __buildDelegateKeySet(self,options,tx):
        src = options.source or options.account or options.fromnow
        delegate_key = options.delegate_key
        if not utils.isValidAddress(src):
            tx.tx_json.delegate_key =  Error('invalid source address')
            return tx
        if not utils.isValidAddress(delegate_key):
            tx.tx_json.delegate_key =  Error('invalid regular key address')
            return tx
        tx.tx_json.TransactionType = 'SetRegularKey'
        tx.tx_json.Account = src
        tx.tx_json.RegularKey = delegate_key
        return tx
    def __buildSignerSet(self):
        return None

    #挂单
    def buildOfferCreateTx(self,options):
        tx = Transaction(slef)
        if not options:
            tx.tx_json.obj = Error('invalid options type')
            return tx
        offer_type = options.type
        src = options.source or options.fromnow or options.account
        taker_gets = options.taker_gets or options.pays
        taker_pays = options.taker_pays or options.gets
        if not utils.isValidAddress(src):
            tx.tx_json.src = Error('invalid source address')
            return tx
         if not isinstance(offer_type, str)  or not ~Transaction.OfferTypes.indexOf(offer_type):
            tx.tx_json.offer_type =  Error('invalid offer type')
            return tx
        taker_gets2, taker_pays2=''
        if  isinstance(taker_gets,str) and not int(taker_gets) and not float(taker_gets):
            tx.tx_json.taker_gets2 = Error('invalid to pays amount')
            return tx
        if not taker_gets  and not utils.isValidAmount(taker_gets):
            tx.tx_json.taker_gets2 = Error('invalid to pays amount object')
            return tx
        if isinstance( taker_pays,str) and not int(taker_pays) and not not float(taker_pays):
            tx.tx_json.taker_pays2 = Error('invalid to gets amount')
            return tx
        if not taker_pays and not utils.isValidAmount(taker_pays):
            tx.tx_json.taker_pays2 = Error('invalid to gets amount object')
            return tx
        tx.tx_json.TransactionType = 'OfferCreate'
        if offer_type is 'Sell':
            tx.setFlags(offer_type)
        tx.tx_json.Account = src
        tx.tx_json.TakerPays = taker_pays2 if taker_pays2 else ToAmount(taker_pays)
        tx.tx_json.TakerGets = taker_gets2 if taker_gets2 else ToAmount(taker_gets)
        return tx

    def ToAmount(self,amount):
        if (amount.value and int(amount.value) > 100000000000):
           return Error('invalid amount: amount\'s maximum value is 100000000000')
        if amount.currency is currency:
        # 这段需要修改
            return str(int(long(amount.value).mul(1000000.00)))
        return amount

    #取消挂单
    def buildOfferCancelTx(self,options):
        tx =Transaction(self)
        if not options:
            tx.tx_json.obj = Error('invalid options type')
            return tx
        src = options.source or options.fromnow or options.account
        sequence = options.sequence
        if not utils.isValidAddress(src):
            tx.tx_json.src = Error('invalid source address')
            return tx
        if not int(sequence) and not float(sequence):
            tx.tx_json.sequence =Error('invalid sequence param')
            return tx
        tx.tx_json.TransactionType = 'OfferCancel'
        tx.tx_json.Account = src
        tx.tx_json.OfferSequence = int(sequence)
        return tx