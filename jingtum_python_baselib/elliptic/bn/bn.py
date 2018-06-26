# Utils
import math
import re

zeros = [
'',
'0',
'00',
'000',
'0000',
'00000',
'000000',
'0000000',
'00000000',
'000000000',
'0000000000',
'00000000000',
'000000000000',
'0000000000000',
'00000000000000',
'000000000000000',
'0000000000000000',
'00000000000000000',
'000000000000000000',
'0000000000000000000',
'00000000000000000000',
'000000000000000000000',
'0000000000000000000000',
'00000000000000000000000',
'000000000000000000000000',
'0000000000000000000000000'
]


groupSizes = [
0, 0,
25, 16, 12, 11, 10, 9, 8,
8, 7, 7, 7, 7, 6, 6,
6, 6, 6, 6, 6, 5, 5,
5, 5, 5, 5, 5, 5, 5,
5, 5, 5, 5, 5, 5, 5
]


groupBases = [
0, 0,
33554432, 43046721, 16777216, 48828125, 60466176, 40353607, 16777216,
43046721, 10000000, 19487171, 35831808, 62748517, 7529536, 11390625,
16777216, 24137569, 34012224, 47045881, 64000000, 4084101, 5153632,
6436343, 7962624, 9765625, 11881376, 14348907, 17210368, 20511149,
24300000, 28629151, 33554432, 39135393, 45435424, 52521875, 60466176
]

def smallMulTo(self, num, out):
    out.negative = num.negative ^ self.negative
    len = (self.length + num.length) | 0
    out.length = len
    len = (len - 1) | 0

    # Peel one iteration (compiler can't do it, because of code complexity)
    a = self.words[0] | 0
    b = num.words[0] | 0
    r = a * b

    lo = r & 0x3ffffff

    carry = (r / 0x4000000) | 0
    out.words[0] = lo

    k = 1
    while k < len:
        # Sum all words with the same `i + j = k` and accumulate `ncarry`,
        # note that ncarry could be >= 0x3ffffff
        ncarry = carry >> 26
        rword = carry & 0x3ffffff
        maxJ = min(k, num.length - 1)
        j = max(0, k - self.length + 1)
        while j <= maxJ:
            i = (k - j) | 0
            a = self.words[i] | 0
            b = num.words[j] | 0
            r = a * b + rword
            ncarry += (r / 0x4000000) | 0
            rword = r & 0x3ffffff
            j += 1
        out.words[k] = rword | 0
        carry = ncarry | 0
        k += 1

    if (carry != 0):
        out.words[k] = carry | 0
    else:
        out.length-= 1

    return out.strip()

def comb10MulTo(self, num, out):
    return smallMulTo(self, num, out);

def jumboMulTo(self, num, out):
    fftm = FFTM()
    return fftm.mulp(self, num, out)

def bigMulTo(self, num, out):
    out.negative = num.negative ^ self.negative
    out.length = self.length + num.length

    carry = 0
    hncarry = 0
    k = 0
    while k < len(out) - 1:
        # Sum all words with the same `i + j = k` and accumulate `ncarry`,
        # note that ncarry could be >= 0x3ffffff
        ncarry = hncarry
        hncarry = 0
        rword = carry & 0x3ffffff
        maxJ = min(k, len(num) - 1)
        j = max(0, k - self.length + 1)
        while j <= maxJ:
            i = k - j
            a = self.words[i] | 0
            b = num.words[j] | 0
            r = a * b

            lo = r & 0x3ffffff
            ncarry = (ncarry + ((r / 0x4000000) | 0)) | 0
            lo = (lo + rword) | 0
            rword = lo & 0x3ffffff
            ncarry = (ncarry + (lo >> 26)) | 0

            hncarry += ncarry >> 26
            ncarry &= 0x3ffffff
            j += 1
    out.words[k] = rword
    carry = ncarry
    ncarry = hncarry
    k += 1

    if (carry != 0):
        out.words[k] = carry
    else:
        out.length-=1
    return out.strip()


# Cooley-Tukey algorithm for FFT
# slightly revisited to rely on looping instead of recursion
class FFTM:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def makeRBT(self, N):
        t = Array(N)
        l = BN._countBits(N) - 1
        i = 0
        while i < N:
            t[i] = self.revBin(i, l, N)
            i += 1

        return t

    # Returns binary-reversed representation of `x`
    def revBin(x, l, N):
        if (x == 0 or x == N - 1):
            return x

        rb = 0
        i = 0
        while i < l:
            rb |= (x & 1) << (l - i - 1)
            x >>= 1
            i += 1

        return rb

    # Performs "tweedling" phase, therefore 'emulating'
    # behaviour of the recursive algorithm
    def permute(rbt, rws, iws, rtws, itws, N):
        i = 0
        while i < N:
            rtws[i] = rws[rbt[i]]
            itws[i] = iws[rbt[i]]
            i += 1

    def transform(self, rws, iws, rtws, itws, N, rbt):
        self.permute(rbt, rws, iws, rtws, itws, N)

        s = 1
        while s < N:
            l = s << 1
            rtwdf = math.cos(2 * math.PI / l)
            itwdf = math.sin(2 * math.PI / l)

            p = 0
            while p < N:
                rtwdf_ = rtwdf
                itwdf_ = itwdf

                j = 0
                while j < s:
                    re = rtws[p + j]
                    ie = itws[p + j]

                    ro = rtws[p + j + s]
                    io = itws[p + j + s]

                    rx = rtwdf_ * ro - itwdf_ * io

                    io = rtwdf_ * io + itwdf_ * ro
                    ro = rx

                    rtws[p + j] = re + ro
                    itws[p + j] = ie + io

                    rtws[p + j + s] = re - ro
                    itws[p + j + s] = ie - io

                    # jshint maxdepth: False * /
                    if (j != l):
                        rx = rtwdf * rtwdf_ - itwdf * itwdf_

                        itwdf_ = rtwdf * itwdf_ + itwdf * rtwdf_
                        rtwdf_ = rx
                    j += 1
                p += l
            s <<= 1

    def guessLen13b(n, m):
        N = max(m, n) | 1
        odd = N & 1
        i = 0
        N = N / 2 | 0
        while N:
            i += 1
            N = N >> 1

        return 1 << i + 1 + odd

    def conjugate(rws, iws, N):
        if (N <= 1):
            return

        i = 0
        while i < N / 2:
            t = rws[i]

            rws[i] = rws[N - i - 1]
            rws[N - i - 1] = t

            t = iws[i]

            iws[i] = -iws[N - i - 1]
            iws[N - i - 1] = -t
            i += 1

    def normalize13b(ws, N):
        carry = 0
        i = 0
        while i < N / 2:
            w = round(ws[2 * i + 1] / N) * 0x2000 + \
                round(ws[2 * i] / N) + carry

            ws[i] = w & 0x3ffffff

            if (w < 0x4000000):
                carry = 0
            else:
                carry = w / 0x4000000 | 0
            i += 1

        return ws

    def convert13b(ws, len, rws, N):
        carry = 0
        i = 0
        while i < len:
            carry = carry + (ws[i] | 0)

            rws[2 * i] = carry & 0x1fff
            carry = carry >> 13
            rws[2 * i + 1] = carry & 0x1fff
            carry = carry >> 13
            i += 1

        # Pad with zeroes
        i = 2 * len
        while i < N:
            rws[i] = 0
            i += 1

        assert (carry == 0)
        assert ((carry & ~0x1fff) == 0)

    def stub(N):
        ph = Array(N)
        i = 0
        while i < N:
            ph[i] = 0
            i += 1
        return ph

    def mulp(self, x, y, out):
        N = 2 * self.guessLen13b(len(x), len(y))
        rbt = self.makeRBT(N)
        _ = self.stub(N)

        rws = Array(N)
        rwst = Array(N)
        iwst = Array(N)

        nrws = Array(N)
        nrwst = Array(N)
        niwst = Array(N)

        rmws = out.words
        rmws.length = N

        self.convert13b(x.words, x.length, rws, N)
        self.convert13b(y.words, y.length, nrws, N)

        self.transform(rws, _, rwst, iwst, N, rbt)
        self.transform(nrws, _, nrwst, niwst, N, rbt)

        i = 0
        while i < N:
            rx = rwst[i] * nrwst[i] - iwst[i] * niwst[i]
            iwst[i] = rwst[i] * niwst[i] + iwst[i] * nrwst[i]
            rwst[i] = rx
            i += 1

        self.conjugate(rwst, iwst, N)
        self.transform(rwst, iwst, rmws, _, N, rbt)
        self.conjugate(rmws, _, N)
        self.normalize13b(rmws, N)

        out.negative = x.negative ^ y.negative
        out.length = x.length + y.length
        return out.strip()

