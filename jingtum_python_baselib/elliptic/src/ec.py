# BN = ('bn.js')
# HmacDRBG = ('hmac-drbg')
# elliptic = ('../../elliptic')
from . import utils

KeyPair = ('./key')
Signature = ('./signature')

class EC:
    def __init__(self, options):
        if not isinstance(self, EC):
            return EC(options)

        # Shortcut `elliptic.ec(curve-name)`
        if isinstance(options, str):
            assert self.curves.hasOwnProperty(options), 'Unknown curve ' + options
            options = self.curves[options]

        # Shortcut for `elliptic.ec(elliptic.curves.curveName)`
        if isinstance(options, self.curves.PresetCurve):
            options = {'curve': options}

        self.curve = options.curve.curve
        self.n = self.curve.n
        self.nh = self.n.ushrn(1)
        self.g = self.curve.g

        # Point on curve
        self.g = options.curve.g
        self.g.precompute(options.curve.n.bitLength() + 1)

        # Hash for function for DRBG
        self.hash = options.hash or options.curve.hash

    def keyPair(self, options):
        return KeyPair(self, options)

    def keyFromPrivate(self, priv, enc):
        return KeyPair.fromPrivate(self, priv, enc)

    def keyFromPublic(self, pub, enc):
        return KeyPair.fromPublic(self, pub, enc)

    def genKeyPair(self, options):
        if (not options):
            options = {}

        # Instantiate Hmac_DRBG
        drbg = HmacDRBG({
            'hash': self.hash,
            'pers': options.pers,
            'persEnc': options.persEnc or 'utf8',
            'entropy': options.entropy or self.rand(self.hash.hmacStrength),
            'entropyEnc': options.entropy and options.entropyEnc or 'utf8',
            'nonce': self.n.toArray()
        })

        bytes = self.n.byteLength()
        ns2 = self.n.sub(BN(2))
        while True:
            priv = BN(drbg.generate(bytes))
            if (priv.cmp(ns2) > 0):
                continue

            priv.iaddn(1)
            return self.keyFromPrivate(priv)

    def _truncateToN(self, msg, truncOnly):
        delta = msg.byteLength() * 8 - self.n.bitLength()
        if (delta > 0):
            msg = msg.ushrn(delta)
        if (not truncOnly and msg.cmp(self.n) >= 0):
            return msg.sub(self.n)
        else:
            return msg

    def sign(self, msg, key, enc, options):
        if enc:
            options = enc
            enc = None
        if (not options):
            options = {}

        key = self.keyFromPrivate(key, enc)
        msg = self._truncateToN(BN(msg, 16))

        # Zero-extend key to provide enough entropy
        bytes = self.n.byteLength()
        bkey = key.getPrivate().toArray('be', bytes)

        # Zero-extend nonce to have the same byte size as N
        nonce = msg.toArray('be', bytes)

        # Instantiate Hmac_DRBG
        drbg = HmacDRBG({
            'hash': self.hash,
            'entropy': bkey,
            'nonce': nonce,
            'pers': options.pers,
            'persEnc': options.persEnc or 'utf8'
        })

        # Number of bytes to generate
        ns1 = self.n.sub(BN(1))

        iter = 0
        while True:
            if options.k:
                k = options.k(iter)
            else:
                k = BN(drbg.generate(self.n.byteLength()))
            k = self._truncateToN(k, True)
            if (k.cmpn(1) <= 0 or k.cmp(ns1) >= 0):
                continue

            kp = self.g.mul(k)
            if (kp.isInfinity()):
                continue

            kpX = kp.getX()
            r = kpX.umod(self.n)
            if (r.cmpn(0) == 0):
                continue

            s = k.invm(self.n).mul(r.mul(key.getPrivate()).iadd(msg))
            s = s.umod(self.n)
            if (s.cmpn(0) == 0):
                continue

            if kp.getY().isOdd():
                r1 = 1
            else:
                r1 = 0
            if kpX.cmp(r) != 0:
                r1 = 2
            else:
                r2 = 0
            recoveryParam = r1 |r2

            # Use complement of `s`, if it is > `n / 2`
            if (options.canonical and s.cmp(self.nh) > 0):
                s = self.n.sub(s)
                recoveryParam ^= 1

            return self.Signature({'r': r, 's': s, 'recoveryParam': recoveryParam})
            iter += 1


def verify(self, msg, signature, key, enc):
    msg = self._truncateToN(BN(msg, 16))
    key = self.keyFromPublic(key, enc)
    signature = self.Signature(signature, 'hex')

    # Perform primitive values validation
    r = signature.r
    s = signature.s
    if (r.cmpn(1) < 0 or r.cmp(self.n) >= 0):
        return False
    if (s.cmpn(1) < 0 or s.cmp(self.n) >= 0):
        return False

    # Validate signature
    sinv = s.invm(self.n)
    u1 = sinv.mul(msg).umod(self.n)
    u2 = sinv.mul(r).umod(self.n)

    if (not self.curve._maxwellTrick):
        p = self.g.mulAdd(u1, key.getPublic(), u2)
    if (p.isInfinity()):
        return False

    return p.getX().umod(self.n).cmp(r) == 0

    # NOTE: Greg Maxwell's trick, inspired by:
    # https:#git.io/vad3K

    p = self.g.jmulAdd(u1, key.getPublic(), u2)
    if (p.isInfinity()):
        return False

    # Compare `p.x` of Jacobian point with `r`,
    # self will do `p.x == r * p.z^2` instead of multiplying `p.x` by the
    # inverse of `p.z^2`
    return p.eqXToP(r)


def recoverPubKey(self, msg, signature, j, enc):
    assert (3 & j) == j, 'The recovery param is more than two bits'
    signature = self.Signature(signature, enc)

    n = self.n
    e = BN(msg)
    r = signature.r
    s = signature.s

    # A set LSB signifies that the y-coordinate is odd
    isYOdd = j & 1
    isSecondKey = j >> 1
    if (r.cmp(self.curve.p.umod(self.curve.n)) >= 0 and isSecondKey):
        raise Exception('Unable to find sencond key candinate')

    # 1.1. Let x = r + jn.
    if (isSecondKey):
        r = self.curve.pointFromX(r.add(self.curve.n), isYOdd)
    else:
        r = self.curve.pointFromX(r, isYOdd)

    rInv = signature.r.invm(n)
    s1 = n.sub(e).mul(rInv).umod(n)
    s2 = s.mul(rInv).umod(n)

    # 1.6.1 Compute Q = r^-1 (sR -  eG)
    #               Q = r^-1 (sR + -eG)
    return self.g.mulAdd(s1, r, s2)


    def getKeyRecoveryParam(self, e, signature, Q, enc):
        signature = self.Signature(signature, enc)
        if (signature.recoveryParam != None):
            return signature.recoveryParam

        i = 0
        while i < 4:
            Qprime
            try:
                Qprime = self.recoverPubKey(e, signature, i)
            except (e):
                continue

            if (Qprime.eq(Q)):
                return i
            i += 1

        raise Exception('Unable to find valid recovery factor')
