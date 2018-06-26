# BN = require('bn.js')
# elliptic = require('../../elliptic')
# utils = elliptic.utils
# getNAF = utils.getNAF
# getJSF = utils.getJSF
# assert = utils.assert
import sys
sys.path.append("..\src")
import math
import utils

class BaseCurve:
    def __init__(self, type, conf):
        self.type = type
        self.p = BN(conf.p, 16)

        # Use Montgomery, when there is no fast reduction for the prime
        if conf.prime:
            self.red = BN.red(conf.prime)
        else:
            self.red = BN.mont(self.p)

        # Useful for many curves
        self.zero = BN(0).toRed(self.red)
        self.one = BN(1).toRed(self.red)
        self.two = BN(2).toRed(self.red)

        # Curve configuration, optional
        self.n = conf.n and BN(conf.n, 16)
        self.g = conf.g and self.pointFromJSON(conf.g, conf.gRed)

        # Temporary arrays
        self._wnafT1 = [None,None,None,None]
        self._wnafT2 = [None,None,None,None]
        self._wnafT3 = [None,None,None,None]
        self._wnafT4 = [None,None,None,None]

        # Generalized Greg Maxwell's trick
        adjustCount = self.n and self.p.div(self.n)

        if (not adjustCount or adjustCount.cmpn(100) > 0):
            self.redN = None
        else:
            self._maxwellTrick = True
            self.redN = self.n.toRed(self.red)

    def point():
        raise Exception('Not implemented')

    def validate():
        raise Exception('Not implemented')

    def _fixedNafMul(self, p, k):
        assert p.precomputed
        doubles = p._getDoubles()

        naf = utils.getNAF(k, 1)
        if (doubles.step%2 == 0):
            i = (1 << (doubles.step + 1)) -2
        else:
            i = (1 << (doubles.step + 1)) -1

        i /= 3

        # Translate into more windowed form
        repr = []
        j = 0
        while j < len(naf):
            nafW = 0
            k = j + doubles.step - 1
            while k >= j:
                nafW = (nafW << 1) + naf[k]
                k -= 1
            repr.append(nafW)
            j += doubles.step

        a = self.jpoint(None, None, None)
        b = self.jpoint(None, None, None)
        while i > 0:
            j = 0
            while j < len(repr):
                nafW = repr[j]
                if (nafW == i):
                    b = b.mixedAdd(doubles.points[j])
                elif (nafW == -i):
                    b = b.mixedAdd(doubles.points[j].neg())
                j += 1
            a = a.add(b)
            i -= 1
        return a.toP()

    def _wnafMul(self, p, k):
        w = 4

        # Precompute window
        nafPoints = p._getNAFPoints(w)
        w = nafPoints.wnd
        wnd = nafPoints.points

        # Get NAF form
        naf = utils.getNAF(k, w)

        # Add self` * (N + 1) for every w - NAF index
        acc = self.jpoint(None, None, None)
        i = len(naf) - 1
        while i >= 0:
            # Count zeroes
            k = 0
            while i >= 0 and naf[i] == 0:
                k +=1
                i -=1
            if (i >= 0):
                k +=1
            acc = acc.dblp(k)

            if (i < 0):
                break
            z = naf[i]
            assert z != 0
            if (p.type == 'affine'):
                # J + - P
                if (z > 0):
                    acc = acc.mixedAdd(wnd[(z - 1) >> 1])
                else:
                    acc = acc.mixedAdd(wnd[(-z - 1) >> 1].neg())
            else:
                # J + - J
                if (z > 0):
                    acc = acc.add(wnd[(z - 1) >> 1])
                else:
                    acc = acc.add(wnd[(-z - 1) >> 1].neg())
            i -= 1

            if p.type == 'affine':
                return acc.toP()
            else:
                return acc

    def _wnafMulAdd(self, defW,
                    points,
                    coeffs,
                    len,
                    jacobianResult):
        wndWidth = self._wnafT1
        wnd = self._wnafT2
        naf = self._wnafT3

        # Fill all arrays
        max = 0
        i = 0
        while i < len:
            p = points[i]
            nafPoints = p._getNAFPoints(defW)
            wndWidth[i] = nafPoints.wnd
            wnd[i] = nafPoints.points
            i -= 1

        # Comb small window NAFs
        i = len - 1
        while i >= 1:
            a = i - 1
            b = i
            if (wndWidth[a] != 1 or wndWidth[b] != 1):
                naf[a] = utils.getNAF(coeffs[a], wndWidth[a])
                naf[b] = utils.getNAF(coeffs[b], wndWidth[b])
                max = max(naf[a].length, max)
                max = max(naf[b].length, max)
                continue

            comb = [
                points[a], #1
                None,  #3
                None,  #5
                points[b] # 7
            ]

            # Try to avoid Projective points, if possible
            if (points[a].y.cmp(points[b].y) == 0):
                comb[1] = points[a].add(points[b])
                comb[2] = points[a].toJ().mixedAdd(points[b].neg())
            elif (points[a].y.cmp(points[b].y.redNeg()) == 0):
                comb[1] = points[a].toJ().mixedAdd(points[b])
                comb[2] = points[a].add(points[b].neg())
            else:
                comb[1] = points[a].toJ().mixedAdd(points[b])
                comb[2] = points[a].toJ().mixedAdd(points[b].neg())

            index =[
                -3, # -1 -1
                -1, # -1 0
                -5, # -1 1
                -7, # 0 -1
                0, #0 0
                7, # 0 1
                5, # 1 -1
                1, # 1 0
                3 #1 1
            ]

            jsf = utils.getJSF(coeffs[a], coeffs[b])
            max = max(len(jsf[0]), max)
            if max > 0:
                naf[a]=[]
                naf[b]=[]
            nafcount=0
            while nafcount < max:
                naf[a].append(None)
                naf[b].append(None)
                nafcount += 1

            j = 0
            while j < max:
                ja = jsf[0][j] | 0
                jb = jsf[1][j] | 0

                naf[a][j] = index[(ja + 1) * 3 + (jb + 1)]
                naf[b][j] = 0
                wnd[a] = comb
                j += 1
            i -= 2

        acc = self.jpoint(None, None, None)
        tmp = self._wnafT4
        i = max
        while i >= 0:
            k = 0

            while (i >= 0):
                zero = True
                j = 0
                while j < len:
                    tmp[j] = naf[j][i] | 0
                    if (tmp[j] != 0):
                        zero = False
                    j += 1
                if (not zero):
                    break
                k += 1
                i -= 1

            if (i >= 0):
                k += 1
            acc = acc.dblp(k)
            if (i < 0):
                break

            j = 0
            while j < len:
                z = tmp[j]
                if (z == 0):
                    continue
                elif (z > 0):
                    p = wnd[j][(z - 1) >> 1]
                elif (z < 0):
                    p = wnd[j][(-z - 1) >> 1].neg()

                if (p.type == 'affine'):
                    acc = acc.mixedAdd(p)
                else:
                    acc = acc.add(p)
                j += 1

            i -= 1

        # Zeroify references
        i = 0
        while i < len:
            wnd[i] = None
            i += 1

        if (jacobianResult):
            return acc
        else:
            return acc.toP()