# BN
class BN:
    def BN(self, number, base, endian):
        if (BN.isBN(number)):
            return number

        self.negative = 0
        self.words = None
        self.length = 0

        # Reduction context
        self.red = None

        if (number != None):
            if (base == 'le' or base == 'be'):
                endian = base
                base = 10
            self._init(number or 0, base or 10, endian or 'be')

        BN.BN = BN
        BN.wordSize = 26
        """
        try {
        Buffer = require('buffer').Buffer
        } catch (e) {
        }
        """

    def isBN(num):
        if isinstance(num, BN):
            return True

        #can't translate into python
        #return num != None and typeof \
        #    num == 'object' and \
        #    num.constructor.wordSize == BN.wordSize and Array.isArray(num.words)

    def max(left, right):
        if (left.cmp(right) > 0):
            return left
        return right

    def min(left, right):
        if (left.cmp(right) < 0):
            return left
        return right

    def __init__(self, number, base, endian):
        if isinstance(number, number):
            return self._initNumber(number, base, endian)

        if isinstance(number, obj):
            return self._initArray(number, base, endian)

        if (base == 'hex'):
            base = 16
        assert (base == (base | 0) and base >= 2 and base <= 36)

        number = re.sub(r'\s +  ', '',number.toString())
        start = 0
        if (number[0] == '-'):
            start += 1

        if (base == 16):
            self._parseHex(number, start)
        else:
            self._parseBase(number, base, start)

        if (number[0] == '-'):
            self.negative = 1

        self.strip()

        if (endian != 'le'):
            return  self._initArray(self.toArray(), base, endian)

    def _initNumber(self, number, base, endian):
        if (number < 0):
            self.negative = 1
            number = -number
        if (number < 0x4000000):
            self.words =[number & 0x3ffffff]
            self.length = 1
        elif (number < 0x10000000000000):
            self.words =[
            number & 0x3ffffff,
            (number / 0x4000000) & 0x3ffffff
            ]
            self.length = 2
        else:
            assert (number < 0x20000000000000)  # 2 ^ 53 (unsafe)
            self.words =[
            number & 0x3ffffff,
            (number / 0x4000000) & 0x3ffffff,
            1
            ]
            self.length = 3

        if (endian != 'le'):
            return

        # Reverse the bytes
        self._initArray(self.toArray(), base, endian)

    def _initArray(self, number, base, endian):
        # Perhaps a Uint8Array
        assert isinstance(number.length, number)
        if (len(number) <= 0):
            self.words = [0]
            self.length = 1
            return self

        self.length = math.ceil(number.length / 3)
        self.words = Array(self.length)
        i = 0
        while i < self.length:
            self.words[i] = 0
            i += 1

        off = 0
        if (endian == 'be'):
            i = number.length - 1
            j = 0
            while i >= 0:
                w = number[i] | (number[i - 1] << 8) | (number[i - 2] << 16)
                self.words[j] |= (w << off) & 0x3ffffff
                self.words[j + 1] = (w >> (26 - off)) & 0x3ffffff
                off += 24
                if (off >= 26):
                    off -= 26
                    j += 1
                i -= 3

        elif (endian == 'le'):
            i = 0
            j = 0
            while i < number.length:
                w = number[i] | (number[i + 1] << 8) | (number[i + 2] << 16)
                self.words[j] |= (w << off) & 0x3ffffff
                self.words[j + 1] = (w >> (26 - off)) & 0x3ffffff
                off += 24
                if (off >= 26):
                    off -= 26
                    j += 1
                i += 3

        return self.strip()

    def parseHex(str, start, end):
        r = 0

        len = min(str.length, end)
        i = start
        while i < len:
            c = str.charCodeAt(i) - 48
            r <<= 4

            # 'a' - 'f'
            if (c >= 49 and c <= 54):
                r |= c - 49 + 0xa
            # 'A' - 'F'
            elif (c >= 17 and c <= 22):
                r |= c - 17 + 0xa
            # '0' - '9'
            else:
                r |= c & 0xf
            i += 1

        return r

    def _parseHex(self, number, start):
        # Create possibly bigger array to ensure that it fits the number
        self.length = math.ceil((number.length - start) / 6)

        self.words = Array(self.length)
        i = 0
        while i < self.length:
            self.words[i] = 0
            i += 1

        # Scan 24-bit chunks and add them to the number
        off = 0
        i = number.length - 6
        j = 0
        while i >= start:
            w = parseHex(number, i, i + 6)
            self.words[j] |= (w << off) & 0x3ffffff
            # NOTE: `0x3fffff` is intentional here, 26bits max shift + 24bit hex limb
            self.words[j + 1] |= w >> (26 - off) & 0x3fffff
            off += 24
            if (off >= 26):
                off -= 26
                j += 1
            i -= 6

        if (i + 6 != start):
            w = parseHex(number, start, i + 6)
            self.words[j] |= (w << off) & 0x3ffffff
            self.words[j + 1] |= w >> (26 - off) & 0x3fffff
        self.strip()

    def parseBase(str, start, end, mul):
        r = 0
        len = min(str.length, end)
        i = start
        while i < len:
            c = str.charCodeAt(i) - 48
            r *= mul

            # 'a'
            if (c >= 49):
                r += c - 49 + 0xa
            # 'A'
            elif (c >= 17):
                r += c - 17 + 0xa
            # '0' - '9'
            else:
                r += c
            i += 1
        return r

    def _parseBase(self, number, base, start):
        # Initialize as zero
        self.words = [0]
        self.length = 1

        # Find length of limb in base
        limbLen = 0
        limbPow = 1
        while limbPow <= 0x3ffffff:
            limbLen += 1
            limbPow *= base
        limbLen -= 1
        limbPow = (limbPow / base) | 0

        total = number.length - start
        mod = total % limbLen
        end = min(total, total - mod) + start

        word = 0
        i = start
        while i < end:
            word = parseBase(number, i, i + limbLen, base)

            self.imuln(limbPow)
            if (self.words[0] + word < 0x4000000):
                self.words[0] += word
            else:
                self._iaddn(word)
            i += limbLen


        if (mod != 0):
            pow = 1
            word = parseBase(number, i, number.length, base)

            i = 0
            while i < mod:
                pow *= base
                i += 1

            self.imuln(pow)
            if (self.words[0] + word < 0x4000000):
                self.words[0] += word
            else:
                self._iaddn(word)

    def copy(self, dest):
        dest.words = Array(self.length)

        i = 0
        while i < self.length:
            dest.words[i] = self.words[i]
            i += 1
        dest.length = self.length
        dest.negative = self.negative
        dest.red = self.red

    def clone(self):
        r = BN(None)
        self.copy(r)
        return r

    def _expand(self, size):
        while (self.length < size):
            self.length += 1
            self.words[self.length] = 0

        return self

    # Remove leading `0` from `self`
    def strip(self):
        while (self.length > 1 and self.words[self.length - 1] == 0):
            self.length -= 1
        return self._normSign()

    def _normSign(self):
        # -0 = 0
        if (self.length == 1 and self.words[0] == 0):
            self.negative = 0
        return self

    def inspect(self):
        if self.red:
            return '<BN-R: ' + hex(self).replace('0x', '') + '>'
        else:
            return '<BN: ' + hex(self).replace('0x', '') + '>'


    def toString(self, base, padding):
        base = base or 10
        padding = padding | 0 or 1

        if (base == 16 or base == 'hex'):
            out = ''
            off = 0

            carry = 0
            i = 0
            while i < self.length:
                w = self.words[i]
                word = (((w << off) | carry) & 0xffffff).toString(16)
                carry = (w >> (24 - off)) & 0xffffff
                if (carry != 0 or i != self.length - 1):
                    out = zeros[6 - word.length] + word + out
                else:
                    out = word + out
                off += 2
                if (off >= 26):
                    off -= 26
                    i -= 1
                i += 1

            if (carry != 0):
                out = carry.toString(16) + out
            while (out.length % padding != 0):
                out = '0' + out
            if (self.negative != 0):
                out = '-' + out
            return out

        if (base == (base | 0) and base >= 2 and base <= 36):
            # groupSize = math.floor(BN.wordSize * math.LN2 / math.log(base))
            groupSize = groupSizes[base]
            # groupBase = math.pow(base, groupSize)

            groupBase = groupBases[base]
            out = ''

            c = self.clone()
            c.negative = 0
            while (not c.isZero()):
                r = c.modn(groupBase).toString(base)
                c = c.idivn(groupBase)

                if (not c.isZero()):
                    out = zeros[groupSize - r.length] + r + out
                else:
                    out = r + out

            if (self.isZero()):
                out = '0' + out

            while (out.length % padding != 0):
                out = '0' + out

            if (self.negative != 0):
                out = '-' + out
            return out

        assert False, 'Base should be between 2 and 36'

    def toNumber(self):
        ret = self.words[0]
        if (self.length == 2):
            ret += self.words[1] * 0x4000000
        elif (self.length == 3 and self.words[2] == 0x01):
            # NOTE: at self stage it is known that the top bit is set
            ret += 0x10000000000000 + (self.words[1] * 0x4000000)
        elif (self.length > 2):
            assert False, 'Number can only safely store up to 53 bits'
        if self.negative != 0:
            return -ret
        else:
            return ret

    def toJSON(self):
        return self.toString(16)

    def toBuffer(self, endian, length):
        assert Buffer
        return self.toArrayLike(Buffer, endian, length)

    def toArray(self, endian, length):
        return self.toArrayLike(Array, endian, length)

    def toArrayLike(self, ArrayType, endian, length):
        byteLength = self.byteLength()

        reqLength = length or max(1, byteLength)
        assert byteLength <= reqLength, 'byte array longer than desired length'
        assert reqLength > 0, 'Requested array length <= 0'

        self.strip()
        littleEndian = endian == 'le'
        res = ArrayType(reqLength)

        q = self.clone()
        if (not littleEndian):
            # Assume big-endian
            i = 0
            while i < reqLength - byteLength:
                res[i] = 0
                i += 1

            i = 0
            while not q.isZero():
                b = q.andln(0xff)
                q.iushrn(8)

                res[reqLength - i - 1] = b
                i += 1
        else:
            i = 0
            while not q.isZero():
                b = q.andln(0xff)
                q.iushrn(8)

                res[i] = b
                i += 1

            while i < reqLength:
                res[i] = 0
                i += 1

        return res

    def _countBits(w):
        t = w
        r = 0
        if (t >= 0x1000):
            r += 13
            t >>= 13
        if (t >= 0x40):
            r += 7
            t >>= 7
        if (t >= 0x8):
            r += 4
            t >>= 4
        if (t >= 0x02):
            r += 2
            t >>= 2
        return r + t

    def _zeroBits(w):
        # Short-cut
        if (w == 0):
            return 26

        t = w
        r = 0
        if ((t & 0x1fff) == 0):
            r += 13
            t >>= 13
        if ((t & 0x7f) == 0):
            r += 7
            t >>= 7
        if ((t & 0xf) == 0):
            r += 4
            t >>= 4
        if ((t & 0x3) == 0):
            r += 2
            t >>= 2
        if ((t & 0x1) == 0):
            r += 1
        return r

    # Return number of used bits in a BN
    def bitLength(self):
        w = self.words[self.length - 1]
        hi = self._countBits(w)
        return (self.length - 1) * 26 + hi

    def toBitArray(num):
        w = Array(num.bitLength())

        bit = 0
        while bit < w.length:
            off = (bit / 26) | 0
            wbit = bit % 26

            w[bit] = (num.words[off] & (1 << wbit)) >> wbit
            bit += 1

        return w

