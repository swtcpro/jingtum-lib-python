# var utils = require('../src/utils')
# var extend = require('extend')
# var UInt = require('./uint').UInt

from src.lib.uint import UInt
from src.utils import utils
#
# UInt256 support
#

# var UInt256 = extend(def ():
#     # Internal form: NaN or BigInteger
#     this._value = NaN
# , UInt)
class UInt256(UInt):
    def __init__(self):
        self._value=None
        UInt256.width = 32
        # UInt256.prototype = extend({}, UInt.prototype)
        # UInt256.prototype.constructor = UInt256

        HEX_ZERO = UInt256.HEX_ZERO = '00000000000000000000000000000000' + '00000000000000000000000000000000'
        HEX_ONE = UInt256.HEX_ONE = '00000000000000000000000000000000' + '00000000000000000000000000000001'
        STR_ZERO = UInt256.STR_ZERO = utils.hexToString(HEX_ZERO)
        STR_ONE = UInt256.STR_ONE = utils.hexToString(HEX_ONE)
