'use strict'

#BN = require('bn.js')
#utils = elliptic.utils

class KeyPair:
    def __init__(self, ec, options):
        self.ec = ec
        self.priv = None
        self.pub = None

        # KeyPair(ec, { priv: ..., pub: ... })
        if (options.priv):
            self._importPrivate(options.priv, options.privEnc)
        if (options.pub):
            self._importPublic(options.pub, options.pubEnc)

    def fromPublic(ec, pub, enc):
        if isinstance(pub, KeyPair):
            return pub

        return KeyPair(ec, {
            'pub': pub,
            'pubEnc': enc
        })

    def fromPrivate(ec, priv, enc):
        if isinstance(priv, KeyPair):
            return priv
        
        return KeyPair(ec, {
            'priv': priv,
            'privEnc': enc
        })

def validate(self):
    pub = self.getPublic()
    if (pub.isInfinity()):
        return {'result': False, 'reason': 'Invalid public key'}
    if (not pub.validate()):
        return {'result': False, 'reason': 'Public key is not a point'}
    if (not pub.mul(self.ec.curve.n).isInfinity()):
        return {'result': False, 'reason': 'Public key * N not = O'}
    
    return {'result': True, 'reason': None}

def getPublic(self, compact, enc):
    # compact is optional argument
    if isinstance(compact, str):
        enc = compact
        compact = None

    if (not self.pub):
        self.pub = self.ec.g.mul(self.priv)

    if (not enc):
        return self.pub

    return self.pub.encode(enc, compact)

def getPrivate(self, enc):
    if (enc == 'hex'):
        return self.priv.toString(16, 2)
    else:
        return self.priv

def _importPrivate(self, key, enc):
    self.priv = BN(key, enc or 16)
    # Ensure that the priv won't be bigger than n, otherwise we may fail
    # in fixed multiplication method
    self.priv = self.priv.umod(self.ec.curve.n)

def _importPublic(self, key, enc):
    if (key.x or key.y):
        # Montgomery points only have an `x` coordinate.
        # Weierstrass/Edwards points on the other hand have both `x` and
        # `y` coordinates.
        if (self.ec.curve.type == 'mont'):
            assert key.x, 'Need x coordinate'
        elif (self.ec.curve.type == 'short' or
        self.ec.curve.type == 'edwards'):
            assert key.x and key.y, 'Need both x and y coordinate'
        self.pub = self.ec.curve.point(key.x, key.y)
        return
    self.pub = self.ec.curve.decodePoint(key, enc)

def derive(self, pub):
    return pub.mul(self.priv).getX()

def sign(self, msg, enc, options):
    return self.ec.sign(msg, self, enc, options)

def verify(self, msg, signature):
    return self.ec.verify(msg, signature, self)

def inspect(self):
    return '<Key priv: ' + (self.priv and self.priv.toString(16, 2)) + \
    ' pub: ' + (self.pub and self.pub.inspect()) + ' >'
