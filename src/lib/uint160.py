# utils = require('../src/utils')
# config = require('./config')
# extend = require('extend')
# BigInteger = require('./jsbn').BigInteger
# UInt = require('./uint').UInt
# Base = require('./base').Base
from src.lib.config import config
from src.utils import utils
from src.lib.base import Base
from src.lib.uint import UInt
from src.config import Config
#
# UInt160 support
#
class UInt160(UInt):
    def __init__(self):
        self._value = None
        self._version_byte = None
        self._update()
        self.width = 20
        # UInt160.prototype = extend({}, UInt.prototype)
        # UInt160.prototype.constructor = UInt160
        self.ACCOUNT_ZERO = UInt160.ACCOUNT_ZERO = 'jjjjjjjjjjjjjjjjjjjjjhoLvTp'
        self.ACCOUNT_ONE = UInt160.ACCOUNT_ONE = 'jjjjjjjjjjjjjjjjjjjjBZbvri'
        self.HEX_ZERO = UInt160.HEX_ZERO = '0000000000000000000000000000000000000000'
        self.HEX_ONE = UInt160.HEX_ONE = '0000000000000000000000000000000000000001'
        self.STR_ZERO = UInt160.STR_ZERO = utils.hexToString(self.HEX_ZERO)
        self.STR_ONE = UInt160.STR_ONE = utils.hexToString(self.HEX_ONE)



    def set_version(self,j):
        self._version_byte = j
        return self


    def get_version(self):
        return self._version_byte


    # value = NaN on error.
    def parse_json(self,j):
        # Canonicalize and validate
        if config.accounts and (j in config.accounts):
            j = config.accounts[j].account


        if isinstance(j,int)and not j:
            # Allow raw numbers - DEPRECATED
            # This is used mostly by the test suite and is supported
            # as a legacy feature only. DO NOT RELY ON THIS BEHAVIOR.
            self._value = int(str(j))
            self._version_byte = Base.VER_ACCOUNT_ID
        elif isinstance(j,str):
            self._value = None
        elif j[0] is 'j':
            self._value = Base.decode_check(Base.VER_ACCOUNT_ID, j)
            self._version_byte = Base.VER_ACCOUNT_ID
        else:
            self.parse_hex(j)


        self._update()
        return self


    def parse_generic(self,j):
        # UInt.prototype.parse_generic.call(this, j)

        if not self._value:
            if isinstance(j,str) and j[0] is 'j':
                self._value = Base.decode_check(Base.VER_ACCOUNT_ID, j)



        self._update()
        return self


    # XXX Json form should allow 0 and 1, C++ doesn't currently allow it.
    def to_json(self,opts):
        opts = optsor {}

        if isinstance(self._value,int):
            # If this value has a type, return a Base58 encoded string.
            if isinstance(self._version_byte,int):
                output = Base.encode_check(self._version_byte, self.to_bytes())

                if opts.gateways and output in opts.gateways:
                    output = opts.gateways[output]


                return output
            else:
                return self.to_hex()


        return None

