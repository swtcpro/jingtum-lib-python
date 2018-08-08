"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/1
 * Time: 13:11
 * Description: 
"""
import json

import schedule
from eventemitter import EventEmitter
from websocket import create_connection

from jingtum_python_lib.config import Config
from jingtum_python_lib.logger import logger

test_evn = False
TEST_MODE = "test"
PROD_MODE = "product"


class Server(Config):
    online_states = ['syncing', 'tracking', 'proposing', 'validating', 'full', 'connected']

    def __init__(self, remote):
        super(Server, self).__init__()
        # global test_evn
        # 设置Server的状态信息
        self.ws = None
        self.remote = remote
        self.connected = False
        self.opened = False
        self.state = "offline"
        self.id = 0
        self.timer = 0
        # 此处可以设置生产环境或开发环境
        self.set_mode(TEST_MODE)

        # 支持异步消息机制而设置的job变量，用在handle_close方法中
        self.job = {}

    def set_mode(self, mode=TEST_MODE):
        if mode == TEST_MODE:
            self.ws_address = Config.test_web_socket_address
            self.tt_address = Config.test_ttong_address
        else:
            self.ws_address = Config.sdk_web_socket_address
            self.tt_address = Config.ttong_address


class WebSocketServer(Server):
    def __init__(self, remote):
        super(WebSocketServer, self).__init__(remote)
        self._shutdown = False
        self.emitter = EventEmitter()

    def connect(self, callback):
        if self.connected:
            return
            # if self.ws is None:
        #     self.ws.close()
        try:
            self.ws = create_connection(self.ws_address)
            self.opened = True
        except Exception as e:
            logger.error(e)
            return e

        self.emitter.on("open", self.socket_open)
        self.emitter.on('message', self.remote.handle_message)
        self.emitter.on('close', self.handle_close)
        return

    def socket_open(self):
        """
        socket打开的回调函数
        :return:
        """
        self.opened = True
        req = self.remote.subscribe(["ledger", "server"])
        return req.submit()

    # 代码进行到此处，接下来需要构建
    # 其他message、close和error的回调
    def handle_close(self):
        """
        handle close and error exception
        and should re-connect server after 3 seconds
        :return:
        """
        if self.state == 'offline':
            return
        self.set_state('offline')
        if self.timer != 0:
            return
        self.remote.emitter.emit('disconnect')
        self.timer = 3
        self.job = schedule.every(self.timer).seconds.do(self.connect_after_close)

    def connect_after_close(self, err):
        """
        当socket断掉之后的重连
        :return:
        """
        if not err:
            # 对应handle_close中的schedule.every方法
            schedule.cancel_job(self.job)
            self.timer = 0
            self.remote.emitter.emit('reconnect')

    def set_state(self, state):
        if state == self.state:
            return
        self.state = state
        self.connected = (state == 'online')
        if not self.connected:
            self.opened = False

    def send_message(self, command, data):
        """
        refuse to send msg if connection blows out
        :param command:
        :param data:
        :return:    backen 返回结果
        """
        if not self.opened:
            return
        req_id = (self.id + 1)
        msg = dict({'id': req_id, 'command': command}, **data)
        self.ws.send(json.dumps(msg))
        callback = self.ws.recv()
        return {'req_id': req_id, 'callback': callback}

    def send(self, data):
        ret = None
        data = json.dumps(data).encode('utf-8')
        try:
            self.ws.send(data)
        except Exception as e:
            print("websocket send error"), e

        return ret

    def close(self):
        _data = {
            "command": "close",
        }
        self._shutdown = True
        return self.send(_data)
