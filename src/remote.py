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
from numbers import Number

from eventemitter import EventEmitter

# rename jingtum-python-baselib to jingtum_python_baselib as python seem can't recognize -
# from jingtum_python_baselib.src.wallet import Wallet as baselib
from src.config import Config
from src.request import Request
from src.server import Server, WebSocketServer
from src.transaction import Transaction
from src.utils.cache import LRUCache
from src.utils.utils import utils
from src import util

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
            return 'server not ready'
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

    def submit(self, command, data):
        """
        request to server and backend
        :param command:
        :param data:
        :param filter:
        :return: {'req_id': req_id, 'callback': callback}
        """
        result = self.server.send_message(command, data)
        self.requests[result['req_id']] = {
            'command': command,
            'data': data,
            # 'filter': filter,
            'callback': result['callback']
        }
        return result['callback']
        # callback()

    def subscribe(self, streams):
        request = Request(self, "subscribe", None)
        if streams:
            request.message['streams'] = streams if isinstance(streams, list) else [streams]
        return request

    # ---------------------- info request - -------------------
    # ---------------------- info request - -------------------
    # ---------------------- info request - -------------------

    def request_server_info(self):
        """
        请求服务器底层信息
        request server info
        return version, ledger, state and node id
        no option is required
        :return: {Request}
        """
        return Request(self, 'server_info', None)

    def request_ledger_closed(self):
        """
        获取最新账本信息
        request last closed ledger index and hash
        :return:   {Request}
        """
        return Request(self, 'ledger_closed', None)

    def request_ledger(self, options):
        """
        获取某一账本具体信息
        :param options: dict{ledger_index: Number, ledger_hash: hash, string}
        :return:
        """
        cmd = 'ledger'
        filter = True
        req = Request(self, cmd, filter)
        if not isinstance(options, dict):
            req.message['type'] = Exception('invalid options type')
            return req
        if options['ledger_index'] and isinstance(options['ledger_index'], int):
            req.message['ledger_index'] = options['ledger_index']
        elif options['ledger_hash'] and util.is_valid_hash(options['ledger_hash']):
            req.message['ledger_hash'] = options['ledger_hash']
        if 'full' in options.keys() and isinstance(options['full'], bool):
            req.message['full'] = options['full']
            filter = False
        if 'expand' in options.keys() and isinstance(options['expand'], bool):
            req.message['expand'] = options['expand']
            filter = False
        if 'transactions' in options.keys() and isinstance(options['transactions'], bool):
            req.message['transactions'] = options['transactions']
            filter = False
        if 'accounts' in options.keys() and isinstance(options['accounts'], bool):
            req.message['accounts'] = options['accounts']
            filter = False
        return req

    def request_tx(self, options):
        """
        查询某一交易具体信息
        :param options:
        :return:
        """
        req = Request(self, 'tx', None)
        if not isinstance(options, dict):
            req.message['type'] = Exception('invalid options type')
            return req
        if not util.is_valid_hash(options['hash']):
            req.message['hash'] = Exception('invalid tx hash')
            return req
        req.message['transaction'] = options['hash']
        return req

    def request_account(self, type, options, req):
        """
        正在撰写当中，未完成




        此处开始
        :param type:
        :param options:
        :param req:
        :return:
        """
        req.command = type
        account = options['account']
        ledger = options['ledger']
        peer = options['peer']
        limit = options['limit']
        marker = options['marker']
        # req.message['relation_type'] =

        return

    def request_account_info(self, options):
        """
        请求账号信息
        :param options: {account:’xxx’}
        :return:
        """
        req = Request(self, None, None)
        if not isinstance(options, dict):
            req.message['type'] = Exception('invalid options type')
            return req

        return self.request_account('account_info', options, req)

    def parse_transaction(self, data):
        data = json.loads(data)
        return data['result']

    def parse_ledger(self, data):
        data = json.loads(data)
        return data['result']['ledger']

    def parse_ledger_closed(self, data):
        data = json.loads(data)
        return {
            'ledger_hash': data['result']['ledger_hash'],
            'ledger_index': data['result']['ledger_index']
        }

    def parse_server_info(self, data):
        data = json.loads(data)
        return {
            'version': data['result']['info']['build_version'],
            'ledgers': data['result']['info']['complete_ledgers'],
            'node': data['result']['info']['pubkey_node'],
            'state': data['result']['info']['server_state']
        }


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
    tx = Transaction(self, None)
    if not options:  # typeof options没有转换
        tx.tx_json['obj'] = Exception('invalid options type')
        return tx
    if options.__contains__('source'):
        src = options['source']
    elif options.__contains__('from'):
        src = options['from']
    elif options.__contains__('account'):
        src = options['account']

    if options.__contains__('destination'):
        dst = options['destination']
    elif options.__contains__('to'):
        dst = options['to']
    amount = options['amount']

    if not baselib.isValidAddress(src):
        tx.tx_json['src'] = Exception('invalid source address')
        return tx
    if not baselib.isValidAddress(dst):
        tx.tx_json['dst'] = Exception('invalid destination address')
        return tx

    if not utils.isValidAmount(amount):
        tx.tx_json['amount'] = Exception('invalid amount')
        return tx

    tx.tx_json['TransactionType'] = 'Payment'
    tx.tx_json['Account'] = src
    tx.tx_json['Amount'] = ToAmount(amount)
    tx.tx_json['Destination'] = dst
    return tx


