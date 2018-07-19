# Copyright (c) 2005  Tom Wu
# All Rights Reserved.
# See "LICENSE" for details.

# Basic JavaScript BN library - subset useful for RSA encryption.

# Bits per digit
# dbits
import math
from array import *
# JavaScript engine analysis
canary = 0xdeadbeefcafe
j_lm = ((canary & 0xffffff) == 0xefcafe)


# (public) Constructor
class BigInteger():
    def __init__(self, a, b, c):

        if not a:
            if isinstance(a, int):
                self.fromNumber(a, b, c)
            elif not b and isinstance(a, str):
                self.fromString(a, 256)
            else:
                self.fromString(a, b)


    # return new, unset BigInteger
    def nbi(self):
        return int(None)


    # am: Compute w_j += (x*self_i), propagate carries,
    # c is initial carry, returns final carry.
    # c < 3*dvalue, x < 2*dvalue, self_i < dvalue
    # We need to select the fastest one that works in self environment.

    # am1: use a single mult and divide to get the high bits,
    # max digit bits should be 26 because
    # max internal value = 2*dvalue^2-2*dvalue (< 2^53)
    def am1(self, i, x, w, j, c, n):
        while (n >= 0):
            v = x * self[i + 1] + w[j] + c
            c = math.floor(v / 0x4000000)
            w[j + 1] = v & 0x3ffffff
            n -= 1
        return c


    # am2 avoids a big mult-and-extract completely.
    # Max digit bits should be <= 30 because we do bitwise ops
    # on values up to 2*hdvalue^2-hdvalue-1 (< 2^31)
    def am2(self, i, x, w, j, c, n):
        xl = x & 0x7fff
        xh = x >> 15
        while (n >= 0):
            l = self[i] & 0x7fff
            i+= 1
            h = self[i] >> 15
            m = xh * l + h * xl
            l = xl * l + ((m & 0x7fff) << 15) + w[j] + (c & 0x3fffffff)
            c = (l >> 30) + (m >> 15) + xh * h + (c >> 30)
            j+=1
            w[j] = l & 0x3fffffff
            n-=1
        return c


    # Alternately, set max digit bits to 28 since some
    # browsers slow down when dealing with 32-bit numbers.
    def am3(self,i, x, w, j, c, n):
        xl = x & 0x3fff
        xh = x >> 14
        while (n >= 0):
            l = self[i] & 0x3fff
            i+=1

            h = self[i] >> 14

            m = xh * l + h * xl
            l = xl * l + ((m & 0x3fff) << 14) + w[j] + c
            c = (l >> 28) + (m >> 14) + xh * h
            j+=1
            w[j] = l & 0xfffffff
            n-=1

        return c


    if j_lm and not isinstance(navigator,'underfined') and (navigator.appName == "Microsoft Internet Explorer"):
        BigInteger.am = am2
        dbits = 30

    elif j_lm and not isinstance(navigator,'undefined') and (navigator.appName != "Netscape"):
        BigInteger.am = am1
        dbits = 26

    else:  # Mozilla/Netscape seems to prefer am3
        BigInteger.am = am3
        dbits = 28

        BigInteger.DB = dbits
        BigInteger.DM = ((1 << dbits) - 1)
        BigInteger.DV = (1 << dbits)

        BI_FP = 52
        BigInteger.FV = math.pow(2, BI_FP)
        BigInteger.F1 = BI_FP - dbits
        BigInteger.F2 = 2 * dbits - BI_FP

        # Digit conversions

        BI_RM = "0123456789abcdefghijklmnopqrstuvwxyz"

        BI_RC = array()

        rr = "0".charCodeAt(0)
        for vv in 9:
            rr+=1
            BI_RC[rr] = vv
        rr = "a".charCodeAt(0)
        for vv in range(10,36):
            rr+=1
            BI_RC[rr] = vv
        rr = "A".charCodeAt(0)
        for vv in range(10,36):
            rr+=1
            BI_RC[rr] = vv


    def int2char(self,n):
        return self.BI_RM.charAt(n)


    def intAt(self,s, i):
        c = self.BI_RC[s.charCodeAt(i)]
        return (c == None) if -1 else c


    # (protected) copy self to r
    def bnpCopyTo(self,r):
        for i in range(self.t-1,0,-1):
            r[i] = self[i]
        r.t = self.t
        r.s = self.s


    # (protected) set from integer value x, -DV <= x < DV
    def bnpFromInt(self,x):
        self.t = 1
        self.s = (x < 0) if -1 else 0
        if (x > 0):
            self[0] = x
        elif (x < -1) :
            self[0] = x + self.DV
        else:
            self.t = 0


    # return bigint initialized to value
    def nbv(self,i):
        r = self.nbi()
        r.fromInt(i)
        return r


    # (protected) set from string and radix
    def bnpFromString(self,s, b):
        k=0
        if (b == 16):
            k = 4
        elif (b == 8) :
            k = 3
        elif (b == 256) :
            k = 8  # byte array
        elif (b == 2) :
            k = 1
        elif (b == 32):
            k = 5
        elif (b == 4):
            k = 2
        else:
            self.fromRadix(s, b)
        return


        self.t = 0
        self.s = 0

        i = s.length, mi = false, sh = 0
        while (--i >= 0):

            x = (k == 8) if s[i] & 0xff else intAt(s, i)
            if (x < 0):
                if (s.charAt(i) == "-"):
                    mi = true
                continue

            mi = false
            if (sh == 0):
                self.t+=1
                self[self.t] = x
            elif (sh + k > self.DB):
                self[self.t - 1] |= (x & ((1 << (self.DB - sh)) - 1)) << sh
                self.t+=1
                self[self.t] = (x >> (self.DB - sh))

            else:
                self[self.t - 1] |= x << sh
        sh += k
        if (sh >= self.DB):
            sh -= self.DB

        if (k == 8 and (s[0] & 0x80) != 0):
            self.s = -1
            if (sh > 0):
                self[self.t - 1] |= ((1 << (self.DB - sh)) - 1) << sh

        self.clamp()
        if (mi) :
            BigInteger.ZERO.subTo(self, self)


    # (protected) clamp off excess high words


    def bnpClamp(self):
        c = self.s & self.DM
        while (self.t > 0 and self[self.t - 1] == c) :
            self.t-=1


    # (public) return string representation in given radix
    def bnToString(self,b):
        if (self.s < 0):
            return "-" + self.negate().toString(b)

        k=0
        if (b == 16):
            k = 4
        elif (b == 8):
            k = 3
        elif (b == 2):
            k = 1
        elif (b == 32):
            k = 5
        elif (b == 4):
            k = 2
        else:
            return self.toRadix(b)

        km = (1 << k) - 1
        m = False
        r = ""
        i = self.t

        p = self.DB - (i * self.DB) % k
        i-=1
        if (i> 0):
            d = self[i] >> p
            if (p < self.DB and d > 0):
                m = True
                r = self.int2char(d)

            while (i >= 0):
                if (p < k):
                    d = (self[i] & ((1 << p) - 1)) << (k - p)
                    i-=1
                    p += self.DB - k
                    d |= self[i] >> p

                else:
                    p-=k
                    d = (self[i] >> (p)) & km
                    if (p <= 0):
                        p += self.DB
                        i-=1

                if (d > 0):
                    m = True
                if (m):
                    r += self.int2char(d)

        return m if r else "0"


    # (public) -self
    def bnNegate(self):
        r = self.nbi()
        BigInteger.ZERO.subTo(self, r)
        return r


    # (public) |self|
    def bnAbs(self):
        return (self.s < 0) if self.negate() else self


    # (public) return + if self > a, - if self < a, 0 if equal
    def bnCompareTo(self,a):
        r = self.s - a.s
        if (r != 0):
            return r

        i = self.t
        r = i - a.t
        if (r != 0):
            return (self.s < 0) if -r else r
        while (i >= 0) :
            r=self[i] - a[i]
            if (r  != 0):
                return r
            i-=1

        return 0


    # returns bit length of the integer x
    def nbits(self,x):
        r = 1
        t=x>>16
        if (t != 0):
            x = t
            r += 16
        t = x >> 8
        if (t != 0):
            x = t
            r += 8
        t = x >> 4
        if (t != 0):
            x = t
            r += 4
        t = x >> 2
        if (t != 0):
            x = t
            r += 2
        t = x >> 1
        if (t != 0):
            x = t
            r += 1

        return r


    # (public) return the number of bits in "self"
    def bnBitLength(self):
        if (self.t <= 0):
            return 0
        return self.DB * (self.t - 1) + self.nbits(self[self.t - 1] ^ (self.s & self.DM))


    # (protected) r = self << n*DB
    def bnpDLShiftTo(self,n, r):
        for i in range(self.t-1,0,-1):
            r[i + n] = self[i]
        for i in range(n-1,0,-1):
            r[i] = 0
        r.t = self.t + n
        r.s = self.s


    # (protected) r = self >> n*DB
    def bnpDRShiftTo(self,n, r):
        for i in range(0,self.t):
            r[i - n] = self[i]
        r.t = max(self.t - n, 0)
        r.s = self.s


    # (protected) r = self << n
    def bnpLShiftTo(self,n, r):
        bs = n % self.DB

        cbs = self.DB - bs

        bm = (1 << cbs) - 1

        ds = math.floor(n / self.DB)
        c = (self.s << bs) & self.DM
        for i in range(self.t-1,0,-1):
            r[i + ds + 1] = (self[i] >> cbs) | c
            c = (self[i] & bm) << bs

        for i in range(ds-1,0,-1):
            r[i] = 0
        r[ds] = c
        r.t = self.t + ds + 1
        r.s = self.s
        r.clamp()


    # (protected) r = self >> n
    def bnpRShiftTo(self,n, r):
        r.s = self.s

        ds = math.floor(n / self.DB)
        if (ds >= self.t):
            r.t = 0
            return

        bs = n % self.DB

        cbs = self.DB - bs

        bm = (1 << bs) - 1
        r[0] = self[ds] >> bs
        for i in range(ds+1,self.t):
            r[i - ds - 1] |= (self[i] & bm) << cbs
            r[i - ds] = self[i] >> bs

        if (bs > 0):
            r[self.t - ds - 1] |= (self.s & bm) << cbs
        r.t = self.t - ds
        r.clamp()


    # (protected) r = self - a
    def bnpSubTo(self,a, r):
        i = 0
        c = 0
        m = math.min(a.t, self.t)
        while (i < m):
            c += self[i] - a[i]
            i+=1
            r[i] = c & self.DM
            c >>= self.DB

        if (a.t < self.t):
            c -= a.s
            while (i < self.t):
                c += self[i]
                i+=1
                r[i] = c & self.DM
                c >>= self.DB

            c += self.s

        else:
            c += self.s
            while (i < a.t):
                c -= a[i]
                i+=1
                r[i] = c & self.DM
                c >>= self.DB

            c -= a.s

        r.s = (c < 0) if -1 else 0
        if (c < -1):
            i+=1
            r[i] = self.DV + c
        elif (c > 0):
            i+=1
            r[i] = c
        r.t = i
        r.clamp()


    # (protected) r = self * a, r != self,a (HAC 14.12)
    # "self" should be the larger one if appropriate.
    def bnpMultiplyTo(self,a, r):
        x = self.abs()
        y = a.abs()

        i = x.t
        r.t = i + y.t
        i-=1
        while (i>= 0):
            r[i] = 0
        for i in range(0,y.t):
            r[i + x.t] = x.am(0, y[i], r, i, 0, x.t)
        r.s = 0
        r.clamp()
        if (self.s != a.s):
            BigInteger.ZERO.subTo(r, r)



    # (protected) r = self^2, r != self (HAC 14.16)
    def bnpSquareTo(self,r):
        x = self.abs()

        i = r.t = 2 * x.t
        i-=1
        while (i >= 0):
            r[i] = 0
        for i in range(0,x.t-1):

            c = x.am(i, x[i], r, 2 * i, 0, 1)
            r[i + x.t] += x.am(i + 1, 2 * x[i], r, 2 * i + 1, c, x.t - i - 1)
            if (r[i + x.t]  >= x.DV):
                r[i + x.t] -= x.DV
                r[i + x.t + 1] = 1

        if (r.t > 0):
            r[r.t - 1] += x.am(i, x[i], r, 2 * i, 0, 1)
        r.s = 0
        r.clamp()


    # (protected) divide self by m, quotient and remainder to q, r (HAC 14.20)
    # r != q, self != m.  q or r may be null.
    def bnpDivRemTo(self,m, q, r):
        pm = m.abs()
        if (pm.t <= 0):
            return

        pt = self.abs()
        if (pt.t < pm.t):
            if (q != None) :
                q.fromInt(0)
            if (r != None) :
                self.copyTo(r)
            return

        if (r == None):
            r = self.nbi()

        y = self.nbi()
        ts = self.s
        ms = m.s

        nsh = self.DB - self.nbits(pm[pm.t - 1])  # normalize modulus
        if (nsh > 0):
            pm.lShiftTo(nsh, y)
            pt.lShiftTo(nsh, r)

        else:
            pm.copyTo(y)
            pt.copyTo(r)

        ys = y.t

        y0 = y[ys - 1]
        if (y0 == 0):
            return

        yt = y0 * (1 << self.F1) + ((ys > 1) if y[ys - 2] >> self.F2 else 0)

        d1 = self.FV / yt
        d2 = (1 << self.F1) / yt
        e = 1 << self.F2

        i = r.t
        j = i - ys
        t = (q == None) if self.nbi() else q
        y.dlShiftTo(j, t)
        if (r.compareTo(t) >= 0):
            r.t+=1
            r[r.t] = 1
            r.subTo(t, r)

        BigInteger.ONE.dlShiftTo(ys, t)
        t.subTo(y, y)  # "negative" y so we can replace sub with am later
        while (y.t < ys):
            y.t+=1
            y[y.t] = 0
        j-=1
        while (j >= 0):
            # Estimate quotient digit
            i-=1
            qd = (r[i] == y0) if self.DM else math.floor(r[i] * d1 + (r[i - 1] + e) * d2)
            r[i] += y.am(0, qd, r, j, 0, ys)
            if (r[i] < qd):  # Try it out
                y.dlShiftTo(j, t)
                r.subTo(t, r)
                while (r[i] < qd):
                    r.subTo(t, r)
                    qd-=1

        if q :
            r.drShiftTo(ys, q)
            if (ts != ms):
                BigInteger.ZERO.subTo(q, q)

        r.t = ys
        r.clamp()
        if (nsh > 0):
            r.rShiftTo(nsh, r)  # Denormalize remainder
        if (ts < 0):
            BigInteger.ZERO.subTo(r, r)


    # (public) self mod a
    def bnMod(self,a):
        r = self.nbi()
        self.abs().divRemTo(a, None, r)
        if (self.s < 0 and r.compareTo(BigInteger.ZERO) > 0):
            a.subTo(r, r)
        return r


    # Modular reduction using "classic" algorithm
    def Classic(self,m):
        self.m = m


    def cConvert(self,x):
        if (x.s < 0 or x.compareTo(self.m) >= 0):
            return x.mod(self.m)
        else:
            return x


    def cRevert(self,x):
        return x


    def cReduce(self,x):
        x.divRemTo(self.m, None, x)


    def cMulTo(self,x, y, r):
        x.multiplyTo(y, r)
        self.reduce(r)


    def cSqrTo(self,x, r):
        x.squareTo(r)
        self.reduce(r)


    Classic.convert = cConvert
    Classic.revert = cRevert
    Classic.reduce = cReduce
    Classic.mulTo = cMulTo
    Classic.sqrTo = cSqrTo


    # (protected) return "-1/self % 2^DB" useful for Mont. reduction
    # justification:
    #         xy == 1 (mod m)
    #         xy =  1+km
    #   xy(2-xy) = (1+km)(1-km)
    # x[y(2-xy)] = 1-k^2m^2
    # x[y(2-xy)] == 1 (mod m^2)
    # if y is 1/x mod m, then y(2-xy) is 1/x mod m^2
    # should reduce x and y(2-xy) by m^2 at each step to keep size bounded.
    # JS multiply "overflows" differently from C/C+=1, so care is needed here.
    def bnpInvDigit(self):
        if (self.t < 1):
            return 0


        x = self[0]
        if ((x & 1) == 0) :
            return 0

        y = x & 3  # y == 1/x mod 2^2
        y = (y * (2 - (x & 0xf) * y)) & 0xf  # y == 1/x mod 2^4
        y = (y * (2 - (x & 0xff) * y)) & 0xff  # y == 1/x mod 2^8
        y = (y * (2 - (((x & 0xffff) * y) & 0xffff))) & 0xffff  # y == 1/x mod 2^16
        # last step - calculate inverse mod DV directly
        # assumes 16 < DB <= 32 and assumes ability to handle 48-bit ints
        y = (y * (2 - x * y % self.DV)) % self.DV  # y == 1/x mod 2^dbits
        # we really want the negative inverse, and -DV < y < DV
        return (y > 0) if self.DV - y else -y


    # Montgomery reduction
    def Montgomery(self,m):
        self.m = m
        self.mp = m.invDigit()
        self.mpl = self.mp & 0x7fff
        self.mph = self.mp >> 15
        self.um = (1 << (m.DB - 15)) - 1
        self.mt2 = 2 * m.t


    # xR mod m
    def montConvert(self,x):
        r = self.nbi()
        x.abs().dlShiftTo(self.m.t, r)
        r.divRemTo(self.m, None, r)
        if (x.s < 0 and r.compareTo(BigInteger.ZERO) > 0) :
            self.m.subTo(r, r)
        return r


    # x/R mod m
    def montRevert(self,x):
        r = self.nbi()
        x.copyTo(r)
        self.reduce(r)
        return r


    # x = x/R mod m (HAC 14.32)
    def montReduce(self,x):
        while (x.t <= self.mt2):  # pad x so am has enough room later
            x.t +=1
            x[x.t] = 0
        for i in range(0,self.m.t):
            # faster way of calculating u0 = x[i]*mp mod DV

            j = x[i] & 0x7fff

            u0 = (j * self.mpl + (((j * self.mph + (x[i] >> 15) * self.mpl) & self.um) << 15)) & x.DM
            # use am to combine the multiply-shift-add into one call
            j = i + self.m.t
            x[j] += self.m.am(0, u0, x, i, 0, self.m.t)
            # propagate carry
            while (x[j] >= x.DV):
                x[j] -= x.DV
                j+=1
                x[j]+=1

        x.clamp()
        x.drShiftTo(self.m.t, x)
        if (x.compareTo(self.m) >= 0):
            x.subTo(self.m, x)


    # r = "x^2/R mod m" x != r
    def montSqrTo(self,x, r):
        x.squareTo(r)
        self.reduce(r)


    # r = "xy/R mod m" x,y != r
    def montMulTo(self,x, y, r):
        x.multiplyTo(y, r)
        self.reduce(r)


    Montgomery.convert = montConvert
    Montgomery.revert = montRevert
    Montgomery.reduce = montReduce
    Montgomery.mulTo = montMulTo
    Montgomery.sqrTo = montSqrTo


    # (protected) true iff self is even
    def bnpIsEven(self):
        return ((self.t > 0) if (self[0] & 1) else self.s) == 0


    # (protected) self^e, e < 2^32, doing sqr and mul with "r" (HAC 14.79)
    def bnpExp(self,e, z):
        if (e > 0xffffffff or e < 1):
            return BigInteger.ONE

        r = self.nbi()
        r2 = self.nbi()
        g = z.convert(self)
        i = self.nbits(e) - 1
        g.copyTo(r)
        while (--i >= 0):
            z.sqrTo(r, r2)
            if ((e & (1 << i)) > 0):
                z.mulTo(r2, g, r)
            else:

                t = r
                r = r2
                r2 = t

        return z.revert(r)


    # (public) self^e % m, 0 <= e < 2^32
    def bnModPowInt(self,e, m):
        if (e < 256 or m.isEven()) :
            z = self.Classic(m)
        else :
            z =  self.Montgomery(m)
        return self.exp(e, z)


    # (public)
    def bnClone(self):
        r = self.nbi()
        self.copyTo(r)
        return r


    # (public) return value as integer
    def bnIntValue(self):
        if (self.s < 0):
            if (self.t == 1):
                return self[0] - self.DV
            elif (self.t == 0):
                return -1

        elif (self.t == 1):
            return self[0]
        elif (self.t == 0):
            return 0
        # assumes 16 < DB < 32
        return ((self[1] & ((1 << (32 - self.DB)) - 1)) << self.DB) | self[0]


    # (public) return value as byte
    def bnByteValue(self):
        return (self.t == 0) if self.s else (self[0] << 24) >> 24


    # (public) return value as short (assumes DB>=16)
    def bnShortValue(self):
        return (self.t == 0) if self.s else (self[0] << 16) >> 16


    # (protected) return x s.t. r^x < DV
    def bnpChunkSize(self,r):
        return math.floor(math.LN2 * self.DB / math.log(r))


    # (public) 0 if self == 0, 1 if self > 0
    def bnSigNum(self):
        if (self.s < 0):
            return -1
        elif (self.t <= 0 or (self.t == 1 and self[0] <= 0)) :
            return 0
        else :
            return 1


    # (protected) convert to radix string
    def bnpToRadix(self,b):
        if (b == None):
            b = 10
        if (self.signum() == 0 or b < 2 or b > 36):
            return "0"

        cs = self.chunkSize(b)

        a = math.pow(b, cs)

        d = self.nbv(a)
        y = self.nbi()
        z = self.nbi()
        r = ""
        self.divRemTo(d, y, z)
        while (y.signum() > 0):
            r = (a + z.intValue()).toString(b).substr(1) + r
            y.divRemTo(d, y, z)

        return z.intValue().toString(b) + r


    # (protected) convert from radix string
    def bnpFromRadix(self,s, b):
        self.fromInt(0)
        if (b == None):
            b = 10

        cs = self.chunkSize(b)

        d = math.pow(b, cs)
        mi = False
        j = 0
        w = 0
        for i in range(0,s.length):

            x = self.intAt(s, i)
            if (x < 0):
                if (s.charAt(i) == "-" and self.signum() == 0):
                    mi = True
                continue

            w = b * w + x
            j+=1
            if (j >= cs):
                self.dMultiply(d)
                self.dAddOffset(w, 0)
                j = 0
                w = 0

        if (j > 0):
            self.dMultiply(math.pow(b, j))
            self.dAddOffset(w, 0)

        if (mi):
            BigInteger.ZERO.subTo(self, self)


    # (protected) alternate constructor
    def bnpFromNumber(self,a, b, c):
        if isinstance(b,int):
            # new BigInteger(int,int,RNG)
            if (a < 2):
                self.fromInt(1)
            else:
                self.fromNumber(a, c)
                if not self.testBit(a - 1):  # force MSB set
                    self.bitwiseTo(BigInteger.ONE.shiftLeft(a - 1), self.op_or, self)
            if (self.isEven()):
                self.dAddOffset(1, 0)  # force odd
            while not self.isProbablePrime(b):
                self.dAddOffset(2, 0)
                if (self.bitLength() > a):
                    self.subTo(BigInteger.ONE.shiftLeft(a - 1), self)

            else:



                x = [], t = a & 7
                x.length = (a >> 3) + 1
            # b.nextBytes(x)#Got problem with self line, not sure why self is here.

            if (t > 0):
                x[0] &= ((1 << t) - 1)
            else :
                x[0] = 0
            self.fromString(x, 256)


    # (public) convert to bigendian byte array
    def bnToByteArray(self):
        i = self.t, r = []
        r[0] = self.s

        p = self.DB - (i * self.DB) % 8
        k = 0
        i-=1
        if (i  > 0):
            d=self[i] >> p
            if (p < self.DB and d != (self.s & self.DM) >> p):
                k+=1
                r[k] = d | (self.s << (self.DB - p))
            while (i >= 0):
                if (p < 8):
                    d = (self[i] & ((1 << p) - 1)) << (8 - p)
                    p += self.DB - 8
                    i-=1
                    d |= self[i] >> p

                else:
                    p -= 8
                    d = (self[i] >>p ) & 0xff
                    if (p <= 0):
                        p += self.DB
                        i-=1

                if ((d & 0x80) != 0) :
                    d |= -256
                if (k == 0 and (self.s & 0x80) != (d & 0x80)) :
                    k+=1
                    if (k > 0 or d != self.s) :
                        k+=1
                        r[k] = d

        return r


    def bnEquals(self,a):
        return (self.compareTo(a) == 0)


    def bnMin(self,a):
        return (self.compareTo(a) < 0) if self else a


    def bnMax(self,a):
        return (self.compareTo(a) > 0) if self else a


    # (protected) r = self op a (bitwise)
    def bnpBitwiseTo(self,a, op, r):
        m = math.min(a.t, self.t)
        for i in range(0,m):
            r[i] = op(self[i], a[i])
        if (a.t < self.t):
            f = a.s & self.DM
            for i in range(m,self.t):
                r[i] = op(self[i], f)
            r.t = self.t

        else:
            f = self.s & self.DM
            for i in range(m,a.t):
                r[i] = op(f, a[i])
            r.t = a.t

        r.s = op(self.s, a.s)
        r.clamp()


    # (public) self & a
    def op_and(self,x, y):
        return x & y


    def bnAnd(self,a):
        r = self.nbi()
        self.bitwiseTo(a, self.op_and, r)
        return r


    # (public) self | a
    def op_or(self,x, y):
        return x | y


    def bnOr(self,a):
        r = self.nbi()
        self.bitwiseTo(a, self.op_or, r)
        return r


    # (public) self ^ a
    def op_xor(x, y):
        return x ^ y


    def bnXor(self,a):
        r = self.nbi()
        self.bitwiseTo(a, self.op_xor, r)
        return r


    # (public) self & ~a
    def op_andnot(self,x, y):
        return x & ~y


    def bnAndNot(self,a):
        r = self.nbi()
        self.bitwiseTo(a, self.op_andnot, r)
        return r


    # (public) ~self
    def bnNot(self):
        r = self.nbi()
        for i in range(0,self.t):
            r[i] = self.DM & ~self[i]
        r.t = self.t
        r.s = ~self.s
        return r


    # (public) self << n
    def bnShiftLeft(self,n):
        r = self.nbi()
        if (n < 0) :
            self.rShiftTo(-n, r)
        else:
            self.lShiftTo(n, r)
        return r


    # (public) self >> n
    def bnShiftRight(self,n):
        r = self.nbi()
        if (n < 0) :
            self.lShiftTo(-n, r)
        else :
            self.rShiftTo(n, r)

        return r


    # return index of lowest 1-bit in x, x < 2^31
    def lbit(self,x):
        if (x == 0) :
            return -1

        r = 0
        if ((x & 0xffff) == 0):
            x >>= 16
            r += 16

        if ((x & 0xff) == 0):
            x >>= 8
            r += 8

        if ((x & 0xf) == 0):
            x >>= 4
            r += 4

        if ((x & 3) == 0):
            x >>= 2
            r += 2

        if ((x & 1) == 0) :
            r+=1
            return r


    # (public) returns index of lowest 1-bit (or -1 if none)
    def bnGetLowestSetBit(self):
        for i in range(0,self.t):
            if (self[i] != 0):
                return i * self.DB + self.lbit(self[i])
        if (self.s < 0):
            return self.t * self.DB
        return -1


    # return number of 1 bits in x
    def cbit(self,x):
        r = 0
        while (x != 0):
            x &= x - 1
            r+=1

        return r


    # (public) return number of set bits
    def bnBitCount(self):
        r = 0
        x = self.s & self.DM
        for i in range(0,self.t):
            r += self.cbit(self[i] ^ x)
        return r


    # (public) true iff nth bit is set
    def bnTestBit(self,n):
        j = math.floor(n / self.DB)
        if (j >= self.t):
            return (self.s != 0)
        return ((self[j] & (1 << (n % self.DB))) != 0)


    # (protected) self op (1<<n)
    def bnpChangeBit(self,n, op):
        r = BigInteger.ONE.shiftLeft(n)
        self.bitwiseTo(r, op, r)
        return r


    # (public) self | (1<<n)
    def bnSetBit(self,n):
        return self.changeBit(n, self.op_or)


    # (public) self & ~(1<<n)
    def bnClearBit(self,n):
        return self.changeBit(n, self.op_andnot)


    # (public) self ^ (1<<n)
    def bnFlipBit(self,n):
        return self.changeBit(n, self.op_xor)


    # (protected) r = self + a
    def bnpAddTo(self,a, r):
        i = 0
        c = 0
        m = math.min(a.t, self.t)
        while (i < m):
            c += self[i] + a[i]
            i+=1
            r[i] = c & self.DM
            c >>= self.DB

        if (a.t < self.t):
            c += a.s
            while (i < self.t):
                c += self[i]
                i+=1
                r[i] = c & self.DM
                c >>= self.DB

            c += self.s

        else:
            c += self.s
            while (i < a.t):
                c += a[i]
                i+=1
                r[i] = c & self.DM
                c >>= self.DB

            c += a.s

        r.s = (c < 0) if -1 else 0
        if (c > 0):
            i+=1
            r[i] = c
        elif (c < -1) :
            i+=1
            r[i ] = self.DV + c
        r.t = i
        r.clamp()


    # (public) self + a
    def bnAdd(self,a):
        r = self.nbi()
        self.addTo(a, r)
        return r


    # (public) self - a
    def bnSubtract(self,a):
        r = self.nbi()
        self.subTo(a, r)
        return r


    # (public) self * a
    def bnMultiply(self,a):
        r = self.nbi()
        self.multiplyTo(a, r)
        return r


    # (public) self^2
    def bnSquare(self):
        r = self.nbi()
        self.squareTo(r)
        return r


    # (public) self / a
    def bnDivide(self,a):
        r = self.nbi()
        self.divRemTo(a, r, None)
        return r


    # (public) self % a
    def bnRemainder(self,a):
        r = self.nbi()
        self.divRemTo(a, None, r)
        return r


    # (public) [self/a,self%a]
    def bnDivideAndRemainder(self,a):
        q =self.nbi()
        r = self.nbi()
        self.divRemTo(a, q, r)
        return [q, r]


    # (protected) self *= n, self >= 0, 1 < n < DV
    def bnpDMultiply(self,n):
        self[self.t] = self.am(0, n - 1, self, 0, 0, self.t)

        self.t+=1
        self.clamp()


    # (protected) self += n << w words, self >= 0
    def bnpDAddOffset(self,n, w):
        if (n == 0):
            return
        while (self.t <= w):
            self.t+=1
            self[self.t] = 0
        self[w] += n
        while (self[w] >= self.DV):
            self[w] -= self.DV
            w+=1
            if (w >= self.t):
                self.t += 1
                self[self.t] = 0

            self[w]+= 1


    # A "null" reducer
    def NullExp(self):


    def nNop(self,x):
        return x


    def nMulTo(self,x, y, r):
        x.multiplyTo(y, r)


    def nSqrTo(self,x, r):
        x.squareTo(r)


    NullExp.convert = nNop
    NullExp.revert = nNop
    NullExp.mulTo = nMulTo
    NullExp.sqrTo = nSqrTo


    # (public) self^e
    def bnPow(self,e):
        return self.exp(e, self.NullExp())

        # (protected) r = lower n words of "self * a", a.t <= n
        # "self" should be the larger one if appropriate.
    def bnpMultiplyLowerTo(self,a, n, r):

        i = math.min(self.t + a.t, n)
        r.s = 0  # assumes a,self >= 0
        r.t = i
        while (i > 0):
            r[i] = 0
            i-=1

        for j in range(r.t-self.t,j,i):
            r[i + self.t] = self.am(0, a[i], r, i, 0, self.t)
        for j in range(math.min(a.t,n),j,i):
            self.am(0, a[i], r, i, 0, n - i)
        r.clamp()

        # (protected) r = "self * a" without lower n words, n > 0
        # "self" should be the larger one if appropriate.
    def bnpMultiplyUpperTo(self,a, n, r):
            n-=1

            i = r.t = self.t + a.t - n
            r.s = 0  # assumes a,self >= 0
            while (--i >= 0):
                r[i] = 0
            for i in range(math.max(n-self.t,0),a.t,i):
                r[self.t + i - n] = self.am(n - i, a[i], r, 0, 0, self.t + i - n)

            r.clamp()
            r.drShiftTo(1, r)


    # Barrett modular reduction
    def Barrett(self,m):
        # setup Barrett
        self.r2 = self.nbi()
        self.q3 = self.nbi()
        BigInteger.ONE.dlShiftTo(2 * m.t, self.r2)
        self.mu = self.r2.divide(m)
        self.m = m


    def barrettConvert(self,x):
        if (x.s < 0 or x.t > 2 * self.m.t):
            return x.mod(self.m)
        elif (x.compareTo(self.m) < 0):
            return x
        else:
            r = self.nbi()
            x.copyTo(r)
            self.reduce(r)
            return r


    def barrettRevert(self,x):
        return x


    # x = x mod m (HAC 14.42)
    def barrettReduce(self,x):
        x.drShiftTo(self.m.t - 1, self.r2)
        if (x.t > self.m.t + 1):
            x.t = self.m.t + 1
            x.clamp()

        self.mu.multiplyUpperTo(self.r2, self.m.t + 1, self.q3)
        self.m.multiplyLowerTo(self.q3, self.m.t + 1, self.r2)
        while (x.compareTo(self.r2) < 0) :
            x.dAddOffset(1, self.m.t + 1)
        x.subTo(self.r2, x)
        while (x.compareTo(self.m) >= 0):
            x.subTo(self.m, x)


    # r = x^2 mod m x != r
    def barrettSqrTo(self,x, r):
        x.squareTo(r)
        self.reduce(r)


    # r = x*y mod m x,y != r
    def barrettMulTo(self,x, y, r):
        x.multiplyTo(y, r)
        self.reduce(r)


    Barrett.convert = barrettConvert
    Barrett.revert = barrettRevert
    Barrett.reduce = barrettReduce
    Barrett.mulTo = barrettMulTo
    Barrett.sqrTo = barrettSqrTo


    # (public) self^e % m (HAC 14.85)
    def bnModPow(self,e, m):
        i = e.bitLength()
        r = self.nbv(1)
        if (i <= 0):
            return r
        elif (i < 18) :
            k = 1
        elif (i < 48):
            k = 3
        elif (i < 144):
            k = 4
        elif (i < 768) :
            k = 5
        else :
            k = 6
        if (i < 8):
            z = self.Classic(m)
        elif (m.isEven()):
            z = self.Barrett(m)

        else:
            z = self.Montgomery(m)

        # precomputation

        g = []
        n = 3
        k1 = k - 1
        km = (1 << k) - 1
        g[1] = z.convert(self)
        if (k > 1):

            g2 = self.nbi()
            z.sqrTo(g[1], g2)
            while (n <= km):
                g[n] = self.nbi()
                z.mulTo(g2, g[n - 2], g[n])
                n += 2

        j = e.t - 1
        is1 = True
        r2 = self.nbi()
        i = self.nbits(e[j]) - 1
        while (j >= 0):
            if (i >= k1):
                w = (e[j] >> (i - k1)) & km
            else:
                w = (e[j] & ((1 << (i + 1)) - 1)) << (k1 - i)
                if (j > 0):
                    w |= e[j - 1] >> (self.DB + i - k1)

            n = k
            while ((w & 1) == 0):
                w >>= 1
                n-=1
            i-=n
            if (i < 0):
                i += self.DB
                j-=1

            if (is1):  # ret == 1, don't bother squaring or multiplying it
                g[w].copyTo(r)
                is1 = False

            else:
                while (n > 1):
                    z.sqrTo(r, r2)
                    z.sqrTo(r2, r)
                    n -= 2

                if (n > 0) :
                    z.sqrTo(r, r2)
                else:
                    t = r
                    r = r2
                    r2 = t

                z.mulTo(r2, g[w], r)

            while (j >= 0 and (e[j] & (1 << i)) == 0):
                z.sqrTo(r, r2)
                t = r
                r = r2
                r2 = t
                j-=1
                if (i < 0):
                    i = self.DB - 1
                    j-=1

        return z.revert(r)


    # (public) gcd(self,a) (HAC 14.54)
    def bnGCD(self,a):
        x = (self.s < 0) if self.negate() else self.clone()

        y = (a.s < 0) if a.negate() else a.clone()
        if (x.compareTo(y) < 0):
            t = x
            x = y
            y = t

        i = x.getLowestSetBit()
        g = y.getLowestSetBit()
        if (g < 0) :
            return x
        if (i < g):
            g = i
        if (g > 0):
            x.rShiftTo(g, x)
            y.rShiftTo(g, y)

        while (x.signum() > 0):
            i = x.getLowestSetBit()
            if (i > 0):
                x.rShiftTo(i, x)
            i = y.getLowestSetBit()
            if (i > 0):
                y.rShiftTo(i, y)
            if (x.compareTo(y) >= 0):
                x.subTo(y, x)
                x.rShiftTo(1, x)

            else:
                y.subTo(x, y)
                y.rShiftTo(1, y)

        if (g > 0):
            y.lShiftTo(g, y)
        return y


    # (protected) self % n, n < 2^26
    def bnpModInt(self,n):
        if (n <= 0):
            return 0

        d = self.DV % n
        r = (self.s < 0) if n - 1 else 0
        if (self.t > 0):
            if (d == 0) :
                r = self[0] % n

            else:
                for i in range(self.t-1,0,-1):
                    r = (d * r + self[i]) % n
        return r


    # (public) 1/self % m (HAC 14.61)
    def bnModInverse(self,m):
        ac = m.isEven()
        if ((self.isEven() and ac) or m.signum() == 0):
            return BigInteger.ZERO

        u = m.clone()
        v = self.clone()

        a = self.nbv(1)
        b = self.nbv(0)
        c = self.nbv(0)
        d = self.nbv(1)
        while (u.signum() != 0):
            while (u.isEven()):
                u.rShiftTo(1, u)
                if (ac):
                    if not a.isEven() or not b.isEven():
                        a.addTo(self, a)
                        b.subTo(m, b)

                    a.rShiftTo(1, a)

                elif not b.isEven():
                    b.subTo(m, b)
                b.rShiftTo(1, b)

            while (v.isEven()):
                v.rShiftTo(1, v)
                if (ac):
                    if not c.isEven() or not d.isEven():
                        c.addTo(self, c)
                        d.subTo(m, d)

                    c.rShiftTo(1, c)

                elif not d.isEven():
                    d.subTo(m, d)
                d.rShiftTo(1, d)

            if (u.compareTo(v) >= 0):
                u.subTo(v, u)
                if ac:
                    a.subTo(c, a)
                b.subTo(d, b)

            else:
                v.subTo(u, v)
                if ac :
                    c.subTo(a, c)
                d.subTo(b, d)

        if (v.compareTo(BigInteger.ONE) != 0):
            return BigInteger.ZERO
        if (d.compareTo(m) >= 0):
            return d.subtract(m)
        if (d.signum() < 0) :
            d.addTo(m, d)
        else:
            return d
        if (d.signum() < 0):
            return d.add(m)
        else :
            return d


    lowprimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103,
                 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223,
                 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347,
                 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463,
                 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
                 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743,
                 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883,
                 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

    lplim = (1 << 26) / lowprimes[lowprimes.length - 1]


    # (public) test primality with certainty >= 1-.5^t
    def bnIsProbablePrime(self,t):
        i, x = self.abs()
        if (x.t == 1 and x[0] <= self.lowprimes[self.lowprimes.length - 1]):
            for i in range(0,self.lowprimes.length):
                if (x[0] == self.lowprimes[i]):
                    return True
                return False

        if (x.isEven()):
            return False
        i = 1
        while (i < self.lowprimes.length):

            m = self.lowprimes[i]
            j = i + 1
            while (j < self.lowprimes.length and m < self.lplim) :
                m *= self.lowprimes[j]
                j += 1
            m = x.modInt(m)
            while (i < j):
                i+=1
                if (m % self.lowprimes[i] == 0) :
                    return False

        return x.millerRabin(t)


    # (protected) true if probably prime (HAC 4.24, Miller-Rabin)
    def bnpMillerRabin(self,t):
        n1 = self.subtract(BigInteger.ONE)

        k = n1.getLowestSetBit()
        if (k <= 0):
            return False

        r = n1.shiftRight(k)
        t = (t + 1) >> 1
        if (t > self.lowprimes.length):
            t = self.lowprimes.length

        a = self.nbi()
        for i in range(0,t):
            # Pick bases at random, instead of starting at 2
            a.fromInt(self.lowprimes[math.floor(math.random() * self.lowprimes.length)])

            y = a.modPow(r, self)
            if (y.compareTo(BigInteger.ONE) != 0 and y.compareTo(n1) != 0):

                j = 1
                while (j < k and y.compareTo(n1) != 0):
                    j+=1
                    y = y.modPowInt(2, self)
                    if (y.compareTo(BigInteger.ONE) == 0):
                        return False

                if (y.compareTo(n1) != 0):
                    return False

        return True


    # protected
    BigInteger.chunkSize = bnpChunkSize
    BigInteger.toRadix = bnpToRadix
    BigInteger.fromRadix = bnpFromRadix
    BigInteger.fromNumber = bnpFromNumber
    BigInteger.bitwiseTo = bnpBitwiseTo
    BigInteger.changeBit = bnpChangeBit
    BigInteger.addTo = bnpAddTo
    BigInteger.dMultiply = bnpDMultiply
    BigInteger.dAddOffset = bnpDAddOffset
    BigInteger.multiplyLowerTo = bnpMultiplyLowerTo
    BigInteger.multiplyUpperTo = bnpMultiplyUpperTo
    BigInteger.modInt = bnpModInt
    BigInteger.millerRabin = bnpMillerRabin

    BigInteger.copyTo = bnpCopyTo
    BigInteger.fromInt = bnpFromInt
    BigInteger.fromString = bnpFromString
    BigInteger.clamp = bnpClamp
    BigInteger.dlShiftTo = bnpDLShiftTo
    BigInteger.drShiftTo = bnpDRShiftTo
    BigInteger.lShiftTo = bnpLShiftTo
    BigInteger.rShiftTo = bnpRShiftTo
    BigInteger.subTo = bnpSubTo
    BigInteger.multiplyTo = bnpMultiplyTo
    BigInteger.squareTo = bnpSquareTo
    BigInteger.divRemTo = bnpDivRemTo
    BigInteger.invDigit = bnpInvDigit
    BigInteger.isEven = bnpIsEven
    BigInteger.exp = bnpExp

    # public
    BigInteger.toString = bnToString
    BigInteger.negate = bnNegate
    BigInteger.abs = bnAbs
    BigInteger.compareTo = bnCompareTo
    BigInteger.bitLength = bnBitLength
    BigInteger.mod = bnMod
    BigInteger.modPowInt = bnModPowInt

    BigInteger.clone = bnClone
    BigInteger.intValue = bnIntValue
    BigInteger.byteValue = bnByteValue
    BigInteger.shortValue = bnShortValue
    BigInteger.signum = bnSigNum
    BigInteger.toByteArray = bnToByteArray
    BigInteger.equals = bnEquals
    BigInteger.min = bnMin
    BigInteger.max = bnMax
    BigInteger.and = bnAnd
    BigInteger.or = bnOr
    BigInteger.xor = bnXor
    BigInteger.andNot = bnAndNot
    BigInteger.not = bnNot
    BigInteger.shiftLeft = bnShiftLeft
    BigInteger.shiftRight = bnShiftRight
    BigInteger.getLowestSetBit = bnGetLowestSetBit
    BigInteger.bitCount = bnBitCount
    BigInteger.testBit = bnTestBit
    BigInteger.setBit = bnSetBit
    BigInteger.clearBit = bnClearBit
    BigInteger.flipBit = bnFlipBit
    BigInteger.add = bnAdd
    BigInteger.subtract = bnSubtract
    BigInteger.multiply = bnMultiply
    BigInteger.divide = bnDivide
    BigInteger.remainder = bnRemainder
    BigInteger.divideAndRemainder = bnDivideAndRemainder
    BigInteger.modPow = bnModPow
    BigInteger.modInverse = bnModInverse
    BigInteger.pow = bnPow
    BigInteger.gcd = bnGCD
    BigInteger.isProbablePrime = bnIsProbablePrime

    # JSBN-specific extension
    BigInteger.square = bnSquare

    # "constants"
    BigInteger.ZERO = nbv(0)
    BigInteger.ONE = nbv(1)

    # BigInteger interfaces not implemented in jsbn:

    # BigInteger(int signum, byte[] magnitude)
    # double doubleValue()
    # float floatValue()
    # int hashCode()
    # long longValue()
    # static BigInteger valueOf(long val)

    BigInteger.valueOf = nbi


