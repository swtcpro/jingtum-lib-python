# var sjcl = require('./sjcl')
# var BigInteger = require('./jsbn').BigInteger

# Abstract UInt class
# Base class for UInt classes

class UInt:
    # Internal form: NaN or BigInteger
    def __init__(self, remote):
        self._value = None
        self._update()


    def _update(self):
        pass
    def json_rewrite(self,j, opts):
        return self.from_json(j).to_json(opts)



    # Return a new UInt from j.
    def from_hex(self,j):
        if isinstance(j,self):
            return j.clone()
        else:
            return (self()).parse_hex(j)



    # Return a new UInt from j.
    def from_json(self,j):
        if isinstance(j,self):
            return j.clone()
        else:
            return (self()).parse_json(j)



    # Return a new UInt from j.
    def from_bits(self,j):
        if isinstance(j,self):
            return j.clone()
        else:
            return (self()).parse_bits(j)



    # Return a new UInt from j.
    def from_bytes(self,j):
        if isinstance(j,self):
            return j.clone()
        else:
            return (self()).parse_bytes(j)



    # Return a new UInt from j.
    def from_bn(self,j):
        if isinstance(j,self):
            return j.clone()
        else:
            return (self()).parse_bn(j)



    # Return a new UInt from j.
    def from_number(self,j):
        if isinstance(j,self):
            return j.clone()
        else:
            return (self()).parse_number(j)



    def is_valid(self,j):
        return self.from_json(j).is_valid()


    def clone(self):
        return self.copyTo(self.constructor())


    # Returns copy.
    def copyTo(self,d):
        d._value = self._value


        if isinstance(d._update,'function'):
            d._update()
        return d


    def equals(self,d):
        return isinstance(self._value,int) and isinstance(d._value,int) and self._value.equals(d._value)


    def is_valid(self):
        return isinstance(self._value,int)


    def is_zero(self):
        return self._value.equals(int.ZERO)


    """"
     * Update any derivative values.
     *
     * This allows subclasses to maintain caches of any data that they derive from
     * the main _value. For example, the Currency class keeps the currency type, the
     * currency code and other information about the currency cached.
     *
     * The reason for keeping this mechanism in this class is so every subclass can
     * call it whenever it modifies the internal state.
    """
    def _update(self):
        pass
        # Nothing to do by default. Subclasses will override this.


    def parse_hex(self,j):
        if isinstance(j,str) and j.length is (self.constructor.width * 2):
            self._value = int(j, 16)
        else:
            self._value = None


        self._update()
        return self


    def parse_bits(self,j):
        if sjcl.bitArray.bitLength(j) is not self.constructor.width * 8:
            self._value = None
        else:
            bytes = sjcl.codec.bytes.fromBits(j)
            self.parse_bytes(bytes)


        self._update()
        return self



    def parse_bytes(self,j):

        if isinstance(j,list) or j.length is not self.constructor.width:
            self._value = None
        else:
            self._value = int([0].concat(j), 256)


        self._update()
        return self



        parse_json = UInt.prototype.parse_hex

    def parse_bn(self,j):
        if isinstance(j,sjcl.bn)  and j.bitLength() <= self.constructor.width * 8:
            bytes = sjcl.codec.bytes.fromBits(j.toBits())
            self._value = int(bytes, 256)
        else:
            self._value = None


        self._update()
        return self


    def parse_number(self,j):
        self._value = None


        if isinstance(j,int) and isFinite(j) and j >= 0:
            self._value =int(str(j))


        self._update()
        return self


    # Convert from internal form.
    def to_bytes(self):
        if not isinstance(self._value,int) :
            return None


        bytes = self._value.toByteArray()
        bytes = map(self._func(),bytes)


        target = self.constructor.width

        # XXX Make sure only trim off leading zeros.
        bytes = bytes.slice(-target)

        while bytes.length < target:
            bytes.unshift(0)

        return bytes

    def _func(self,b):
        return (b + 256) % 256

    def to_hex(self):
        if not isinstance(self._value,int):
            return None


        bytes = self.to_bytes()
        return sjcl.codec.hex.fromBits(sjcl.codec.bytes.toBits(bytes)).toUpperCase()


        to_json = UInt.prototype.to_hex

    def to_bits(self):
        if not isinstance(self._value,int):
            return None


        bytes = self.to_bytes()
        return sjcl.codec.bytes.toBits(bytes)


    def to_bn(self):
        if not isinstance(self._value,int):
            return None


        bits = self.to_bits()
        return sjcl.bn.fromBits(bits)