# Number of trailing zero bits
    def zeroBits(self):
        if (self.isZero()):
            return 0

        r = 0
        i = 0
        while i < self.length:
            b = self._zeroBits(self.words[i])
            r += b
            if (b != 26):
                break
            i += 1
        return r

    def byteLength(self):
        return math.ceil(self.bitLength() / 8)

    def toTwos(self, width):
        if (self.negative != 0):
            return self.abs().inotn(width).iaddn(1)
        return self.clone()

    def fromTwos(self, width):
        if (self.testn(width - 1)):
            return self.notn(width).iaddn(1).ineg()
        return self.clone()

    def isNeg(self):
        return self.negative != 0

    # Return negative clone of `self`
    def neg(self):
        return self.clone().ineg()

    def ineg(self):
        if not self.isZero():
            self.negative ^= 1
        return self

    # Or `num` with `self` in-place
    def iuor(self, num):
        while (self.length < num.length):
            self.length += 1
            self.words[self.length] = 0

        i = 0
        while i < num.length:
            self.words[i] = self.words[i] | num.words[i]
            i += 1

        return self.strip()

    def ior(self, num):
        assert ((self.negative | num.negative) == 0)
        return self.iuor(num)

    # Or `num` with `self`   or-->bnor in python
    def bnor(self,num):
        if (self.length > num.length):
            return self.clone().ior(num)
        return num.clone().ior(self)

    def uor(self, num):
        if (self.length > num.length):
            return self.clone().iuor(num)
        return num.clone().iuor(self)

    # And `num` with `self` in-place
    def iuand(self, num):
        # b = min-length(num, self)
        if (self.length > num.length):
            b = num
        else:
            b = self

        i = 0
        while i < b.length:
            self.words[i] = self.words[i] & num.words[i]
            i += 1

        self.length = b.length

        return self.strip()

    def iand(self, num):
        assert ((self.negative | num.negative) == 0)
        return self.iuand(num)

    # And `num` with `self`   and -->bnand
    def bnand(self, num):
        if (self.length > num.length):
            return self.clone().iand(num)
        return num.clone().iand(self)

    def uand(self, num):
        if (self.length > num.length):
            return self.clone().iuand(num)
        return num.clone().iuand(self)

