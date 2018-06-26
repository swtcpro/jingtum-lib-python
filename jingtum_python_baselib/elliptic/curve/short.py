# curve = require('../curve')
# elliptic = require('../../elliptic')
# BN = require('bn.js')
# inherits = require('inherits')
# Base = curve.base
import sys
sys.path.append("..")
import math
from curve.base import *
import bn.bn
#import base

class ShortCurve(BaseCurve):
    def __init__(self, conf):
        super().__init__('short', conf)

        self.a = BN(conf.a, 16).toRed(self.red)
        self.b = BN(conf.b, 16).toRed(self.red)
        self.tinv = self.two.redInvm()

        self.zeroA = self.a.fromRed().cmpn(0) == 0
        self.threeA = self.a.fromRed().sub(self.p).cmpn(-3) == 0

        # If the curve is endomorphic, precalculate beta and lambda
        self.endo = self._getEndomorphism(conf)
        self._endoWnafT1 = [None,None,None,None]
        self._endoWnafT2 = [None,None,None,None]

    def vec():
        return {
            a: BN(a, 16),
            b: BN(b, 16)
        }

    def _getEndomorphism(self, conf):
        # No efficient endomorphism
        if (not self.zeroA or not self.g or not self.n or self.p.modn(3) != 1):
            return
        """
        # Compute beta and lambda, that lambda * P = (beta * Px Py)
        if (conf.beta):
            beta = BN(conf.beta, 16).toRed(self.red)
        else:
            betas = self._getEndoRoots(self.p)
            # Choose the smallest beta
            if betas[0].cmp(betas[1]) < 0:
                beta = betas[0]
            else:
                beta = betas[1]
            beta = beta.toRed(self.red)

        if  hasattr(conf, 'lambda'):
            lambda = BN(conf.lambda, 16)
        else:
            # Choose the lambda that is matching selected beta
            lambdas = self._getEndoRoots(self.n)
            if (self.g.mul(lambdas[0]).x.cmp(self.g.x.redMul(beta)) == 0):
                lambda = lambdas[0]
            else:
                lambda = lambdas[1]
                assert self.g.mul( lambda ).x.cmp(self.g.x.redMul(beta)) == 0


        # Get basis vectors, used for balanced length-two representation
        if (conf.basis):
            basis = map(vec, conf.basis)
        else:
            basis = self._getEndoBasis(lambda)

        return {
            'beta': beta,
            'lambda': lambda,
            'basis': basis
        }
        """

    def _getEndoRoots(num):
        # Find roots of for x^2 + x + 1 in F
        # Root = (-1 +- Sqrt(-3)) / 2
        if num == self.p:
            red = self.red
        else:
            red = BN.mont(num)
        tinv = BN(2).toRed(red).redInvm()
        ntinv = tinv.redNeg()

        s = BN(3).toRed(red).redNeg().redSqrt().redMul(tinv)

        l1 = ntinv.redAdd(s).fromRed()
        l2 = ntinv.redSub(s).fromRed()
        return [l1, l2]

    """
    def _getEndoBasis(self, lambda):
        # aprxSqrt >= sqrt(self.n)
        aprxSqrt = self.n.ushrn(math.floor(self.n.bitLength() / 2))

        # 3.74
        # Run EGCD, until r(L + 1) < aprxSqrt
        u = lambda
        v = self.n.clone()
        x1 =  BN(1)
        y1 =  BN(0)
        x2 =  BN(0)
        y2 =  BN(1)

        #NOTE: all vectors are roots of: a + b * lambda = 0 (mod n)
        a0
        b0
        # First vector
        a1
        b1
        # Second vector
        a2
        b2
        

        i = 0
        while (u.cmpn(0) != 0):
            q = v.div(u)
            r = v.sub(q.mul(u))
            x = x2.sub(q.mul(x1))
            y = y2.sub(q.mul(y1))

            if (not a1 and r.cmp(aprxSqrt) < 0):
                a0 = prevR.neg()
                b0 = x1
                a1 = r.neg()
                b1 = x
            elif a1:
                i += 1
                if i == 2:
                    break

            prevR = r

            v = u
            u = r
            x2 = x1
            x1 = x
            y2 = y1
            y1 = y

        a2 = r.neg()
        b2 = x

        len1 = a1.sqr().add(b1.sqr())
        len2 = a2.sqr().add(b2.sqr())
        if (len2.cmp(len1) >= 0):
            a2 = a0
            b2 = b0

        # Normalize signs
        if (a1.negative):
            a1 = a1.neg()
            b1 = b1.neg()
        if (a2.negative):
            a2 = a2.neg()
            b2 = b2.neg()

        return[
            {a: a1, b: b1},
            {a: a2, b: b2}
        ]
    """

    def _endoSplit(self, k):
        basis = self.endo.basis
        v1 = basis[0]
        v2 = basis[1]

        c1 = v2.b.mul(k).divRound(self.n)
        c2 = v1.b.neg().mul(k).divRound(self.n)

        p1 = c1.mul(v1.a)
        p2 = c2.mul(v2.a)
        q1 = c1.mul(v1.b)
        q2 = c2.mul(v2.b)

        # Calculate answer
        k1 = k.sub(p1).sub(p2)
        k2 = q1.add(q2).neg()

        return {k1: k1, k2: k2}

    def pointFromX(x, odd):
        x = BN(x, 16)
        if (not x.red):
            x = x.toRed(self.red)

        y2 = x.redSqr().redMul(x).redIAdd(x.redMul(self.a)).redIAdd(self.b)
        y = y2.redSqrt()
        if (y.redSqr().redSub(y2).cmp(self.zero) != 0):
            raise Exception('invalid point')

        # XXX Is there any way to tell if the number is odd without converting it
        # to non-red form?
        isOdd = y.fromRed().isOdd()
        if (odd and not isOdd or not odd and isOdd):
            y = y.redNeg()

        return self.point(x, y)

    def validate(point):
        if (point.inf):
            return True

        x = point.x
        y = point.y

        ax = self.a.redMul(x)
        rhs = x.redSqr().redMul(x).redIAdd(ax).redIAdd(self.b)
        return y.redSqr().redISub(rhs).cmpn(0) == 0

    def _endoWnafMulAdd(points, coeffs, jacobianResult):
        npoints = self._endoWnafT1
        ncoeffs = self._endoWnafT2
        i = 0
        while i < points.length:
            split = self._endoSplit(coeffs[i])
            p = points[i]
            beta = p._getBeta()

            if (split.k1.negative):
                split.k1.ineg()
                p = p.neg(True)
            if (split.k2.negative):
                split.k2.ineg()
                beta = beta.neg(True)

            npoints[i * 2] = p
            npoints[i * 2 + 1] = beta
            ncoeffs[i * 2] = split.k1
            ncoeffs[i * 2 + 1] = split.k2
            i += 1

        res = self._wnafMulAdd(1, npoints, ncoeffs, i * 2, jacobianResult)

        # Clean-up references to points and coefficients
        j = 0
        while j < i * 2:
            npoints[j] = None
            ncoeffs[j] = None
            j += 1
        return res

    def point(self, x, y, isRed):
        return Point(self, x, y, isRed)

    def pointFromJSON(obj, red):
        return Point.fromJSON(self, obj, red)