def __buildRelationSet(options, tx):
    if options.__contains__('source'):
        src = options['source']
    elif options.__contains__('from'):
        src = options['from']
    elif options.__contains__('account'):
        src = options['account']

    des = options['target']
    limit = options['limit']

    if not baselib.isValidAddress(src):
        tx.tx_json['src'] = Exception('invalid source address')
        return tx
    if not baselib.isValidAddress(des):
        tx.tx_json['des'] = Exception('invalid target address')
        return tx
    if not utils.isValidAmount(limit):
        tx.tx_json['limit'] = Exception('invalid amount')
        return tx

    if options['type'] == 'unfreeze':
        tx.tx_json['TransactionType'] = 'RelationDel'
    else:
        tx.tx_json['TransactionType'] = 'RelationSet'
    tx.tx_json['Account'] = src
    tx.tx_json['Target'] = des
    if options['type'] == 'authorize':
        tx.tx_json['RelationType'] = '1'
    else:
        tx.tx_json['RelationType'] = '3'
    if limit:
        tx.tx_json['LimitAmount'] = limit
    return tx


def __buildTrustSet(options, tx):
    if options.__contains__('source'):
        src = options['source']
    elif options.__contains__('from'):
        src = options['from']
    elif options.__contains__('account'):
        src = options['account']
    limit = options['limit']
    quality_out = options['quality_out']
    quality_in = options['quality_in']

    if not baselib.isValidAddress(src):
        tx.tx_json['src'] = Exception('invalid source address')
        return tx
    if not utils.isValidAmount(limit):
        tx.tx_json['limit'] = Exception('invalid amount')
        return tx

    tx.tx_json['TransactionType'] = 'TrustSet'
    tx.tx_json['Account'] = src
    if limit:
        tx.tx_json['LimitAmount'] = limit
    if quality_in:
        tx.tx_json['QualityIn'] = quality_in
    if quality_out:
        tx.tx_json['QualityOut'] = quality_out
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
        tx.tx_json['obj'] = Exception('invalid options type')
        return tx
    if not ~Transaction.RelationTypes.index(options.type):
        tx.tx_json['type'] = Exception('invalid relation type')
        return tx
    if options['type'] == 'trust':
        return self.__buildTrustSet(options, tx)
    elif options['type'] == 'authorize' or \
            options['type'] == 'freeze' or options['type'] == 'unfreeze':
        return self.__buildRelationSet(options, tx)
    tx.tx_json['msg'] = Exception('build relation set should not go here')
    return tx