class BasePoint:
    def __init__(self, curve, type):
        self.curve = curve
        self.type = type
        self.precomputed = None

    def eq():
        raise Exception('Not implemented')

    def validate(self):
        return self.curve.validate(self)

    def decodePoint(self, bytes, enc):
        bytes = utils.toArray(bytes, enc)

        len = self.p.byteLength()

        # uncompressed, hybrid - odd, hybrid - even
        if ((bytes[0] == 0x04 or bytes[0] == 0x06 or bytes[0] == 0x07) and
                bytes.length - 1 == 2 * len):
            if (bytes[0] == 0x06):
                assert (bytes[bytes.length - 1] % 2 == 0)
            elif (bytes[0] == 0x07):
                assert (bytes[bytes.length - 1] % 2 == 1)

            res = self.point(bytes.slice(1, 1 + len),
                             bytes.slice(1 + len, 1 + 2 * len))

            return res
        elif ((bytes[0] == 0x02 or bytes[0] == 0x03) and bytes.length - 1 == len):
            return self.pointFromX(bytes.slice(1, 1 + len), bytes[0] == 0x03)

        raise Exception('Unknown point format')

    def encodeCompressed(self, enc):
        return self.encode(enc, True)

    def _encode(self, compact):
        len = self.curve.p.byteLength()
        x = self.getX().toArray('be', len)

        if (compact):
            if self.getY().isEven():
                return [0x02].concat(x)
            else:
                return [0x03].concat(x)

        return [0x04].concat(x, self.getY().toArray('be', len))

    def encode(self, enc, compact):
        return utils.encode(self._encode(compact), enc)

    def precompute(self, power):
        if (self.precomputed):
            return self

        precomputed = {
            'doubles': None,
            'naf': None,
            'beta': None
        }

        precomputed.naf = self._getNAFPoints(8)
        precomputed.doubles = self._getDoubles(4, power)
        precomputed.beta = self._getBeta()
        self.precomputed = precomputed

        return self

    def _hasDoubles(self, k):
        if (not self.precomputed):
            return False

        doubles = self.precomputed.doubles
        if (not doubles):
            return False

        return doubles.points.length >= math.ceil((k.bitLength() + 1) / doubles.step)

    def _getDoubles(self, step, power):
        if (self.precomputed and self.precomputed.doubles):
            return self.precomputed.doubles

        doubles = [self]
        acc = self

        i = 0
        while i < power:
            j = 0
            while j < step:
                acc = acc.dbl()
                j += 1
            doubles.append(acc)
            i += step

        return {
            'step': step,
            'points': doubles
        }

    def _getNAFPoints(self, wnd):
        if (self.precomputed and self.precomputed.naf):
            return self.precomputed.naf

        res = [self]
        max = (1 << wnd) - 1
        if max == 1:
            dbl= None
        else:
            dbl = self.dbl()

        i = 1
        while i < max:
            res[i] = res[i - 1].add(dbl)
            i += 1
        return {
            'wnd': wnd,
            'points': res
        }

    def _getBeta():
        return None

    def dblp(self, k):
        r = self

        i = 0
        while i < k:
            r = r.dbl()
            i += 1
        return r
