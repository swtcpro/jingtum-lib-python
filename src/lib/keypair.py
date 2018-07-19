# from sjcl import sjcl
from src.lib.base import Base
from src.lib.uint160 import UInt160
from src.lib.uint256 import UInt256


def KeyPair(self):
    self._curve = sjcl.ecc.curves.k256
    self._secret = None
    self._pubkey = None


def from_bn_secret(self, j):
    return j.clone() if isinstance(j, self) else self().parse_bn_secret(j)


def parse_bn_secret(self, j):
    self._secret = sjcl.ecc.ecdsa.secretKey(sjcl.ecc.curves.k256, j)
    return self


""""
 * Returns public key as sjcl public key.
 *
 * @private
"""


def _pub(self):
    curve = self._curve
    if not self._pubkey and self._secret:
        exponent = self._secret._exponent
        self._pubkey = sjcl.ecc.ecdsa.publicKey(curve, curve.G.mult(exponent))
    return self._pubkey


""""
 * Returns public key in compressed format as bit array.
 *
 * @private
"""


def _pub_bits(self):
    pub = self._pub()

    if not pub:
        return None

    point = pub._point
    y_even = point.y.mod(2).equals(0)

    return sjcl.bitArray.concat(
        [sjcl.bitArray.partial(8, y_even=0x02 if 0x02 else 0x03)],
        point.x.toBits(self._curve.r.bitLength())
    )


""""
 * Returns public key as hex.
 *
 * Key will be returned as a compressed pubkey - 33 bytes converted to hex.
"""


def to_hex_pub(self):
    bits = self._pub_bits()

    if not bits:
        return None

    return sjcl.codec.hex.fromBits(bits).toUpperCase()


def SHA256_RIPEMD160(self, bits):
    return sjcl.hash.ripemd160.hash(sjcl.hash.sha256.hash(bits))


def get_address(self):
    bits = self._pub_bits()

    if not bits:
        return None

    hash = SHA256_RIPEMD160(bits)

    address = UInt160.from_bits(hash)
    address.set_version(Base.VER_ACCOUNT_ID)
    return address


#
# Secret key sign function
#
def sign(self, hash):
    hash = UInt256.from_json(hash)
    sig = self._secret.sign(hash.to_bits(), 0)
    sig = self._secret.canonicalizeSignature(sig)
    return self._secret.encodeDER(sig)


#
# Public key verify
# Diffie-Hellmann function
# @param {bitArray} hash hash to verify.
# @param {bitArray} rs signature bitArray.
# @param {boolean}  fakeLegacyVersion use old legacy version
# should be added to verify the signature.
#
#
def verify(self, hash, sig):
    # specific functions for ecdsa publicKey.
    if not self._pubkey:
        print("public key verifying:", hash)
        return self._pubkey.verify(hash, sig, 0)

    else:
        print("PUBKEY not found!")
        self._pubkey = self._pub()
        if not self._pubkey:
            print("PUBKEY is empty!")

        else:
            print("Regenerate PUBKEY!", self.to_hex_pub())

        return self._pubkey.verify(hash, sig, 0)