# Xor `num` with `self` in-place
    def iuxor(self, num):
        # a.length > b.length
        if (self.length > num.length):
            a = self
            b = num
        else:
            a = num
            b = self

        i = 0
        while i < b.length:
            self.words[i] = a.words[i] ^ b.words[i]
            i += 1

        if (self != a):
            while i < a.length:
                self.words[i] = a.words[i]
                i += 1

        self.length = a.length
        return self.strip()

    def ixor(self, num):
        assert ((self.negative | num.negative) == 0)
        return self.iuxor(num)

    # Xor `num` with `self`
    def xor(self, num):
        if (self.length > num.length):
            return self.clone().ixor(num)
        return num.clone().ixor(self)

    def uxor(num):
        if (self.length > num.length):
            return self.clone().iuxor(num)
        return num.clone().iuxor(self)

    # Not ``self`` with ``width`` bitwidth
    def inotn(self, width):
        assert (isinstance(width,number) and width >= 0)
        bytesNeeded = math.ceil(width / 26) | 0

        bitsLeft = width % 26

        # Extend the buffer with leading zeroes
        self._expand(bytesNeeded)

        if (bitsLeft > 0):
            bytesNeeded -= 1

        # Handle complete words
        i = 0
        while i < bytesNeeded:
            self.words[i] = ~self.words[i] & 0x3ffffff
            i += 1

        # Handle the residue
        if (bitsLeft > 0):
            self.words[i] = ~self.words[i] & (0x3ffffff >> (26 - bitsLeft))

        # And remove leading zeroes
        return self.strip()

    def notn(self, width):
        return self.clone().inotn(width)

    # Set `bit` of `self`
    def setn(self, bit, val):
        assert (isinstance(bit,number) and bit >= 0)
        off = (bit / 26) | 0

        wbit = bit % 26

        self._expand(off + 1)

        if (val):
            self.words[off] = self.words[off] | (1 << wbit)
        else:
            self.words[off] = self.words[off] & ~(1 << wbit)

        return self.strip()

    # Add `num` to `self` in-place
    def iadd(self, num):
        # negative + positive
        if (self.negative != 0 and num.negative == 0):
            self.negative = 0
            r = self.isub(num)
            self.negative ^= 1
            return self._normSign()
        # positive + negative
        elif (self.negative == 0 and num.negative != 0):
            num.negative = 0
            r = self.isub(num)
            num.negative = 1
            return r._normSign()

        # a.length > b.length
        if (self.length > num.length):
            a = self
            b = num
        else:
            a = num
            b = self

        carry = 0
        i = 0
        while i < b.length:
            r = (a.words[i] | 0) + (b.words[i] | 0) + carry
            self.words[i] = r & 0x3ffffff
            carry = r >> 26
            i += 1
        while carry != 0 and i < a.length:
            r = (a.words[i] | 0) + carry
            self.words[i] = r & 0x3ffffff
            carry = r >> 26
            i += 1

        self.length = a.length
        if (carry != 0):
            self.words[self.length] = carry
            self.length += 1
            # Copy the rest of the words
        elif (a != self):
            while i < a.length:
                self.words[i] = a.words[i]
                i += 1

        return self

    # Add `num` to `self`
    def add(self, num):
        if (num.negative != 0 and self.negative == 0):
            num.negative = 0
            res = self.sub(num)
            num.negative ^= 1
            return res
        elif (num.negative == 0 and self.negative != 0):
            self.negative = 0
            res = num.sub(self)
            self.negative = 1
            return res

        if (self.length > num.length):
            return self.clone().iadd(num)

        return num.clone().iadd(self)

    # Subtract `num` from `self` in-place
    def isub(self, num):
        # self - (-num) = self + num
        if (num.negative != 0):
            num.negative = 0
            r = self.iadd(num)
            num.negative = 1
            return r._normSign()
        # -self - num = -(self + num)
        elif (self.negative != 0):
            self.negative = 0
            self.iadd(num)
            self.negative = 1
            return self._normSign()

        # At self point both numbers are positive
        cmp = self.cmp(num)

        # Optimization - zeroify
        if (cmp == 0):
            self.negative = 0
            self.length = 1
            self.words[0] = 0
            return self

        # a > b
        if (cmp > 0):
            a = self
            b = num
        else:
            a = num
            b = self

        carry = 0
        i = 0
        while i < b.length:
            r = (a.words[i] | 0) - (b.words[i] | 0) + carry
            carry = r >> 26
            self.words[i] = r & 0x3ffffff
            i += 1
        while carry != 0 and i < a.length:
            r = (a.words[i] | 0) + carry
            carry = r >> 26
            self.words[i] = r & 0x3ffffff
            i += 1

        # Copy rest of the words
        if (carry == 0 and i < a.length and a != self):
            while i < a.length:
                self.words[i] = a.words[i]
                i += 1

        self.length = max(self.length, i)

        if (a != self):
            self.negative = 1

        return self.strip()

    # Subtract `num` from `self`
    def sub(self, num):
        return self.clone().isub(num)

    def mulTo(self, num, out):
        len = self.length + num.length
        if (self.length == 10 and num.length == 10):
            res = comb10MulTo(self, num, out)
        elif (len < 63):
            res = smallMulTo(self, num, out)
        elif (len < 1024):
            res = bigMulTo(self, num, out)
        else:
            res = jumboMulTo(self, num, out)

        return res


    # Multiply `self` by `num`
    def mul(self, num):
        out = BN(None)
        out.words = Array(self.length + num.length)
        return self.mulTo(num, out)