class Point(BasePoint):
    def __init__(self, curve, x, y, isRed):
        super().__init__(self, curve, 'affine')
        if (x == None and y == None):
            self.x = None
            self.y = None
            self.inf = True
        else:
            self.x = BN(x, 16)
            self.y = BN(y, 16)
            # Force redgomery representation when loading from JSON
            if (isRed):
                self.x.forceRed(self.curve.red)
                self.y.forceRed(self.curve.red)
            if (not self.x.red):
                self.x = self.x.toRed(self.curve.red)
            if (not self.y.red):
                self.y = self.y.toRed(self.curve.red)
        self.inf = False

    def endoMul(p):
        return curve.point(p.x.redMul(curve.endo.beta), p.y)

    def _getBeta(self):
        if (not self.curve.endo):
            return

        pre = self.precomputed
        if (pre and pre.beta):
            return pre.beta

        beta = self.curve.point(self.x.redMul(self.curve.endo.beta), self.y)
        if (pre):
            curve = self.curve
            pre.beta = beta
            beta.precomputed = {
                    beta: None,
                    naf: pre.naf and {
                    wnd: pre.naf.wnd,
                    points: map(endoMul, pre.naf.points.map)
                },
                doubles: pre.doubles and {
                    step: pre.doubles.step,
                    points: map(endoMul, pre.doubles.points)
                }
            }
        return beta

    def toJSON(self):
        if (not self.precomputed):
            return [self.x, self.y]

        return [self.x, self.y, self.precomputed and {
            doubles: self.precomputed.doubles and {
            step: self.precomputed.doubles.step,
            points: self.precomputed.doubles.points.slice(1)
        },
        naf: self.precomputed.naf and {
            wnd: self.precomputed.naf.wnd,
            points: self.precomputed.naf.points.slice(1)
        }
        }]

    def fromJSON(curve, obj, red):
        if isinstance(obj, str):
            obj = JSON.parse(obj)
        res = curve.point(obj[0], obj[1], red)
        if (not obj[2]):
            return res

        def obj2point(obj):
            return curve.point(obj[0], obj[1], red)

        pre = obj[2]
        res.precomputed = {
            beta: None,
            doubles: pre.doubles and {
                step: pre.doubles.step,
                points: [res].concat(pre.doubles.points.map(obj2point))
            },
            naf: pre.naf and {
                wnd: pre.naf.wnd,
                points: [res].concat(pre.naf.points.map(obj2point))
            }
        }
        return res

    def inspect(self):
        if (self.isInfinity()):
            return '<EC Point Infinity>'
        return '<EC Point x: ' + self.x.fromRed().toString(16, 2) + \
            ' y: ' + self.y.fromRed().toString(16, 2) + '>'

    def isInfinity(self):
        return self.inf

    def add(self, p):
        # O + P = P
        if (self.inf):
            return p

        # P + O = P
        if (p.inf):
            return self
        
        # P + P = 2P
        if (self.eq(p)):
            return self.dbl()
        
        # P + (-P) = O
        if (self.neg().eq(p)):
            return self.curve.point(None, None)
        
        # P + Q = O
        if (self.x.cmp(p.x) == 0):
            return self.curve.point(None, None)
        
        c = self.y.redSub(p.y)
        if (c.cmpn(0) != 0):
            c = c.redMul(self.x.redSub(p.x).redInvm())
        nx = c.redSqr().redISub(self.x).redISub(p.x)
        ny = c.redMul(self.x.redSub(nx)).redISub(self.y)
        return self.curve.point(nx, ny)

    def dbl(self):
        if (self.inf):
            return self

        # 2P = O
        ys1 = self.y.redAdd(self.y)
        if (ys1.cmpn(0) == 0):
            return self.curve.point(None, None)

        a = self.curve.a

        x2 = self.x.redSqr()
        dyinv = ys1.redInvm()
        c = x2.redAdd(x2).redIAdd(x2).redIAdd(a).redMul(dyinv)

        nx = c.redSqr().redISub(self.x.redAdd(self.x))
        ny = c.redMul(self.x.redSub(nx)).redISub(self.y)
        return self.curve.point(nx, ny)

    def getX(self):
        return self.x.fromRed()

    def getY(self):
        return self.y.fromRed()

    def mul(k):
        k = BN(k, 16)

        if (self._hasDoubles(k)):
            return self.curve._fixedNafMul(self, k)
        elif (self.curve.endo):
            return self.curve._endoWnafMulAdd([self], [k])
        else:
            return self.curve._wnafMul(self, k)

    def mulAdd(self, k1, p2, k2):
        points = [self, p2]
        coeffs = [k1, k2]
        if (self.curve.endo):
            return self.curve._endoWnafMulAdd(points, coeffs)
        else:
            return self.curve._wnafMulAdd(1, points, coeffs, 2)

    def jmulAdd(self, k1, p2, k2):
        points = [self, p2]
        coeffs = [k1, k2]
        if (self.curve.endo):
            return self.curve._endoWnafMulAdd(points, coeffs, True)
        else:
            return self.curve._wnafMulAdd(1, points, coeffs, 2, True)

    def eq(self, p):
        return self == p or self.inf == p.inf and \
            (self.inf or self.x.cmp(p.x) == 0 and self.y.cmp(p.y) == 0)

    def negate(p):
        return p.neg()

    def neg(self, _precompute):
        if (self.inf):
            return self

        res = self.curve.point(self.x, self.y.redNeg())
        if (_precompute and self.precomputed):
            pre = self.precomputed

            res.precomputed = {
                naf: pre.naf and {
                    wnd: pre.naf.wnd,
                    points: map(negate, pre.naf.points)
                },
            doubles: pre.doubles and {
                step: pre.doubles.step,
                points: map(negate, pre.doubles.points)
                }
            }
        return res

    def toJ(self):
        if (self.inf):
            return self.curve.jpoint(None, None, None)

        res = self.curve.jpoint(self.x, self.y, self.curve.one)
        return res

