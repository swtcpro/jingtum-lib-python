# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 钱包依赖的模块
"""
import binascii
import six
from hashlib import sha256

def bytesToHex(srcinfo):
    # srcinfo is a array
    return ''.join(["%02X" % x for x in srcinfo]).strip()

def hexToBytes(srcinfo):
    assert (len(srcinfo) % 2 == 0)
    # return BN(srcinfo, 16).toArray(null, len(srcinfo) / 2)
    i = 0
    dst = []
    while i < len(srcinfo):
        k = str(srcinfo[i: i + 2])
        dst.append(int(str(srcinfo[i: i + 2]), 16))
        i += 2
    return dst

def decode_hex(hex_string):
    """Decode a string like "fa4b21" to actual bytes."""
    if six.PY3:
        return bytes.fromhex(hex_string)
    else:
        return hex_string.decode('hex')

def from_bytes(bytes):
    """Reverse of to_bytes()."""
    # binascii works on all versions of Python, the hex encoding does not
    return int(binascii.hexlify(bytes), 16)

def to_bytes(number, length=None, endianess='big'):
    """Will take an integer and serialize it to a string of bytes.
    Python 3 has this, this is originally a backport to Python 2, from:
        http://stackoverflow.com/a/16022710/15677
    We use it for Python 3 as well, because Python 3's builtin version
    needs to be given an explicit length, which means our base decoder
    API would have to ask for an explicit length, which just isn't as nice.
    Alternative implementation here:
       https://github.com/nederhoed/python-bitcoinaddress/blob/c3db56f0a2d4b2a069198e2db22b7f607158518c/bitcoinaddress/__init__.py#L26
    """
    h = '%x' % number
    s = ('0'*(len(h) % 2) + h)
    if length:
        if len(s) > length*2:
            raise ValueError('number of large for {} bytes'.format(length))
        s = s.zfill(length*2)
    s = decode_hex(s)
    return s if endianess == 'big' else s[::-1]

def fmt_hex(bytes):
    """Format the bytes as a hex string, return upper-case version.
    """
    # This is a separate function so as to not make the mistake of
    # using the '%X' format string with an ints, which will not
    # guarantee an even-length string.
    #
    # binascii works on all versions of Python, the hex encoding does not.
    hex = binascii.hexlify(bytes)
    hex = hex.decode()  # Returns bytes, which makes no sense to me
    return hex.upper()

class JingtumBaseDecoder():
    def __init__(self):
        pass

    """Decodes Jingtum's base58 alphabet.
    """
    alphabet = 'jpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65rkm8oFqi1tuvAxyz'

    @classmethod
    def decode(cls, *a, **kw):
        """Apply base58 decode, verify checksum, return payload.
        """
        decoded = cls.decode_base(*a, **kw)
        assert cls.verify_checksum(decoded)
        payload = decoded[:-4] # remove the checksum
        payload = payload[1:]  # remove first byte, a version number
        return payload

    @classmethod
    def decode_base(cls, encoded, pad_length=None):
        """Decode a base encoded string with the Jingtum alphabet."""
        n = 0
        base = len(cls.alphabet)
        for char in encoded:
            n = n * base + cls.alphabet.index(char)
        return to_bytes(n, pad_length, 'big')

    @classmethod
    def verify_checksum(cls, bytes):
        """
        """
        valid = bytes[-4:] == sha256(sha256((bytes[:-4])).digest()).digest()[:4]
        return valid

    @staticmethod
    def as_ints(bytes):
        return list([ord(c) for c in bytes])

    @classmethod
    def encode(cls, data):
        """Apply base58 encode including version, checksum."""
        version = b'\x00'
        bytes = version + data
        bytes += sha256(sha256(bytes).digest()).digest()[:4]   # checksum
        return cls.encode_base(bytes)

    @classmethod
    def encode_base(cls, data):
        # https://github.com/jgarzik/python-bitcoinlib/blob/master/bitcoin/base58.py
        # Convert big-endian bytes to integer
        n = int(binascii.hexlify(data).decode('utf8'), 16)

        # Divide that integer into base58
        res = []
        while n > 0:
            n, r = divmod(n, len(cls.alphabet))
            res.append(cls.alphabet[r])
        res = ''.join(res[::-1])

        # Encode leading zeros as base58 zeros
        czero = 0 if six.PY3 else b'\x00'
        pad = 0
        for c in data:
            if c == czero:
                pad += 1
            else:
                break
        return cls.alphabet[0] * pad + res