# Multiply employing FFT
    def mulf(self, num):
        out = BN(None)
        out.words = Array(self.length + num.length)
        return jumboMulTo(self, num, out)

    # In-place Multiplication
    def imul(self, num):
        return self.clone().mulTo(num, self)

    def imuln(self, num):
        assert isinstance(num, number)
        assert (num < 0x4000000)

        # Carry
        carry = 0
        i = 0
        while i < self.length:
            w = (self.words[i] | 0) * num
            lo = (w & 0x3ffffff) + (carry & 0x3ffffff)
            carry >>= 26
            carry += (w / 0x4000000) | 0
            # NOTE: lo is 27bit maximum
            carry += lo >> 26
            self.words[i] = lo & 0x3ffffff
            i += 1

        if (carry != 0):
            self.words[i] = carry
            self.length+= 1

        return self

    def muln(self, num):
        return self.clone().imuln(num)

    # `self` * `self`
    def sqr(self):
        return self.mul(self)

    # `self` * `self` in-place
    def isqr(self):
        return self.imul(self.clone())

    # math.pow(`self`, `num`)
    def pow(num):
        w = toBitArray(num)
        if (w.length == 0):
            return BN(1)

        # Skip leading zeroes
        res = self
        i = 0
        while i < w.length:
            if (w[i] != 0):
                break
            i += 1
            res = res.sqr()

        i += 1
        if (i < w.length):
            q = res.sqr()
            while i < w.length:
                if (w[i] == 0):
                    continue
                res = res.mul(q)
                i += 1
                q = q.sqr()
        return res

    # Shift-left in-place
    def iushln(self, bits):
        assert isinstance(bits, number) and bits >= 0
        r = bits % 26
        s = (bits - r) / 26
        carryMask = (0x3ffffff >> (26 - r)) << (26 - r)

        if (r != 0):
            carry = 0

            i = 0
            while i < self.length:
                newCarry = self.words[i] & carryMask
                c = ((self.words[i] | 0) - newCarry) << r
                self.words[i] = c | carry
                carry = newCarry >> (26 - r)
                i += 1

            if (carry):
                self.words[i] = carry
                self.length+= 1

        if (s != 0):
            i = self.length - 1
            while i >= 0:
                self.words[i + s] = self.words[i]
                i -= 1

            i = 0
            while i < s:
                self.words[i] = 0
                i += 1

            self.length += s
        return self.strip()

    def ishln(self, bits):
        # TODO(indutny): implement me
        assert (self.negative == 0)
        return self.iushln(bits)

    # Shift-right in-place
    # NOTE: `hint` is a lowest bit before trailing zeroes
    # NOTE: if `extended` is present - it will be filled with destroyed bits
    def iushrn(self, bits, hint, extended):
        assert isinstance(bits, number) and bits >= 0
        if (hint):
            h = (hint - (hint % 26)) / 26
        else:
            h = 0

        r = bits % 26
        s = min((bits - r) / 26, self.length)
        mask = 0x3ffffff ^ ((0x3ffffff >> r) << r)
        maskedWords = extended

        h -= s
        h = max(0, h)

        # Extended mode, copy masked part
        if (maskedWords):
            i = 0
            while i < s:
                maskedWords.words[i] = self.words[i]
                i += 1
            maskedWords.length = s

        if (s == 0):
            None
            # No-op, we should not move anything at all
        elif (self.length > s):
            self.length -= s
            i = 0
            while i < self.length:
                self.words[i] = self.words[i + s]
                i += 1
        else:
            self.words[0] = 0
            self.length = 1

        carry = 0
        i = self.length - 1
        while i >= 0 and (carry != 0 or i >= h):
            word = self.words[i] | 0
            self.words[i] = (carry << (26 - r)) | (word >> r)
            carry = word & mask
            i -= 1

        # Push carried bits as a mask
        if (maskedWords and carry != 0):
            maskedWords.length += 1
            maskedWords.words[maskedWords.length] = carry

        if (self.length == 0):
            self.words[0] = 0
            self.length = 1

        return self.strip()

    def ishrn(self, bits, hint, extended):
        # TODO(indutny): implement me
        assert (self.negative == 0)
        return self.iushrn(bits, hint, extended)

    # Shift-left
    def shln(self, bits):
        return self.clone().ishln(bits)

    def ushln(self, bits):
        return self.clone().iushln(bits)

    # Shift-right
    def shrn(self, bits):
        return self.clone().ishrn(bits)

    def ushrn(self, bits):
        return self.clone().iushrn(bits)

    # Test if n bit is set
    def testn(self, bit):
        assert isinstance(bit, number) and bit >= 0
        r = bit % 26
        s = (bit - r) / 26
        q = 1 << r

        # Fast case: bit is much higher than all existing words
        if (self.length <= s):
            return False

        # Check bit and return
        w = self.words[s]

        return w & q

    # Return only lowers bits of number (in-place)
    def imaskn(self, bits):
        assert isinstance(bits, number) and bits >= 0
        r = bits % 26
        s = (bits - r) / 26
        assert self.negative == 0, 'imaskn works only with positive numbers'

        if (self.length <= s):
            return self

        if (r != 0):
            s += 1
        self.length = min(s, self.length)

        if (r != 0):
            mask = 0x3ffffff ^ ((0x3ffffff >> r) << r)
            self.words[self.length - 1] &= mask

        return self.strip()

    # Return only lowers bits of number
    def maskn(self, bits):
        return self.clone().imaskn(bits)

    # Add plain number `num` to `self`
    def iaddn(self, num):
        assert isinstance(num, number)
        assert (num < 0x4000000)
        if (num < 0):
            return self.isubn(-num)

        # Possible sign change
        if (self.negative != 0):
            if (self.length == 1 and (self.words[0] | 0) < num):
                self.words[0] = num - (self.words[0] | 0)
                self.negative = 0
                return self

            self.negative = 0
            self.isubn(num)
            self.negative = 1
            return self

        # Add without checks
        return self._iaddn(num)

    def _iaddn(self, num):
        self.words[0] += num

        # Carry
        i = 0
        while i < self.length and self.words[i] >= 0x4000000:
            self.words[i] -= 0x4000000
            if (i == self.length - 1):
                self.words[i + 1] = 1
            else:
                self.words[i + 1]+= 1
            i += 1
        self.length = max(self.length, i + 1)

        return self

    # Subtract plain number `num` from `self`
    def isubn(self, num):
        assert isinstance(num, number)
        assert (num < 0x4000000)
        if (num < 0):
            return self.iaddn(-num)

        if (self.negative != 0):
            self.negative = 0
            self.iaddn(num)
            self.negative = 1
            return self

        self.words[0] -= num

        if (self.length == 1 and self.words[0] < 0):
            self.words[0] = -self.words[0]
            self.negative = 1
        else:
            # Carry
            i = 0
            while i < self.length and self.words[i] < 0:
                self.words[i] += 0x4000000
                self.words[i + 1] -= 1
                i += 1

        return self.strip()

    def addn(self, num):
        return self.clone().iaddn(num)

    def subn(self, num):
        return self.clone().isubn(num)

    def iabs(self):
        self.negative = 0
        return self

    def abs(self):
        return self.clone().iabs()

    def _ishlnsubmul(self, num, mul, shift):
        len = num.length + shift
        self._expand(len)

        carry = 0
        i = 0
        while i < num.length:
            w = (self.words[i + shift] | 0) + carry
            right = (num.words[i] | 0) * mul
            w -= right & 0x3ffffff
            carry = (w >> 26) - ((right / 0x4000000) | 0)
            self.words[i + shift] = w & 0x3ffffff
            i += 1
        while i < self.length - shift:
            w = (self.words[i + shift] | 0) + carry
            carry = w >> 26
            self.words[i + shift] = w & 0x3ffffff
            i += 1

        if (carry == 0):
            return self.strip()

        # Subtraction overflow
        assert (carry == -1)
        carry = 0
        i = 0
        while i < self.length:
            w = -(self.words[i] | 0) + carry
            carry = w >> 26
            self.words[i] = w & 0x3ffffff
            i += 1
        self.negative = 1

        return self.strip()

    def _wordDiv(self, num, mode):
        shift = self.length - num.length
        a = self.clone()
        b = num

        # Normalize
        bhi = b.words[b.length - 1] | 0
        bhiBits = self._countBits(bhi)
        shift = 26 - bhiBits
        if (shift != 0):
            b = b.ushln(shift)
            a.iushln(shift)
            bhi = b.words[b.length - 1] | 0

        # Initialize quotient
        m = a.length - b.length
        if (mode != 'mod'):
            q = BN(None)
            q.length = m + 1
            q.words = Array(q.length)
            i = 0
            while i < q.length:
                q.words[i] = 0
                i += 1

        diff = a.clone()._ishlnsubmul(b, 1, m)
        if (diff.negative == 0):
            a = diff
            if (q):
                q.words[m] = 1

        j = m - 1
        while j >= 0:
            qj = (a.words[b.length + j] | 0) * 0x4000000 + \
            (a.words[b.length + j - 1] | 0)

            # NOTE: (qj / bhi) is (0x3ffffff * 0x4000000 + 0x3ffffff) / 0x2000000 max
            # (0x7ffffff)
            qj = min((qj / bhi) | 0, 0x3ffffff)

            a._ishlnsubmul(b, qj, j)
            while (a.negative != 0):
                qj -= 1
                a.negative = 0
                a._ishlnsubmul(b, 1, j)
                if (not a.isZero()):
                    a.negative ^= 1
            if (q):
                q.words[j] = qj
            j -= 1
        if (q):
            q.strip()
        a.strip()

        # Denormalize
        if (mode != 'div' and shift != 0):
            a.iushrn(shift)

        return {
            'div': q or None,
            'mod': a
        }

    # NOTE: 1) `mode` can be set to `mod` to request mod only,
    #       to `div` to request div only, or be absent to
    #       request both div & mod
    #       2) `positive` is True if unsigned mod is requested
    def divmod(self, num, mode, positive):
        assert (not num.isZero())

        if (self.isZero()):
            return {
                'div': BN(0),
                'mod': BN(0)
            }

        if (self.negative != 0 and num.negative == 0):
            res = self.neg().divmod(num, mode)

            if (mode != 'mod'):
                div = res.div.neg()

            if (mode != 'div'):
                mod = res.mod.neg()
                if (positive and mod.negative != 0):
                    mod.iadd(num)

            return {
                'div': div,
                'mod': mod
            }

        if (self.negative == 0 and num.negative != 0):
            res = self.divmod(num.neg(), mode)

            if (mode != 'mod'):
                div = res.div.neg()

            return {
                'div': div,
                'mod': res.mod
            }

        if ((self.negative & num.negative) != 0):
            res = self.neg().divmod(num.neg(), mode)

            if (mode != 'div'):
                mod = res.mod.neg()
                if (positive and mod.negative != 0):
                    mod.isub(num)

            return {
                'div': res.div,
                'mod': mod
            }

        # Both numbers are positive at self point

        # Strip both numbers to approximate shift value
        if (num.length > self.length or self.cmp(num) < 0):
            return {
                div: BN(0),
                mod: self
            }

        # Very short reduction
        if (num.length == 1):
            if (mode == 'div'):
                return {
                    div: self.divn(num.words[0]),
                    mod: None
                }

            if (mode == 'mod'):
                return {
                    div: None,
                    mod: BN(self.modn(num.words[0]))
                }

            return {
                div: self.divn(num.words[0]),
                mod: BN(self.modn(num.words[0]))
            }

        return self._wordDiv(num, mode)

    # Find `self` / `num`
    def div(self, num):
        return self.divmod(num, 'div', False).div

    # Find `self` % `num`
    def mod(self, num):
        return self.divmod(num, 'mod', False).mod

    def umod(self, num):
        return self.divmod(num, 'mod', True).mod

    # Find Round(`self` / `num`)
    def divRound(self, num):
        dm = self.divmod(num)

        # Fast case - exact division
        if (dm.mod.isZero()):
            return dm.div

        if dm.div.negative != 0:
            mod =  dm.mod.isub(num)
        else:
            mod = dm.mod

        half = num.ushrn(1)
        r2 = num.andln(1)
        cmp = mod.cmp(half)

        # Round down
        if (cmp < 0 or r2 == 1 and cmp == 0):
            return dm.div

        # Round up
        if dm.div.negative != 0:
            return dm.div.isubn(1)
        else:
            return dm.div.iaddn(1)

    def modn(self, num):
        assert (num <= 0x3ffffff)
        p = (1 << 26) % num

        acc = 0
        i = self.length - 1
        while i >= 0:
            acc = (p * acc + (self.words[i] | 0)) % num
            i -= 1

        return acc

    # In-place division by number
    def idivn(self, num):
        assert (num <= 0x3ffffff)
        carry = 0
        i = self.length - 1
        while i >= 0:
            w = (self.words[i] | 0) + carry * 0x4000000
            self.words[i] = (w / num) | 0
            carry = w % num
            i -= 1

        return self.strip()

    def divn(self, num):
        return self.clone().idivn(num)

    def egcd(self, p):
        assert (p.negative == 0)
        assert (not p.isZero())

        x = self
        y = p.clone()

        if (x.negative != 0):
            x = x.umod(p)
        else:
            x = x.clone()

        # A * x + B * y = x
        A = BN(1)
        B = BN(0)

        # C * x + D * y = y
        C = BN(0)
        D = BN(1)

        g = 0

        while (x.isEven() and y.isEven()):
            x.iushrn(1)
            y.iushrn(1)
            g +=1

        yp = y.clone()
        xp = x.clone()

        while (not x.isZero()):
            i = 0
            im = 1
            while (x.words[0] & im) == 0 and i < 26:
                if (i > 0):
                    x.iushrn(i)
                    i = i-1
                    while i > 0:
                        if (A.isOdd() or B.isOdd()):
                            A.iadd(yp)
                            B.isub(xp)

                        A.iushrn(1)
                        B.iushrn(1)
                        i -= 1
                i += 1
                im<<= 1

            j = 0
            jm = 1
            while (y.words[0] & jm) == 0 and j < 26:
                if (j > 0):
                    y.iushrn(j)
                    j = j-1
                    while j> 0:
                        if (C.isOdd() or D.isOdd()):
                            C.iadd(yp)
                            D.isub(xp)

                        C.iushrn(1)
                        D.iushrn(1)
                        j = j-1

                j += 1
                jm <<= 1

            if (x.cmp(y) >= 0):
                x.isub(y)
                A.isub(C)
                B.isub(D)
            else:
                y.isub(x)
                C.isub(A)
                D.isub(B)

        return {
            a: C,
            b: D,
            gcd: y.iushln(g)
        }

    # self is reduced incarnation of the binary EEA
    # above, designated to invert members of the
    # _prime_ fields F(p) at a maximal speed
    def _invmp(self, p):
        assert (p.negative == 0)
        assert (not p.isZero())

        a = self
        b = p.clone()

        if (a.negative != 0):
            a = a.umod(p)
        else:
            a = a.clone()

        x1 = BN(1)
        x2 = BN(0)

        delta = b.clone()

        while (a.cmpn(1) > 0 and b.cmpn(1) > 0):
            i = 0
            im = 1
            while (a.words[0] & im) == 0 and i < 26:
                if (i > 0):
                    a.iushrn(i)
                    i -= 1
                    while (i> 0):
                        if (x1.isOdd()):
                            x1.iadd(delta)
                        x1.iushrn(1)
                        i -= 1
                i += 1
                im <<= 1

            j = 0
            jm = 1
            while (b.words[0] & jm) == 0 and j < 26:
                if (j > 0):
                    b.iushrn(j)
                    j -= 1
                    while j > 0:
                        if (x2.isOdd()):
                            x2.iadd(delta)
                        x2.iushrn(1)
                        j -= 1
                j += 1
                jm <<= 1

            if (a.cmp(b) >= 0):
                a.isub(b)
                x1.isub(x2)
            else:
                b.isub(a)
                x2.isub(x1)

        if (a.cmpn(1) == 0):
            res = x1
        else:
            res = x2

        if (res.cmpn(0) < 0):
            res.iadd(p)

        return res

    def gcd(self, num):
        if (self.isZero()):
            return num.abs()
        if (num.isZero()):
            return self.abs()

        a = self.clone()
        b = num.clone()
        a.negative = 0
        b.negative = 0

        # Remove common factor of two
        shift = 0
        while a.isEven() and b.isEven():
            a.iushrn(1)
            b.iushrn(1)
            shift += 1

        while True:
            while (a.isEven()):
                a.iushrn(1)
            while (b.isEven()):
                b.iushrn(1)

            r = a.cmp(b)
            if (r < 0):
                # Swap `a` and `b` to make `a` always bigger than `b`
                t = a
                a = b
                b = t
            elif (r == 0 or b.cmpn(1) == 0):
                break
            a.isub(b)

        return b.iushln(shift)

    # Invert number in the field F(num)
    def invm(self, num):
        return self.egcd(num).a.umod(num)

    def isEven(self):
        return (self.words[0] & 1) == 0

    def isOdd(self):
        return (self.words[0] & 1) == 1

    # And first word and num
    def andln(self, num):
        return self.words[0] & num

    # Increment at the bit position in-line
    def bincn(self, bit):
        assert isinstance(bit, number)
        r = bit % 26
        s = (bit - r) / 26
        q = 1 << r

        # Fast case: bit is much higher than all existing words
        if (self.length <= s):
            self._expand(s + 1)
            self.words[s] |= q
            return self

        # Add bit and propagate, if needed
        carry = q
        i = s
        while carry != 0 and i < self.length :
            w = self.words[i] | 0
            w += carry
            carry = w >> 26
            w &= 0x3ffffff
            self.words[i] = w
            i += 1
        if (carry != 0):
            self.words[i] = carry
            self.length += 1
        return self

    def isZero(self):
        return self.length == 1 and self.words[0] == 0

    def cmpn(self, num):
        negative = num < 0

        if (self.negative != 0 and not negative):
            return -1
        if (self.negative == 0 and negative):
            return 1

        self.strip()

        if (self.length > 1):
            res = 1
        else:
            if (negative):
                num = -num

            assert num <= 0x3ffffff, 'Number is too big'

            w = self.words[0] | 0
            if w == num:
                res = 0
            elif  w < num:
                res = -1
            else:
                res = 1
        if (self.negative != 0):
            return -res | 0
        return res

    # Compare two numbers and return:
    # 1 - if `self` > `num`
    # 0 - if `self` == `num`
    # -1 - if `self` < `num`
    def cmp(self, num):
        if (self.negative != 0 and num.negative == 0):
            return -1
        if (self.negative == 0 and num.negative != 0):
            return 1

        res = self.ucmp(num)
        if (self.negative != 0):
            return -res | 0
        return res

    # Unsigned comparison
    def ucmp(self, num):
        # At self point both numbers have the same sign
        if (self.length > num.length):
            return 1
        if (self.length < num.length):
            return -1

        res = 0
        i = self.length - 1
        while i >= 0:
            a = self.words[i] | 0
            b = num.words[i] | 0

            if (a == b):
                continue
            if (a < b):
                res = -1
            elif (a > b):
                res = 1
            break
            i -= 1
        return res

    def gtn(self, num):
        return self.cmpn(num) == 1

    def gt(self, num):
        return self.cmp(num) == 1

    def gten(self, num):
        return self.cmpn(num) >= 0

    def gte(self, num):
        return self.cmp(num) >= 0

    def ltn(num):
        return self.cmpn(num) == -1

    def lt(self, num):
        return self.cmp(num) == -1

    def lten(self, num):
        return self.cmpn(num) <= 0

    def lte(self, num):
        return self.cmp(num) <= 0

    def eqn(self, num):
        return self.cmpn(num) == 0

    def eq(self, num):
        return self.cmp(num) == 0

    # A reduce context, could be using montgomery or something better, depending
    # on the `m` itself.
    def red(num):
        return Red(num)

    def toRed(self, ctx):
        assert not self.red, 'Already a number in reduction context'
        assert self.negative == 0, 'red works only with positives'
        return ctx.convertTo(self)._forceRed(ctx)

    def fromRed(self):
        assert self.red, 'fromRed works only with numbers in reduction context'
        return self.red.convertFrom(self)

    def _forceRed(self, ctx):
        self.red = ctx
        return self

    def forceRed(self, ctx):
        assert not self.red, 'Already a number in reduction context'
        return self._forceRed(ctx)

    def redAdd(self, num):
        assert self.red, 'redAdd works only with red numbers'
        return self.red.add(self, num)

    def redIAdd(self, num):
        assert self.red, 'redIAdd works only with red numbers'
        return self.red.iadd(self, num)

    def redSub(self, num):
        assert self.red, 'redSub works only with red numbers'
        return self.red.sub(self, num)

    def redISub(self, num):
        assert self.red, 'redISub works only with red numbers'
        return self.red.isub(self, num)

    def redShl(self, num):
        assert self.red, 'redShl works only with red numbers'
        return self.red.shl(self, num)

    def redMul(self, num):
        assert self.red, 'redMul works only with red numbers'
        self.red._verify2(self, num)
        return self.red.mul(self, num)

    def redIMul(self, num):
        assert self.red, 'redMul works only with red numbers'
        self.red._verify2(self, num)
        return self.red.imul(self, num)

    def redSqr(self):
        assert self.red, 'redSqr works only with red numbers'
        self.red._verify1(self)
        return self.red.sqr(self)

    def redISqr(self):
        assert self.red, 'redISqr works only with red numbers'
        self.red._verify1(self)
        return self.red.isqr(self)

    # Square root over p
    def redSqrt(self):
        assert self.red, 'redSqrt works only with red numbers'
        self.red._verify1(self)
        return self.red.sqrt(self)

    def redInvm(self):
        assert self.red, 'redInvm works only with red numbers'
        self.red._verify1(self)
        return self.red.invm(self)

    # Return negative clone of `self` % `red modulo`
    def redNeg(self):
        assert self.red, 'redNeg works only with red numbers'
        self.red._verify1(self)
        return self.red.neg(self)

    def redPow(self, num):
        assert self.red and not num.red, 'redPow(normalNum)'
        self.red._verify1(self)
        return self.red.pow(self, num)

    # Exported mostly for testing purposes, use plain name instead
    def prime(name):
        # Cached version of prime
        if (primes[name]):
            return primes[name]

        if (name == 'k256'):
            prime = K256()
        elif (name == 'p224'):
            prime = P224()
        elif (name == 'p192'):
            prime = P192()
        elif (name == 'p25519'):
            prime = P25519()
        else:
            raise Exception('Unknown prime ' + name)
        primes[name] = prime

        return prime

    # Montgomery method engine
    def mont(num):
        return Mont(num)

    # Prime numbers with efficient reduction
    primes = {
        'k256': None,
        'p224': None,
        'p192': None,
        'p25519': None
        }