class JPoint(BasePoint):
    def __init__(self, curve, x, y, z):
        super().__init__(self, curve, 'jacobian')
        if (x == None and y == None and z == None):
            self.x = self.curve.one
            self.y = self.curve.one
            self.z = BN(0)
        else:
            self.x = BN(x, 16)
            self.y = BN(y, 16)
            self.z = BN(z, 16)
        if (not self.x.red):
            self.x = self.x.toRed(self.curve.red)
        if (not self.y.red):
            self.y = self.y.toRed(self.curve.red)
        if (not self.z.red):
            self.z = self.z.toRed(self.curve.red)

        self.zOne = self.z == self.curve.one

    def jpoint(self, x, y, z):
        return JPoint(self, x, y, z)

    def toP(self):
        if (self.isInfinity()):
            return self.curve.point(None, None)

        zinv = self.z.redInvm()
        zinv2 = zinv.redSqr()
        ax = self.x.redMul(zinv2)
        ay = self.y.redMul(zinv2).redMul(zinv)

        return self.curve.point(ax, ay)

    def neg(self):
        return self.curve.jpoint(self.x, self.y.redNeg(), self.z)

    def add(self, p):
        # O + P = P
        if (self.isInfinity()):
            return p

        # P + O = P
        if (p.isInfinity()):
            return self

        # 12M + 4S + 7A
        pz2 = p.z.redSqr()
        z2 = self.z.redSqr()
        u1 = self.x.redMul(pz2)
        u2 = p.x.redMul(z2)
        s1 = self.y.redMul(pz2.redMul(p.z))
        s2 = p.y.redMul(z2.redMul(self.z))

        h = u1.redSub(u2)
        r = s1.redSub(s2)
        if (h.cmpn(0) == 0):
            if (r.cmpn(0) != 0):
                return self.curve.jpoint(None, None, None)
            else:
                return self.dbl()

        h2 = h.redSqr()
        h3 = h2.redMul(h)
        v = u1.redMul(h2)

        nx = r.redSqr().redIAdd(h3).redISub(v).redISub(v)
        ny = r.redMul(v.redISub(nx)).redISub(s1.redMul(h3))
        nz = self.z.redMul(p.z).redMul(h)

        return self.curve.jpoint(nx, ny, nz)

    def mixedAdd(self, p):
        # O + P = P
        if (self.isInfinity()):
            return p.toJ()

        # P + O = P
        if (p.isInfinity()):
            return self

            # 8M + 3S + 7A
        z2 = self.z.redSqr()
        u1 = self.x
        u2 = p.x.redMul(z2)
        s1 = self.y
        s2 = p.y.redMul(z2).redMul(self.z)

        h = u1.redSub(u2)
        r = s1.redSub(s2)
        if (h.cmpn(0) == 0):
            if (r.cmpn(0) != 0):
                return self.curve.jpoint(None, None, None)
            else:
                return self.dbl()

        h2 = h.redSqr()
        h3 = h2.redMul(h)
        v = u1.redMul(h2)

        nx = r.redSqr().redIAdd(h3).redISub(v).redISub(v)
        ny = r.redMul(v.redISub(nx)).redISub(s1.redMul(h3))
        nz = self.z.redMul(h)

        return self.curve.jpoint(nx, ny, nz)

    def dblp(self, pow):
        if (pow == 0):
            return self
        if (self.isInfinity()):
            return self
        if (not pow):
            return self.dbl()

        if (self.curve.zeroA or self.curve.threeA):
            r = self
            i = 0
            while i < pow:
                r = r.dbl()
                i += 1
            return r

        # 1M + 2S + 1A + N * (4S + 5M + 8A)
        # N = 1 => 6M + 6S + 9A
        a = self.curve.a
        tinv = self.curve.tinv

        jx = self.x
        jy = self.y
        jz = self.z
        jz4 = jz.redSqr().redSqr()

        # Reuse results
        jyd = jy.redAdd(jy)
        i = 0
        while i < pow:
            jx2 = jx.redSqr()
            jyd2 = jyd.redSqr()
            jyd4 = jyd2.redSqr()
            c = jx2.redAdd(jx2).redIAdd(jx2).redIAdd(a.redMul(jz4))

            t1 = jx.redMul(jyd2)
            nx = c.redSqr().redISub(t1.redAdd(t1))
            t2 = t1.redISub(nx)
            dny = c.redMul(t2)
            dny = dny.redIAdd(dny).redISub(jyd4)
            nz = jyd.redMul(jz)
            if (i + 1 < pow):
                jz4 = jz4.redMul(jyd4)

            jx = nx
            jz = nz
            jyd = dny
            i += 1

        return self.curve.jpoint(jx, jyd.redMul(tinv), jz)

    def dbl(self):
        if (self.isInfinity()):
            return self

        if (self.curve.zeroA):
            return self._zeroDbl()
        elif (self.curve.threeA):
            return self._threeDbl()
        else:
            return self._dbl()

    def _zeroDbl(self):
        # Z = 1
        if (self.zOne):
            # hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html
            #     #doubling-mdbl-2007-bl
            # 1M + 5S + 14A

            # XX = X1^2
            xx = self.x.redSqr()
            # YY = Y1^2
            yy = self.y.redSqr()
            # YYYY = YY^2
            yyyy = yy.redSqr()
            # S = 2 * ((X1 + YY)^2 - XX - YYYY)
            s = self.x.redAdd(yy).redSqr().redISub(xx).redISub(yyyy)
            s = s.redIAdd(s)
            # M = 3 * XX + a a = 0
            m = xx.redAdd(xx).redIAdd(xx)
            # T = M ^ 2 - 2*S
            t = m.redSqr().redISub(s).redISub(s)

            # 8 * YYYY
            yyyy8 = yyyy.redIAdd(yyyy)
            yyyy8 = yyyy8.redIAdd(yyyy8)
            yyyy8 = yyyy8.redIAdd(yyyy8)

            # X3 = T
            nx = t
            # Y3 = M * (S - T) - 8 * YYYY
            ny = m.redMul(s.redISub(t)).redISub(yyyy8)
            # Z3 = 2*Y1
            nz = self.y.redAdd(self.y)
        else:
            # hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html
            #     #doubling-dbl-2009-l
            # 2M + 5S + 13A

            # A = X1^2
            a = self.x.redSqr()
            # B = Y1^2
            b = self.y.redSqr()
            # C = B^2
            c = b.redSqr()
            # D = 2 * ((X1 + B)^2 - A - C)
            d = self.x.redAdd(b).redSqr().redISub(a).redISub(c)
            d = d.redIAdd(d)
            # E = 3 * A
            e = a.redAdd(a).redIAdd(a)
            # F = E^2
            f = e.redSqr()

            # 8 * C
            c8 = c.redIAdd(c)
            c8 = c8.redIAdd(c8)
            c8 = c8.redIAdd(c8)

            # X3 = F - 2 * D
            nx = f.redISub(d).redISub(d)
            # Y3 = E * (D - X3) - 8 * C
            ny = e.redMul(d.redISub(nx)).redISub(c8)
            # Z3 = 2 * Y1 * Z1
            nz = self.y.redMul(self.z)
            nz = nz.redIAdd(nz)

        return self.curve.jpoint(nx, ny, nz)

    def _threeDbl(self):
        # Z = 1
        if (self.zOne):
            # hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-3.html
            #     #doubling-mdbl-2007-bl
            # 1M + 5S + 15A

            # XX = X1^2
            xx = self.x.redSqr()
            # YY = Y1^2
            yy = self.y.redSqr()
            # YYYY = YY^2
            yyyy = yy.redSqr()
            # S = 2 * ((X1 + YY)^2 - XX - YYYY)
            s = self.x.redAdd(yy).redSqr().redISub(xx).redISub(yyyy)
            s = s.redIAdd(s)
            # M = 3 * XX + a
            m = xx.redAdd(xx).redIAdd(xx).redIAdd(self.curve.a)
            # T = M^2 - 2 * S
            t = m.redSqr().redISub(s).redISub(s)
            # X3 = T
            nx = t
            # Y3 = M * (S - T) - 8 * YYYY
            yyyy8 = yyyy.redIAdd(yyyy)
            yyyy8 = yyyy8.redIAdd(yyyy8)
            yyyy8 = yyyy8.redIAdd(yyyy8)
            ny = m.redMul(s.redISub(t)).redISub(yyyy8)
            # Z3 = 2 * Y1
            nz = self.y.redAdd(self.y)
        else:
            # hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-3.html#doubling-dbl-2001-b
            # 3M + 5S

            # delta = Z1^2
            delta = self.z.redSqr()
            # gamma = Y1^2
            gamma = self.y.redSqr()
            # beta = X1 * gamma
            beta = self.x.redMul(gamma)
            # alpha = 3 * (X1 - delta) * (X1 + delta)
            alpha = self.x.redSub(delta).redMul(self.x.redAdd(delta))
            alpha = alpha.redAdd(alpha).redIAdd(alpha)
            # X3 = alpha^2 - 8 * beta
            beta4 = beta.redIAdd(beta)
            beta4 = beta4.redIAdd(beta4)
            beta8 = beta4.redAdd(beta4)
            nx = alpha.redSqr().redISub(beta8)
            # Z3 = (Y1 + Z1)^2 - gamma - delta
            nz = self.y.redAdd(self.z).redSqr().redISub(gamma).redISub(delta)
            # Y3 = alpha * (4 * beta - X3) - 8 * gamma^2
            ggamma8 = gamma.redSqr()
            ggamma8 = ggamma8.redIAdd(ggamma8)
            ggamma8 = ggamma8.redIAdd(ggamma8)
            ggamma8 = ggamma8.redIAdd(ggamma8)
            ny = alpha.redMul(beta4.redISub(nx)).redISub(ggamma8)

        return self.curve.jpoint(nx, ny, nz)

    def _dbl(self):
        a = self.curve.a

        # 4M + 6S + 10A
        jx = self.x
        jy = self.y
        jz = self.z
        jz4 = jz.redSqr().redSqr()

        jx2 = jx.redSqr()
        jy2 = jy.redSqr()

        c = jx2.redAdd(jx2).redIAdd(jx2).redIAdd(a.redMul(jz4))

        jxd4 = jx.redAdd(jx)
        jxd4 = jxd4.redIAdd(jxd4)
        t1 = jxd4.redMul(jy2)
        nx = c.redSqr().redISub(t1.redAdd(t1))
        t2 = t1.redISub(nx)

        jyd8 = jy2.redSqr()
        jyd8 = jyd8.redIAdd(jyd8)
        jyd8 = jyd8.redIAdd(jyd8)
        jyd8 = jyd8.redIAdd(jyd8)
        ny = c.redMul(t2).redISub(jyd8)
        nz = jy.redAdd(jy).redMul(jz)

        return self.curve.jpoint(nx, ny, nz)

    def trpl(self):
        if (not self.curve.zeroA):
            return self.dbl().add(self)

        # hyperelliptic.org/EFD/g1p/auto-shortw-jacobian-0.html#tripling-tpl-2007-bl
        # 5M + 10S + ...

        # XX = X1^2
        xx = self.x.redSqr()
        # YY = Y1^2
        yy = self.y.redSqr()
        # ZZ = Z1^2
        zz = self.z.redSqr()
        # YYYY = YY^2
        yyyy = yy.redSqr()
        # M = 3 * XX + a * ZZ2 a = 0
        m = xx.redAdd(xx).redIAdd(xx)
        # MM = M^2
        mm = m.redSqr()
        # E = 6 * ((X1 + YY)^2 - XX - YYYY) - MM
        e = self.x.redAdd(yy).redSqr().redISub(xx).redISub(yyyy)
        e = e.redIAdd(e)
        e = e.redAdd(e).redIAdd(e)
        e = e.redISub(mm)
        # EE = E^2
        ee = e.redSqr()
        # T = 16*YYYY
        t = yyyy.redIAdd(yyyy)
        t = t.redIAdd(t)
        t = t.redIAdd(t)
        t = t.redIAdd(t)
        # U = (M + E)^2 - MM - EE - T
        u = m.redIAdd(e).redSqr().redISub(mm).redISub(ee).redISub(t)
        # X3 = 4 * (X1 * EE - 4 * YY * U)
        yyu4 = yy.redMul(u)
        yyu4 = yyu4.redIAdd(yyu4)
        yyu4 = yyu4.redIAdd(yyu4)
        nx = self.x.redMul(ee).redISub(yyu4)
        nx = nx.redIAdd(nx)
        nx = nx.redIAdd(nx)
        # Y3 = 8 * Y1 * (U * (T - U) - E * EE)
        ny = self.y.redMul(u.redMul(t.redISub(u)).redISub(e.redMul(ee)))
        ny = ny.redIAdd(ny)
        ny = ny.redIAdd(ny)
        ny = ny.redIAdd(ny)
        # Z3 = (Z1 + E)^2 - ZZ - EE
        nz = self.z.redAdd(e).redSqr().redISub(zz).redISub(ee)

        return self.curve.jpoint(nx, ny, nz)

    def mul(self, k, kbase):
        k = BN(k, kbase)
        return self.curve._wnafMul(self, k)

    def eq(p):
        if (p.type == 'affine'):
            return self.eq(p.toJ())

        if (self == p):
            return True

        # x1 * z2^2 == x2 * z1^2
        z2 = self.z.redSqr()
        pz2 = p.z.redSqr()
        if (self.x.redMul(pz2).redISub(p.x.redMul(z2)).cmpn(0) != 0):
            return False

        # y1 * z2^3 == y2 * z1^3
        z3 = z2.redMul(self.z)
        pz3 = pz2.redMul(p.z)
        return self.y.redMul(pz3).redISub(p.y.redMul(z3)).cmpn(0) == 0

    def eqXToP(self, x):
        zs = self.z.redSqr()
        rx = x.toRed(self.curve.red).redMul(zs)
        if (self.x.cmp(rx) == 0):
            return True

        xc = x.clone()
        t = self.curve.redN.redMul(zs)
        while True:
            xc.iadd(self.curve.n)
            if (xc.cmp(self.curve.p) >= 0):
                return False

            rx.redIAdd(t)
            if (self.x.cmp(rx) == 0):
                return True

        return False

    def inspect(self):
        if (self.isInfinity()):
            return '<EC JPoint Infinity>'
        return '<EC JPoint x: ' + self.x.toString(16, 2) + \
        ' y: ' + self.y.toString(16, 2) + \
        ' z: ' + self.z.toString(16, 2) + '>'

    def isInfinity(self):
        # XXX self code assumes that zero is always zero in red
        return self.z.cmpn(0) == 0
