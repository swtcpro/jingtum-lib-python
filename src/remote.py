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

LEDGER_OPTIONS = ['closed', 'header', 'current']


class Remote:
    def __init__(self, options):
        self.opts = options
        self.local_sign = options.local_sign
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
        if self.server:
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
                command: command,
                data: data,
                filter: filter,
                callback: callback
            }

    def subscribe(self, streams):
        request = Request(self, "subscribe")
        if streams is not None:
            request.message.streams = streams if isinstance(streams, list) else [streams]
        return request
