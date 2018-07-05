"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/7/5
 * Time: 16:19
 * Description: sha512
"""
import hashlib


class Sha512:
    def __init__(self):
        self.hash = hashlib.sha512()

    def add(self, bytes):
        self.hash.update(bytes)
        return self

    def addU32(self, i):
        return self.add([i >> 24 & 0xFF, i >> 16 & 0xFF, i >> 8 & 0xFF, i & 0xFF])

    def finish(self):
        return self.hash.digest()

    def first256(self):
        return self.finish()[0, 32]

    def first256BN(self):
        return self.first256()