# Pseudo-Mersenne prime
class MPrime:
    def __init__(self, name, p):
        # P = 2 ^ N - K
        self.name = name
        self.p = BN(p, 16)
        self.n = self.p.bitLength()
        self.k = BN(1).iushln(self.n).isub(self.p)

        self.tmp = self._tmp()

    def _tmp(self):
        tmp = BN(None)
        tmp.words = Array(math.ceil(self.n / 13))
        return tmp

    def ireduce(self, num):
        # Assumes that `num` is less than `P^2`
        # num = HI * (2 ^ N - K) + HI * K + LO = HI * K + LO (mod P)
        r = num

        while (rlen > self.n):
            self.split(r, self.tmp)
            r = self.imulK(r)
            r = r.iadd(self.tmp)
            rlen = r.bitLength()

        if rlen < self.n:
            cmp = -1
        else:
            cmp = r.ucmp(self.p)
        if (cmp == 0):
            r.words[0] = 0
            r.length = 1
        elif (cmp > 0):
            r.isub(self.p)
        else:
            r.strip()

        return r

    def split(self, input, out):
        input.iushrn(self.n, 0, out)

    def imulK(self, num):
        return num.imul(self.k)

class K256(MPrime):
    def __init__(self):
        super().__init__(
            'k256',
            'ffffffff ffffffff ffffffff ffffffff ffffffff ffffffff fffffffe fffffc2f')

    def split(input, output):
        # 256 = 9 * 26 + 22
        mask = 0x3fffff

        outLen = min(input.length, 9)
        i = 0
        while i < outLen:
            output.words[i] = input.words[i]
            i += 1
        output.length = outLen

        if (input.length <= 9):
            input.words[0] = 0
            input.length = 1
            return

        # Shift by 9 limbs
        prev = input.words[9]
        output.length += 1
        output.words[output.length] = prev & mask

        i = 10
        while i < input.length:
            next = input.words[i] | 0
            input.words[i - 10] = ((next & mask) << 4) | (prev >> 22)
            prev = next
            i += 1
        prev >>= 22
        input.words[i - 10] = prev
        if (prev == 0 and input.length > 10):
            input.length -= 10
        else:
            input.length -= 9

    def imulK(num):
        # K = 0x1000003d1 = [ 0x40, 0x3d1 ]
        num.words[num.length] = 0
        num.words[num.length + 1] = 0
        num.length += 2

        # bounded at: 0x40 * 0x3ffffff + 0x3d0 = 0x100000390
        lo = 0
        i = 0
        while i < num.length:
            w = num.words[i] | 0
            lo += w * 0x3d1
            num.words[i] = lo & 0x3ffffff
            lo = w * 0x40 + ((lo / 0x4000000) | 0)
            i += 1

        # Fast length reduction
        if (num.words[num.length - 1] == 0):
            num.length -= 1
            if (num.words[num.length - 1] == 0):
                num.length -= 1
        return num

