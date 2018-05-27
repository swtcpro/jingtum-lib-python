"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/1
 * Time: 13:11
 * Description: 
"""
from websocket import create_connection
from src.config import Config
from src.logger import logger
from eventemitter import EventEmitter
import json

test_evn = False
TEST_MODE = "test"
PROD_MODE = "product"


class Server(Config):
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

    def set_mode(self, mode=TEST_MODE):
        if mode == TEST_MODE:
            self.ws_address = Config.test_web_socket_address
            self.tt_address = Config.test_ttong_address
        else:
            self.ws_address = Config.sdk_web_socket_address
            self.tt_address = Config.ttong_address


class WebSocketServer(Server):
    def __init__(self):
        super(WebSocketServer, self).__init__()
        self._shutdown = False
        self.emitter = EventEmitter()

    def connect(self, callback):
        if self.connected:
            return
        if self.ws is None:
            self.ws.close()
        try:
            self.ws = create_connection(self.ws_address)
        except Exception as e:
            logger.error(e)
            return e

        self.emitter.on("open", self.socket_open(callback=callback))

    def socket_open(self, callback):
        """
        socket打开的回调函数
        :return:
        """
        self.opened = True
        req = self.remote.subscribe(["ledger", "server"])
        req.submit(callback=callback)

    # 代码进行到此处，接下来需要构建
    # 其他message、close和error的回调
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #

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
