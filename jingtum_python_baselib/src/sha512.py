# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 钱包依赖的模块
"""
import hashlib
import src.utils


class Sha512:
    def __init__(self):
        self.hash = hashlib.sha512()

    def add(self, bytes):
        for part in bytes:
            self.hash.update(hex(part).encode("utf-8"))
            # self.hash.update(bytes)
        return self

    def addU32(self, i):
        return self.add([i >> 24 & 0xFF, i >> 16 & 0xFF, i >> 8 & 0xFF, i & 0xFF])

    def finish(self):
        return self.hash.digest()

    def first256(self):
        return self.finish()

"""
def first256BN(self):
    return BN(self.first256())
"""