class P224(MPrime):
    def __init__(self):
        super().__init__(
                'p224',
                'ffffffff ffffffff ffffffff ffffffff 00000000 00000000 00000001')

class P192(MPrime):
    def __init__(self):
        super().__init__(
                'p192',
                'ffffffff ffffffff ffffffff fffffffe ffffffff ffffffff')

class P25519(MPrime):
    def __init__(self):
        # 2 ^ 255 - 19
        super().__init__(
                '25519',
                '7fffffffffffffff ffffffffffffffff ffffffffffffffff ffffffffffffffed')

    def imulK(num):
        # K = 0x13
        carry = 0
        i = 0
        while i < num.length:
            hi = (num.words[i] | 0) * 0x13 + carry
            lo = hi & 0x3ffffff
            hi >>= 26

            num.words[i] = lo
            carry = hi
            i += 1
        if (carry != 0):
            num.length += 1
            num.words[num.length] = carry
        return num


# Base reduction engine
class Red:
    def __init__(self, m):
        if isinstance(m, str):
            prime = BN._prime(m)
            self.m = prime.p
            self.prime = prime
        else:
            assert m.gtn(1), 'modulus must be greater than 1'
            self.m = m
            self.prime = None

    def _verify1(a):
        assert a.negative == 0, 'red works only with positives'
        assert a.red, 'red works only with red numbers'

    def _verify2(a, b):
        assert (a.negative | b.negative) == 0, 'red works only with positives'
        assert a.red and a.red == b.red,  'red works only with red numbers'

    def imod(self, a):
        if (self.prime):
            return self.prime.ireduce(a)._forceRed(self)
        return a.umod(self.m)._forceRed(self)

    def neg(self, a):
        if (a.isZero()):
            return a.clone()

        return self.m.sub(a)._forceRed(self)

    def add(self, a, b):
        self._verify2(a, b)

        res = a.add(b)
        if (res.cmp(self.m) >= 0):
            res.isub(self.m)
        return res._forceRed(self)

    def iadd(self, a, b):
        self._verify2(a, b)

        res = a.iadd(b)
        if (res.cmp(self.m) >= 0):
            res.isub(self.m)
        return res

    def sub(self, a, b):
        self._verify2(a, b)

        res = a.sub(b)
        if (res.cmpn(0) < 0):
            res.iadd(self.m)
        return res._forceRed(self)

    def isub(self, a, b):
        self._verify2(a, b)

        res = a.isub(b)
        if (res.cmpn(0) < 0):
            res.iadd(self.m)
        return res

    def shl(self, a, num):
        self._verify1(a)
        return self.imod(a.ushln(num))

    def imul(self, a, b):
        self._verify2(a, b)
        return self.imod(a.imul(b))

    def mul(self, a, b):
        self._verify2(a, b)
        return self.imod(a.mul(b))

    def isqr(self, a):
        return self.imul(a, a.clone())

    def sqr(self, a):
        return self.mul(a, a)

    def sqrt(self, a):
        if (a.isZero()):
            return a.clone()

        mod3 = self.m.andln(3)
        assert (mod3 % 2 == 1)

        # Fast case
        if (mod3 == 3):
            pow = self.m.add(BN(1)).iushrn(2)
            return self.pow(a, pow)

        # Tonelli-Shanks algorithm (Totally unoptimized and slow)
        #
        # Find Q and S, that Q * 2 ^ S = (P - 1)

        q = self.m.subn(1)
        s = 0
        while (not q.isZero() and q.andln(1) == 0):
            s+= 1
            q.iushrn(1)
        assert (not q.isZero())

        one = BN(1).toRed(self)
        nOne = one.redNeg()

        # Find quadratic non-residue
        # NOTE: Max is such because of generalized Riemann hypothesis.
        lpow = self.m.subn(1).iushrn(1)
        z = self.m.bitLength()
        z = BN(2 * z * z).toRed(self)

        while (self.pow(z, lpow).cmp(nOne) != 0):
            z.redIAdd(nOne)

        c = self.pow(z, q)
        r = self.pow(a, q.addn(1).iushrn(1))
        t = self.pow(a, q)
        m = s
        while (t.cmp(one) != 0):
            tmp = t
            i = 0
            while tmp.cmp(one) != 0:
                tmp = tmp.redSqr()
                i += 1
            assert (i < m)
            b = self.pow(c, BN(1).iushln(m - i - 1))

            r = r.redMul(b)
            c = b.redSqr()
            t = t.redMul(c)
            m = i

        return r

    def invm(self, a):
        inv = a._invmp(self.m)
        if (inv.negative != 0):
            inv.negative = 0
            return self.imod(inv).redNeg()
        else:
            return self.imod(inv)

    def pow(self, a, num):
        if (num.isZero()):
            return BN(1).toRed(self)
        if (num.cmpn(1) == 0):
            return a.clone()

        windowSize = 4
        wnd = Array(1 << windowSize)
        wnd[0] = BN(1).toRed(self)
        wnd[1] = a
        i = 2
        while i < wnd.length:
            wnd[i] = self.mul(wnd[i - 1], a)
            i += 1

        res = wnd[0]
        current = 0
        currentLen = 0
        start = num.bitLength() % 26
        if (start == 0):
            start = 26

        i = num.length - 1
        while i >= 0:
            word = num.words[i]
            j = start - 1
            while j >= 0:
                bit = (word >> j) & 1
                if (res != wnd[0]):
                    res = self.sqr(res)

                if (bit == 0 and current == 0):
                    currentLen = 0
                    continue

                current <<= 1
                current |= bit
                currentLen += 1
                if (currentLen != windowSize and (i != 0 or j != 0)):
                    continue

                res = self.mul(res, wnd[current])
                currentLen = 0
                current = 0
                j -= 1
            start = 26
            i -= 1

        return res

    def convertTo(self, num):
        r = num.umod(self.m)
        if r == num:
            return r.clone()
        else:
            return  r

    def convertFrom(num):
        res = num.clone()
        res.red = None
        return res

