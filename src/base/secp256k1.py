"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/7/5
 * Time: 16:09
 * Description:
"""
# from ecdsa import SECP256k1 as ec
# from src.base.sha512 import *
#
#
# def scalarMultiple(bytes, discrim):
#     order = ec.curve.n
#     for i in range(0, 0xFFFFFFFF):
#         # We hash the bytes to find a 256 bit number, looping until we are sure it
#         # is less than the order of the curve.
#         hasher = Sha512().add(bytes)
#         # If the optional discriminator index was passed in, update the hash.
#         if discrim:
#             hasher.addU32(discrim)
#         hasher.addU32(i)
#         key = hasher.first256BN()
#         if key.cmp(0) > 0 and key.cmp(order) < 0:
#             return key
#
#     raise Exception('impossible space search)')
