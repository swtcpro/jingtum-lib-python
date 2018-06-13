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
import json
from inspect import isfunction
from numbers import Number

from src.server import Server, WebSocketServer
from src.request import Request
from src.utils.cache import LRUCache
from eventemitter import EventEmitter

# rename jingtum-python-baselib to jingtum_python_baselib as python seem can't recognize -
from jingtum_python_baselib.src.utils import utils as baselib
from src.transaction import Transaction
from src.utils.utils import utils
from src.config import Config

LEDGER_OPTIONS = ['closed', 'header', 'current']

"""
* ---------------------- transaction request --------------------
**
 * return string if swt amount
 * @param amount
 * @returns {Amount}
"""


def ToAmount(amount):
    if (amount.value and int(amount.value) > 100000000000):
        return Exception('invalid amount: amount\'s maximum value is 100000000000')
    if (amount.currency == Config.currency):
        # return new String(parseInt(Number(amount.value) * 1000000.00))
        return str(int(amount.value * 1000000.00))
    return amount


class Remote:
    def __init__(self, options={'server': 'ws://ts5.jingtum.com:5020', 'local_sign': True}):
        self.opts = options
        self.local_sign = options['local_sign']
        self.server = WebSocketServer(self)
        self.status = {"ledger_index": 0}
        self.requests = {}
        self.cache = LRUCache(100)  # 100 size，为cache和path设置缓存
        self.path = LRUCache(2100)  # 2100 size
        self.emitter = EventEmitter()

    def connect(self, callback):
        """
        connect first on every case
        :param callback:(error, result)
        :return:
        """
        if not self.server:
            return callback('server not ready')
        self.server.connect(callback)

    def is_connected(self):
        """
        check is remote is connected to jingtumd
        :return:
        """
        return self.server.connected

    def handle_message(self, data):
        # 此处可能要处理异常情况
        data = json.loads(data)

        if not data:
            return
        if data.type == 'ledgerClosed':
            self.handle_ledger_closed(data)
        elif data.type == 'serverStatus':
            self.handle_server_status(data)
        elif data.type == 'response':
            self.handle_response(data)
        elif data.type == 'transaction':
            self.handle_transaction(data)
        elif data.type == 'path_find':
            self.handle_path_find(data)

    def handle_ledger_closed(self, data):
        """
        update server ledger status
        supply data to outside include ledger, reserve and fee
        :param data:
        :return:
        """
        if data.ledger_index > self.status.ledger_index:
            self.status.ledger_index = data.ledger_index
            self.status.ledger_time = data.ledger_time
            self.status.reserve_base = data.reserve_base
            self.status.reserve_inc = data.reserve_inc
            self.status.fee_base = data.fee_base
            self.status.fee_ref = data.fee_ref
            self.emitter.emit('ledger_closed', data)

    def handle_server_status(self, data):
        """
        supply data to outside about server status
        :param data:
        :return:
        """
        self.update_server_status(data)
        self.emitter.emit('server_status', data)

    def update_server_status(self, data):
        self.status.load_base = data.load_base
        self.status.load_factor = data.load_factor
        if data.pubkey_node:
            self.status.pubkey_node = data.pubkey_node

        self.status.server_status = data.server_status
        online = ~Server.online_states.indexOf(data.server_status)
        self.server.set_state('online' if online else 'offline')

    def handle_response(self, data):
        """
        handle response by every websocket request
        :param data:
        :return:
        """
        req_id = data.id
        if isinstance(req_id, Number) or req_id < 0 or req_id > self.requests.__len__():
            return
        request = self.requests[req_id]
        # pass process it when null callback
        del self.requests[req_id]
        del data.id

        # check if data contain server info
        if data.result and data.status == 'success' and data.result.server_status:
            self.update_server_status(data.result)

        # return to callback
        if data.status == 'suceess':
            result = request.filter(data.result)
            request.callback(None, result)
        elif data.status == 'error':
            request.callback(data.error_message or data.error_exception)

    def handle_transaction(self, data):
        """
        handle transaction type response
        TODO supply more friendly transaction data
        :param data:
        :return:
        """
        tx = data.transaction.hash
        if self.cache.get(tx):
            return
        self.cache.set(tx, 1)
        self.emitter.emit('transactions', data)

    def handle_path_find(self, data):
        """
        emit path find date to other
        :param data:
        :return:
        """
        self.emitter.emit('path_find', data)

    def submit(self, command, data, filter, callback):
        """
        request to server and backend
        :param command:
        :param data:
        :param filter:
        :param callback:
        :return:
        """
        if isfunction(callback):
            req_id = self.server.send_message(command, data)
            self.requests[req_id] = {
                'command': command,
                'data': data,
                'filter': filter,
                'callback': callback
            }

    def subscribe(self, streams):
        request = Request(self, "subscribe", None)
        if streams:
            request.message['streams'] = streams if isinstance(streams, list) else [streams]
        return request

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

    def buildPaymentTx(self, options):
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
        if limit:
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
        if limit:
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