class Mont(Red):
    def __init__(self, m):
        super().__init__(self, m)

        self.shift = self.m.bitLength()
        if (self.shift % 26 != 0):
            self.shift += 26 - (self.shift % 26)

        self.r = BN(1).iushln(self.shift)
        self.r2 = self.imod(self.r.sqr())
        self.rinv = self.r._invmp(self.m)

        self.minv = self.rinv.mul(self.r).isubn(1).div(self.m)
        self.minv = self.minv.umod(self.r)
        self.minv = self.r.sub(self.minv)

    def convertTo(self, num):
        return self.imod(num.ushln(self.shift))

    def convertFrom(self, num):
        r = self.imod(num.mul(self.rinv))
        r.red = None
        return r

    def imul(self, a, b):
        if (a.isZero() or b.isZero()):
            a.words[0] = 0
            a.length = 1
            return a

        t = a.imul(b)
        c = t.maskn(self.shift).mul(self.minv).imaskn(self.shift).mul(self.m)
        u = t.isub(c).iushrn(self.shift)
        res = u

        if (u.cmp(self.m) >= 0):
            res = u.isub(self.m)
        elif (u.cmpn(0) < 0):
            res = u.iadd(self.m)

        return res._forceRed(self)

    def mul(self, a, b):
        if (a.isZero() or b.isZero()):
            return BN(0)._forceRed(self)

        t = a.mul(b)
        c = t.maskn(self.shift).mul(self.minv).imaskn(self.shift).mul(self.m)
        u = t.isub(c).iushrn(self.shift)
        res = u
        if (u.cmp(self.m) >= 0):
            res = u.isub(self.m)
        elif (u.cmpn(0) < 0):
            res = u.iadd(self.m)

        return res._forceRed(self)

    def invm(self, a):
        # (AR)^-1 * R^2 = (A^-1 * R^-1) * R^2 = A^-1 * R
        res = self.imod(a._invmp(self.m).mul(self.r2))
        return res._forceRed(self)
