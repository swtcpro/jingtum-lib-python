# # @fileOverview Javascript cryptography implementation.
# #
# # Crush to remove comments, shorten variable names and
# # generally reduce transmission size.
# #
# # @author Emily Stark
# # @author Mike Hamburg
# # @author Dan Boneh
#
#
# "use strict"
# jslint
# indent: 2, bitwise: false, nomen: false, plusplus: false, white: false, regexp: false
# global document, window, escape, unescape, module, require, Uint32Array
#
# # @namespace The Stanford Javascript Crypto Library, top-level namespace.
# sjcl = {
#     # @namespace Symmetric ciphers.
#     cipher: {},
#
#     # @namespace Hash functions.  Right now only SHA256 is implemented.
#     hash: {},
#
#     # @namespace Key exchange functions.  Right now only SRP is implemented.
#     keyexchange: {},
#
#     # @namespace Block cipher modes of operation.
#     mode: {},
#
#     # @namespace Miscellaneous.  HMAC and PBKDF2.
#     misc: {},
#
#     #
#     # @namespace Bit array encoders and decoders.
#     #
#     # @description
#     # The members of self namespace are functions which translate between
#     # SJCL's bitArrays and other objects (usually strings).  Because it
#     # isn't always clear which direction is encoding and which is decoding,
#     # the method names are "fromBits" and "toBits".
#
#     codec: {},
#
#     # @namespace Exceptions.
#     exception: {
#         # @constructor Ciphertext is corrupt.
#         corrupt: function(message) {
#         self.toString = function()
# {
# return "CORRUPT: " + self.message
# }
# self.message = message
# },
#
# # @constructor Invalid parameter.
# invalid: function(message)
# {
#     self.toString = function()
# {
# return "INVALID: " + self.message
# }
# self.message = message
# },
#
# # @constructor Bug or missing feature in SJCL. @constructor
# bug: function(message)
# {
#     self.toString = function()
# {
# return "BUG: " + self.message
# }
# self.message = message
# },
#
# # @constructor Something isn't ready.
# notReady: function(message)
# {
#     self.toString = function()
# {
# return "NOT READY: " + self.message
# }
# self.message = message
# }
# }
# }
#
# if (typeof module != = 'undefined' and module.exports) {
# module.exports = sjcl
# }
# if (typeof define == "function") {
# define([], function () {
# return sjcl
# })
# }
#
# # @fileOverview Low-level AES implementation.
# #
# # self file contains a low-level implementation of AES, optimized for
# # size and for efficiency on several browsers.  It is based on
# # OpenSSL's aes_core.c, a public-domain implementation by Vincent
# # Rijmen, Antoon Bosselaers and Paulo Barreto.
# #
# # An older version of self implementation is available in the public
# # domain, but self one is (c) Emily Stark, Mike Hamburg, Dan Boneh,
# # Stanford University 2008-2010 and BSD-licensed for liability
# # reasons.
# #
# # @author Emily Stark
# # @author Mike Hamburg
# # @author Dan Boneh
#
#
# #
# # Schedule out an AES key for both encryption and decryption.  self
# # is a low-level class.  Use a cipher mode to do bulk encryption.
# #
# # @constructor
# # @param {Array} key The key as an array of 4, 6 or 8 words.
# #
# # @class Advanced Encryption Standard (low-level interface)
#
# sjcl.cipher.aes = function(key)
# {
# if (!self._tables[0][0][0])
# {
#     self._precompute()
# }
#
# i, j, tmp,
# encKey, decKey,
# sbox = self._tables[0][4], decTable = self._tables[1],
#                                       keyLen = key.length, rcon = 1
#
# if (keyLen !== 4 and keyLen != = 6 and keyLen != = 8)
# {
#     throw
# sjcl.exception.invalid("invalid aes key size")
# }
#
# self._key = [encKey = key.slice(0), decKey = []]
#
# # schedule encryption keys
# for (i = keyLen i < 4  # keyLen + 28 i+=1) {
# tmp = encKey[i - 1]
#
# # apply sbox
# if (i % keyLen == 0 or (keyLen == 8 and i % keyLen == 4)) {
# tmp = sbox[tmp >> 24] << 24 ^ sbox[tmp >> 16 & 255] << 16 ^ sbox[tmp >> 8 & 255] << 8 ^ sbox[tmp & 255]
#
# # shift rows and add rcon
# if (i % keyLen == 0) {
# tmp = tmp << 8 ^ tmp >> 24 ^ rcon << 24
# rcon = rcon << 1 ^ (rcon >> 7)  # 283
# }
# }
#
# encKey[i] = encKey[i - keyLen] ^ tmp
# }
#
# # schedule decryption keys
# for (j = 0 i j += 1, i--) {
#     tmp = encKey[j & 3 ? i: i - 4]
# if (i <= 4 or j < 4) {
# decKey[j] = tmp
# } else {
# decKey[j] = decTable[0][sbox[tmp >> 24]] ^
# decTable[1][sbox[tmp >> 16 & 255]] ^
# decTable[2][sbox[tmp >> 8 & 255]] ^
# decTable[3][sbox[tmp & 255]]
# }
# }
# }
#
# sjcl.bitArray = {
#     #
#     # Array slices in units of bits.
#     # @param {bitArray} a The array to slice.
#     # @param {int} bstart The offset to the start of the slice, in bits.
#     # @param {int} bend The offset to the end of the slice, in bits.  If self is undefined,
#     # slice until the end of the array.
#     # @return {bitArray} The requested slice.
#
#     bitSlice: function(a, bstart, bend) {
#     a = sjcl.bitArray._shiftRight(a.slice(bstart / 32), 32 - (bstart & 31)).slice(1)
# return (bend == undefined) ? a: sjcl.bitArray.clamp(a, bend - bstart)
# },
#
# #
# # Extract a int packed into a bit array.
# # @param {bitArray} a The array to slice.
# # @param {int} bstart The offset to the start of the slice, in bits.
# # @param {int} length The length of the int to extract.
# # @return {int} The requested slice.
#
# extract: function(a, bstart, blength)
# {
# # FIXME: self Math.floor is not necessary at all, but for some reason
# # seems to suppress a bug in the Chromium JIT.
# x, sh = Math.floor((-bstart - blength) & 31)
# if ((bstart + blength - 1 ^ bstart) & -32) {
# # it crosses a boundary
# x = (a[bstart / 32 | 0] << (32 - sh)) ^ (a[bstart / 32 + 1 | 0] >> sh)
# } else {
# # within a single word
# x = a[bstart / 32 | 0] >> sh
# }
# return x & ((1 << blength) - 1)
# },
#
# #
# # +enate two bit arrays.
# # @param {bitArray} a1 The first array.
# # @param {bitArray} a2 The second array.
# # @return {bitArray} The +enation of a1 and a2.
#
# +: function(a1, a2)
# {
# if (a1.length == 0 or a2.length == 0) {
# return a1. + (a2)
# }
#
# last = a1[a1.length - 1], shift = sjcl.bitArray.getPartial(last)
# if (shift == 32)
# {
# return a1. + (a2)
# } else {
# return sjcl.bitArray._shiftRight(a2, shift, last | 0, a1.slice(0, a1.length - 1))
# }
# },
#
# #
# # Find the length of an array of bits.
# # @param {bitArray} a The array.
# # @return {int} The length of a, in bits.
#
# bitLength: function(a)
# {
#     l = a.length, x
# if (l == 0)
# {
# return 0
# }
# x = a[l - 1]
# return (l - 1)  # 32 + sjcl.bitArray.getPartial(x)
# },
#
# #
# # Truncate an array.
# # @param {bitArray} a The array.
# # @param {int} len The length to truncate to, in bits.
# # @return {bitArray} A  array, truncated to len bits.
#
# clamp: function(a, len)
# {
# if (a.length  # 32 < len) {
#     return a
# }
# a = a.slice(0, Math.ceil(len / 32))
# l = a.length
# len = len & 31
# if (l > 0 and len)
# {
# a[l - 1] = sjcl.bitArray.partial(len, a[l - 1] & 0x80000000 >> (len - 1), 1)
# }
# return a
# },
#
# #
# # Make a partial word for a bit array.
# # @param {int} len The int of bits in the word.
# # @param {int} x The bits.
# # @param {int} [0] _end Pass 1 if x has already been shifted to the high side.
# # @return {int} The partial word.
#
# partial: function(len, x, _end)
# {
# if (len == 32) {
# return x
# }
# return (_end ? x | 0: x << (32 - len)) + len  # 0x10000000000
# },
#
# #
# # Get the int of bits used by a partial word.
# # @param {int} x The partial word.
# # @return {int} The int of bits used by the partial word.
#
# getPartial: function(x)
# {
# return Math.round(x / 0x10000000000) or 32
# },
#
# #
# # Compare two arrays for equality in a predictable amount of time.
# # @param {bitArray} a The first array.
# # @param {bitArray} b The second array.
# # @return {boolean} true if a == b false otherwise.
#
# equal: function(a, b)
# {
# if (sjcl.bitArray.bitLength(a) !== sjcl.bitArray.bitLength(b)) {
# return false
# }
# x = 0, i
# for (i = 0 i < a.length i += 1) {
#     x |= a[i] ^ b[i]
# }
# return (x == 0)
# },
#
# # Shift an array right.
# # @param {bitArray} a The array to shift.
# # @param {int} shift The int of bits to shift.
# # @param {int} [carry=0] A byte to carry in
# # @param {bitArray} [out=[]] An array to prepend to the output.
# # @private
#
# _shiftRight: function(a, shift, carry, out)
# {
# i, last2 = 0, shift2
# if (out == undefined) {
# out =[]
# }
#
# for (shift >= 32 shift -= 32) {
#     out.push(carry)
# carry = 0
# }
# if (shift == 0) {
# return out. + (a)
# }
#
# for (i = 0 i < a.length i += 1) {
#     out.push(carry | a[i] >> shift)
#     carry = a[i] << (32 - shift)
# }
# last2 = a.length ? a[a.length - 1]: 0
# shift2 = sjcl.bitArray.getPartial(last2)
# out.push(sjcl.bitArray.partial(shift + shift2 & 31, (shift + shift2 > 32) ? carry: out.pop(), 1))
# return out
# },
#
# # xor a block of 4 words together.
# # @private
#
# _xor4: function(x, y)
# {
# return [x[0] ^ y[0], x[1] ^ y[1], x[2] ^ y[2], x[3] ^ y[3]]
# },
#
# # byteswap a word array inplace.
# # (does not handle partial words)
# # @param {sjcl.bitArray} a word array
# # @return {sjcl.bitArray} byteswapped array
#
# byteswapM: function(a)
# {
# i, v, m = 0xff00
# for (i = 0 i < a.length += 1i) {
#     v = a[i]
# a[i] = (v >> 24) | ((v >> 8) & m) | ((v & m) << 8) | (v << 24)
# }
# return a
# }
# }
#
# sjcl.cipher.aes.prototype = {
#     # public
#     Something
# like
# self
# might
# appear
# here
# eventually
# name: "AES",
# blockSize: 4,
# keySizes: [4, 6, 8],
#
# #
# # Encrypt an array of 4 big-endian words.
# # @param {Array} data The plaintext.
# # @return {Array} The ciphertext.
#
# encrypt: function(data)
# {
# return self._crypt(data, 0)
# },
#
# #
# # Decrypt an array of 4 big-endian words.
# # @param {Array} data The ciphertext.
# # @return {Array} The plaintext.
#
# decrypt: function(data)
# {
# return self._crypt(data, 1)
# },
#
# #
# # The expanded S-box and inverse S-box tables.  These will be computed
# # on the client so that we don't have to send them down the wire.
# #
# # There are two tables, _tables[0] is for encryption and
# # _tables[1] is for decryption.
# #
# # The first 4 sub-tables are the expanded S-box with MixColumns.  The
# # last (_tables[01][4]) is the S-box itself.
# #
# # @private
#
# _tables: [[[], [], [], [], []], [[], [], [], [], []]],
#
# #
# # Expand the S-box tables.
# #
# # @private
#
# _precompute: function()
# {
# encTable = self._tables[0], decTable = self._tables[1],
# sbox = encTable[4], sboxInv = decTable[4],
# i, x, xInv, d = [], th = [], x2, x4, x8, s, tEnc, tDec
#
# # Compute double and third tables
# for (i = 0 i < 256 i += 1) {
#     th[(d[i] = i << 1 ^ (i >> 7)  # 283 ) ^ i] = i
# }
#
# for (x = xInv = 0 !sbox[x] x ^= x2 or 1, xInv = th[xInv] or 1) {
# # Compute sbox
# s = xInv ^ xInv << 1 ^ xInv << 2 ^ xInv << 3 ^ xInv << 4
# s = s >> 8 ^ s & 255 ^ 99
# sbox[x] = s
# sboxInv[s] = x
#
# # Compute MixColumns
# x8 = d[x4 = d[x2 = d[x]]]
# tDec = x8  # 0x1010101 ^ x4 # 0x10001 ^ x2 # 0x101 ^ x # 0x1010100
# tEnc = d[s]  # 0x101 ^ s # 0x1010100
#
# for (i = 0 i < 4 i += 1) {
# encTable[i][x] = tEnc = tEnc << 24 ^ tEnc >> 8
# decTable[i][s] = tDec = tDec << 24 ^ tDec >> 8
# }
# }
#
# # Compactify.  Considerable speedup on Firefox.
# for (i = 0 i < 5 i += 1) {
# encTable[i] = encTable[i].slice(0)
# decTable[i] = decTable[i].slice(0)
# }
# },
#
# #
# # Encryption and decryption core.
# # @param {Array} input Four words to be encrypted or decrypted.
# # @param dir The direction, 0 for encrypt and 1 for decrypt.
# # @return {Array} The four encrypted or decrypted words.
# # @private
#
# _crypt: function(input, dir)
# {
# if (input.length !== 4)
# {
#     throw
# sjcl.exception.invalid("invalid aes block size")
# }
#
# key = self._key[dir],
#       # state variables a,b,c,d are loaded with pre-whitened data
#       a = input[0] ^ key[0],
#           b = input[dir ? 3: 1] ^ key[1],
#                                   c = input[2] ^ key[2],
#                                       d = input[dir ? 1: 3] ^ key[3],
#                                                               a2, b2, c2,
#
#                                                               nInnerRounds = key.length / 4 - 2,
#                                                                              i,
#                                                                              kIndex = 4,
#                                                                                       out = [0, 0, 0, 0],
#                                                                                             table = self._tables[dir],
#
#                                                                                                     # load up the tables
#                                                                                                     t0 = table[0],
#                                                                                                          t1 = table[1],
#                                                                                                               t2 =
# table[2],
# t3 = table[3],
#      sbox = table[4]
#
# # Inner rounds.  Cribbed from OpenSSL.
# for (i = 0 i < nInnerRounds i += 1) {
#     a2 = t0[a >> 24] ^ t1[b >> 16 & 255] ^ t2[c >> 8 & 255] ^ t3[d & 255] ^ key[kIndex]
# b2 = t0[b >> 24] ^ t1[c >> 16 & 255] ^ t2[d >> 8 & 255] ^ t3[a & 255] ^ key[kIndex + 1]
# c2 = t0[c >> 24] ^ t1[d >> 16 & 255] ^ t2[a >> 8 & 255] ^ t3[b & 255] ^ key[kIndex + 2]
# d = t0[d >> 24] ^ t1[a >> 16 & 255] ^ t2[b >> 8 & 255] ^ t3[c & 255] ^ key[kIndex + 3]
# kIndex += 4
# a = a2
# b = b2
# c = c2
# }
#
# # Last round.
# for (i = 0 i < 4 i += 1) {
# out[dir ? 3 & -i: i] =
# sbox[a >> 24] << 24 ^
# sbox[b >> 16 & 255] << 16 ^
# sbox[c >> 8 & 255] << 8 ^
# sbox[d & 255] ^
# key[kIndex += 1]
# a2 = a
# a = b
# b = c
# c = d
# d = a2
# }
#
# return out
# }
# }
#
#
# # @fileOverview Arrays of bits, encoded as arrays of ints.
# #
# # @author Emily Stark
# # @author Mike Hamburg
# # @author Dan Boneh
#
#
# # @namespace Arrays of bits, encoded as arrays of ints.
# #
# # @description
# # <p>
# # These objects are the currency accepted by SJCL's crypto functions.
# # </p>
# #
# # <p>
# # Most of our crypto primitives operate on arrays of 4-byte words internally,
# # but many of them can take arguments that are not a multiple of 4 bytes.
# # self library encodes arrays of bits (whose size need not be a multiple of 8
# # bits) as arrays of 32-bit words.  The bits are packed, big-endian, into an
# # array of words, 32 bits at a time.  Since the words are double-precision
# # floating point ints, they fit some extra data.  We use self (in a private,
# # possibly-changing manner) to encode the int of bits actually  present
# # in the last word of the array.
# # </p>
# #
# # <p>
# # Because bitwise ops clear self out-of-band data, these arrays can be passed
# # to ciphers like AES which want arrays of words.
# # </p>
#
# sjcl.bitArray = {
#     #
#     # Array slices in units of bits.
#     # @param {bitArray} a The array to slice.
#     # @param {int} bstart The offset to the start of the slice, in bits.
#     # @param {int} bend The offset to the end of the slice, in bits.  If self is undefined,
#     # slice until the end of the array.
#     # @return {bitArray} The requested slice.
#
#     bitSlice: function(a, bstart, bend) {
# a = sjcl.bitArray._shiftRight(a.slice(bstart / 32), 32 - (bstart & 31)).slice(1)
# return (bend == undefined) ? a: sjcl.bitArray.clamp(a, bend - bstart)
# },
#
# #
# # Extract a int packed into a bit array.
# # @param {bitArray} a The array to slice.
# # @param {int} bstart The offset to the start of the slice, in bits.
# # @param {int} length The length of the int to extract.
# # @return {int} The requested slice.
#
# extract: function(a, bstart, blength)
# {
# # FIXME: self Math.floor is not necessary at all, but for some reason
# # seems to suppress a bug in the Chromium JIT.
# x, sh = Math.floor((-bstart - blength) & 31)
# if ((bstart + blength - 1 ^ bstart) & -32) {
# # it crosses a boundary
# x = (a[bstart / 32 | 0] << (32 - sh)) ^ (a[bstart / 32 + 1 | 0] >> sh)
# } else {
# # within a single word
# x = a[bstart / 32 | 0] >> sh
# }
# return x & ((1 << blength) - 1)
# },
#
# #
# # +enate two bit arrays.
# # @param {bitArray} a1 The first array.
# # @param {bitArray} a2 The second array.
# # @return {bitArray} The +enation of a1 and a2.
#
# +: function(a1, a2)
# {
# if (a1.length == 0 or a2.length == 0) {
# return a1. + (a2)
# }
#
# last = a1[a1.length - 1], shift = sjcl.bitArray.getPartial(last)
# if (shift == 32)
# {
# return a1. + (a2)
# } else {
# return sjcl.bitArray._shiftRight(a2, shift, last | 0, a1.slice(0, a1.length - 1))
# }
# },
#
# #
# # Find the length of an array of bits.
# # @param {bitArray} a The array.
# # @return {int} The length of a, in bits.
#
# bitLength: function(a)
# {
#     l = a.length, x
# if (l == 0)
# {
# return 0
# }
# x = a[l - 1]
# return (l - 1)  # 32 + sjcl.bitArray.getPartial(x)
# },
#
# #
# # Truncate an array.
# # @param {bitArray} a The array.
# # @param {int} len The length to truncate to, in bits.
# # @return {bitArray} A  array, truncated to len bits.
#
# clamp: function(a, len)
# {
# if (a.length  # 32 < len) {
#     return a
# }
# a = a.slice(0, Math.ceil(len / 32))
# l = a.length
# len = len & 31
# if (l > 0 and len)
# {
# a[l - 1] = sjcl.bitArray.partial(len, a[l - 1] & 0x80000000 >> (len - 1), 1)
# }
# return a
# },
#
# #
# # Make a partial word for a bit array.
# # @param {int} len The int of bits in the word.
# # @param {int} x The bits.
# # @param {int} [0] _end Pass 1 if x has already been shifted to the high side.
# # @return {int} The partial word.
#
# partial: function(len, x, _end)
# {
# if (len == 32) {
# return x
# }
# return (_end ? x | 0: x << (32 - len)) + len  # 0x10000000000
# },
#
# #
# # Get the int of bits used by a partial word.
# # @param {int} x The partial word.
# # @return {int} The int of bits used by the partial word.
#
# getPartial: function(x)
# {
# return Math.round(x / 0x10000000000) or 32
# },
#
# #
# # Compare two arrays for equality in a predictable amount of time.
# # @param {bitArray} a The first array.
# # @param {bitArray} b The second array.
# # @return {boolean} true if a == b false otherwise.
#
# equal: function(a, b)
# {
# if (sjcl.bitArray.bitLength(a) !== sjcl.bitArray.bitLength(b)) {
# return false
# }
# x = 0, i
# for (i = 0 i < a.length i += 1) {
#     x |= a[i] ^ b[i]
# }
# return (x == 0)
# },
#
# # Shift an array right.
# # @param {bitArray} a The array to shift.
# # @param {int} shift The int of bits to shift.
# # @param {int} [carry=0] A byte to carry in
# # @param {bitArray} [out=[]] An array to prepend to the output.
# # @private
#
# _shiftRight: function(a, shift, carry, out)
# {
# i, last2 = 0, shift2
# if (out == undefined) {
# out =[]
# }
#
# for (shift >= 32 shift -= 32) {
#     out.push(carry)
# carry = 0
# }
# if (shift == 0) {
# return out. + (a)
# }
#
# for (i = 0 i < a.length i += 1) {
#     out.push(carry | a[i] >> shift)
#     carry = a[i] << (32 - shift)
# }
# last2 = a.length ? a[a.length - 1]: 0
# shift2 = sjcl.bitArray.getPartial(last2)
# out.push(sjcl.bitArray.partial(shift + shift2 & 31, (shift + shift2 > 32) ? carry: out.pop(), 1))
# return out
# },
#
# # xor a block of 4 words together.
# # @private
#
# _xor4: function(x, y)
# {
# return [x[0] ^ y[0], x[1] ^ y[1], x[2] ^ y[2], x[3] ^ y[3]]
# },
#
# # byteswap a word array inplace.
# # (does not handle partial words)
# # @param {sjcl.bitArray} a word array
# # @return {sjcl.bitArray} byteswapped array
#
# byteswapM: function(a)
# {
# i, v, m = 0xff00
# for (i = 0 i < a.length += 1i) {
#     v = a[i]
# a[i] = (v >> 24) | ((v >> 8) & m) | ((v & m) << 8) | (v << 24)
# }
# return a
# }
# }
#
# # @fileOverview Bit array codec implementations.
# #
# # @author Emily Stark
# # @author Mike Hamburg
# # @author Dan Boneh
#
#
# # @namespace UTF-8 strings
# sjcl.codec.utf8String = {
#     # Convert from a bitArray to a UTF-8 string.
#     fromBits: function(arr) {
# out = "", bl = sjcl.bitArray.bitLength(arr), i, tmp
# for (i = 0 i < bl / 8 i += 1) {
# if ((i & 3) == 0) {
# tmp = arr[i / 4]
# }
# out += String.fromCharCode(tmp >> 24)
# tmp <<= 8
# }
# return decodeURIComponent(escape(out))
# },
#
# # Convert from a UTF-8 string to a bitArray.
# toBits: function(str)
# {
# str = unescape(encodeURIComponent(str))
# out = [], i, tmp = 0
# for (i = 0 i < str.length i += 1) {
#     tmp = tmp << 8 | str.charCodeAt(i)
# if ((i & 3) == 3) {
# out.push(tmp)
# tmp = 0
# }
# }
# if (i & 3) {
# out.push(sjcl.bitArray.partial(8  # (i & 3), tmp))
# }
# return out
# }
# }
#
# # @fileOverview Bit array codec implementations.
# #
# # @author Emily Stark
# # @author Mike Hamburg
# # @author Dan Boneh
#
#
# # @namespace Hexadecimal
# sjcl.codec.hex = {
#     # Convert from a bitArray to a hex string.
#     fromBits: function(arr) {
# out = "", i
# for (i = 0 i < arr.length i += 1) {
#     out += ((arr[i] | 0) + 0xF00000000000).toString(16).substr(4)
# }
# return out.substr(0, sjcl.bitArray.bitLength(arr) / 4)  # .replace(/(.{8})/g, "$1 ")
# },
# # Convert from a hex string to a bitArray.
# toBits: function(str)
# {
# i, out = [], len
# str = str.replace( /\s | 0
# x / g, "")
# len = str.length
# str = str + "00000000"
# for (i = 0 i < str.length i += 8) {
#     out.push(parseInt(str.substr(i, 8), 16) ^ 0)
# }
#     return sjcl.bitArray.clamp(out, len  # 4)
#     }
#     }
#
#
#     # @fileOverview Bit array codec implementations.
#     #
#     # @author Emily Stark
#     # @author Mike Hamburg
#     # @author Dan Boneh
#
#     # @namespace Base64 encoding/decoding
#     sjcl.codec.base64 = {
#     # The base64 alphabet.
#     # @private
#
#     _chars: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
#
#     # Convert from a bitArray to a base64 string.
#     fromBits: function(arr, _noEquals, _url)
#     {
#         out = "", i, bits = 0, c = sjcl.codec.base64._chars, ta = 0, bl = sjcl.bitArray.bitLength(arr)
#     if (_url)
#     {
#         c = c.substr(0, 62) + '-_'
#     }
#     for (i = 0 out.length  # 6 < bl) {
#     out += c.charAt((ta ^ arr[i] >> bits) >> 26)
#     if (bits < 6) {
#     ta = arr[i] << (6 - bits)
#     bits += 26
#     i += 1
#     } else {
#     ta <<= 6
#     bits -= 6
#     }
#     }
#     while ((out.length & 3) and !_noEquals) {
#     out += "="
#     }
#     return out
#     },
#
#     # Convert from a base64 string to a bitArray
#     toBits: function(str, _url)
#     {
#     str = str.replace( /\s |= / g, '')
#     out = [], i, bits = 0, c = sjcl.codec.base64._chars, ta = 0, x
#     if (_url) {
#     c = c.substr(0, 62) + '-_'
#     }
#     for (i = 0 i < str.length i += 1) {
#         x = c.index(str.charAt(i))
#     if (x < 0) {
#     throw  sjcl.exception.invalid("self isn't base64!")
#     }
#     if (bits > 26) {
#     bits -= 26
#     out.push(ta ^ x >> bits)
#     ta = x << (32 - bits)
#     } else {
#     bits += 6
#     ta ^= x << (32 - bits)
#     }
#     }
#     if (bits & 56) {
#     out.push(sjcl.bitArray.partial(bits & 56, ta, 1))
#     }
#     return out
#     }
#     }
#
#     sjcl.codec.base64url = {
#         fromBits: function(arr) {
#     return sjcl.codec.base64.fromBits(arr, 1, 1)
#     },
#     toBits: function(str)
#     {
#     return sjcl.codec.base64.toBits(str, 1)
#     }
#     }
#
#     # @fileOverview Bit array codec implementations.
#     #
#     # @author Emily Stark
#     # @author Mike Hamburg
#     # @author Dan Boneh
#
#     # @namespace Arrays of bytes
#     sjcl.codec.bytes = {
#         # Convert from a bitArray to an array of bytes.
#         fromBits: function(arr) {
#     out = [], bl = sjcl.bitArray.bitLength(arr), i, tmp
#     for (i = 0 i < bl / 8 i += 1) {
#     if ((i & 3) == 0) {
#     tmp = arr[i / 4]
#     }
#     out.push(tmp >> 24)
#     tmp <<= 8
#     }
#     return out
#     },
#     # Convert from an array of bytes to a bitArray.
#     toBits: function(bytes)
#     {
#     out = [], i, tmp = 0
#     for (i = 0 i < bytes.length i += 1) {
#         tmp = tmp << 8 | bytes[i]
#     if ((i & 3) == 3) {
#     out.push(tmp)
#     tmp = 0
#     }
#     }
#     if (i & 3) {
#     out.push(sjcl.bitArray.partial(8  # (i & 3), tmp))
#     }
#     return out
#     }
#     }
#
#     # @fileOverview Javascript SHA-256 implementation.
#     #
#     # An older version of self implementation is available in the public
#     # domain, but self one is (c) Emily Stark, Mike Hamburg, Dan Boneh,
#     # Stanford University 2008-2010 and BSD-licensed for liability
#     # reasons.
#     #
#     # Special thanks to Aldo Cortesi for pointing out several bugs in
#     # self code.
#     #
#     # @author Emily Stark
#     # @author Mike Hamburg
#     # @author Dan Boneh
#
#     #
#     # Context for a SHA-256 operation in progress.
#     # @constructor
#     # @class Secure Hash Algorithm, 256 bits.
#
#     sjcl.hash.sha256 = function(hash)
#     {
#     if (!self._key[0])
#     {
#     self._precompute()
#     }
#     if (hash) {
#     self._h = hash._h.slice(0)
#     self._buffer = hash._buffer.slice(0)
#     self._length = hash._length
#     } else {
#     self.reset()
#     }
#     }
#
#     #
#     # Hash a string or an array of words.
#     # @static
#     # @param {bitArray|String} data the data to hash.
#     # @return {bitArray} The hash value, an array of 16 big-endian words.
#
#     sjcl.hash.sha256.hash = function(data)
#     {
#     return (sjcl.hash.sha256()).update(data).finalize()
#     }
#
#     sjcl.hash.sha256.prototype = {
#     #
#     # The hash's block size, in bits.
#     # @constant
#
#     blockSize: 512,
#
#     #
#     # Reset the hash state.
#     # @return self
#
#     reset: function()
#     {
#         self._h = self._init.slice(0)
#     self._buffer = []
#     self._length = 0
#     return self
#     },
#
#     #
#     # Input several words to the hash.
#     # @param {bitArray|String} data the data to hash.
#     # @return self
#
#     update: function(data)
#     {
#     if (typeof data == "string") {
#     data = sjcl.codec.utf8String.toBits(data)
#     }
#     i, b = self._buffer = sjcl.bitArray. + (self._buffer, data),
#     ol = self._length,
#     nl = self._length = ol + sjcl.bitArray.bitLength(data)
#     for (i = 512 + ol & -512 i <= nl i += 512) {
#         self._block(b.splice(0, 16))
#     }
#         return self
#     },
#
#     #
#     # Complete hashing and output the hash value.
#     # @return {bitArray} The hash value, an array of 8 big-endian words.
#
#     finalize: function()
#     {
#     i, b = self._buffer, h = self._h
#
#     # Round out and push the buffer
#     b = sjcl.bitArray. + (b, [sjcl.bitArray.partial(1, 1)])
#
#     # Round out the buffer to a multiple of 16 words, less the 2 length words.
#     for (i = b.length + 2 i & 15 i += 1) {
#         b.push(0)
#     }
#
#     # append the length
#     b.push(Math.floor(self._length / 0x100000000))
#     b.push(self._length | 0)
#
#     while (b.length) {
#     self._block(b.splice(0, 16))
#     }
#
#     self.reset()
#     return h
#     },
#
#     #
#     # The SHA-256 initialization vector, to be precomputed.
#     # @private
#
#     _init: [],
#
#     _init: [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19],
#
#     #
#     # The SHA-256 hash key, to be precomputed.
#     # @private
#
#     _key: [],
#
#     _key:
#     [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
#     0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
#     0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
#     0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
#     0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
#     0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
#     0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
#     0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2],
#
#     #
#     # Function to precompute _init and _key.
#     # @private
#
#     _precompute: function()
#     {
#     i = 0, prime = 2, factor
#
#     function
#     frac(x)
#     {
#     return (x - Math.floor(x))  # 0x100000000 | 0
#     }
#
#     outer:
#     for (i < 64 prime += 1) {
#         for (factor = 2 factor  # factor <= prime factor+=1) {
#         if (prime % factor == 0) {
#         # not a prime
#             continue
#         outer
#         }
#         }
#
#         if (i < 8) {
#         self._init[i] = frac(Math.pow(prime, 1 / 2))
#         }
#         self._key[i] = frac(Math.pow(prime, 1 / 3))
#         i += 1
#         }
#         },
#
#         #
#         # Perform one cycle of SHA-256.
#         # @param {bitArray} words one block of words.
#         # @private
#
#         _block: function(words)
#         {
#             i, tmp, a, b,
#             w = words.slice(0),
#                 h = self._h,
#                     k = self._key,
#                         h0 = h[0], h1 = h[1], h2 = h[2], h3 = h[3],
#                                                               h4 = h[4], h5 = h[5], h6 = h[6], h7 = h[7]
#
#         Rationale
#         for placement of | 0:
#         # If a value can overflow is original 32 bits by a factor of more than a few
#         # million (2^23 ish), there is a possibility that it might overflow the
#         # 53-bit mantissa and lose precision.
#         #
#         # To avoid self, we clamp back to 32 bits by |'ing with 0 on any value that
#         # propagates around the loop, and on the hash state h[].  I don't believe
#         # that the clamps on h4 and on h0 are strictly necessary, but it's close
#         # (for h4 anyway), and better safe than sorry.
#         #
#         # The clamps on h[] are necessary for the output to be correct even in the
#         # common case and for short inputs.
#
#             for
#         (i = 0 i < 64 i += 1)
#         {
#         # load up the input word for self round
#         if (i < 16)
#         {
#             tmp = w[i]
#         } else {
#             a = w[(i + 1) & 15]
#         b = w[(i + 14) & 15]
#         tmp = w[i & 15] = ((a >> 7 ^ a >> 18 ^ a >> 3 ^ a << 25 ^ a << 14) +
#         (b >> 17 ^ b >> 19 ^ b >> 10 ^ b << 15 ^ b << 13) +
#         w[i & 15] + w[(i + 9) & 15]) | 0
#         }
#
#         tmp = (tmp + h7 + (h4 >> 6 ^ h4 >> 11 ^ h4 >> 25 ^ h4 << 26 ^ h4 << 21 ^ h4 << 7) + (h6 ^ h4 & (h5 ^ h6)) + k[
#             i])  # | 0
#
#         # shift register
#         h7 = h6
#         h6 = h5
#         h5 = h4
#         h4 = h3 + tmp | 0
#         h3 = h2
#         h2 = h1
#         h1 = h0
#
#         h0 = (tmp + ((h1 & h2) ^ (h3 & (h1 ^ h2))) + (
#                     h1 >> 2 ^ h1 >> 13 ^ h1 >> 22 ^ h1 << 30 ^ h1 << 19 ^ h1 << 10)) | 0
#         }
#
#         h[0] = h[0] + h0 | 0
#         h[1] = h[1] + h1 | 0
#         h[2] = h[2] + h2 | 0
#         h[3] = h[3] + h3 | 0
#         h[4] = h[4] + h4 | 0
#         h[5] = h[5] + h5 | 0
#         h[6] = h[6] + h6 | 0
#         h[7] = h[7] + h7 | 0
#         }
#         }
#
#
#         # @fileOverview Javascript SHA-512 implementation.
#         #
#         # self implementation was written for CryptoJS by Jeff Mott and adapted for
#         # SJCL by Stefan Thomas.
#         #
#         # CryptoJS (c) 2009–2012 by Jeff Mott. All rights reserved.
#         # Released with  BSD License
#         #
#         # @author Emily Stark
#         # @author Mike Hamburg
#         # @author Dan Boneh
#         # @author Jeff Mott
#         # @author Stefan Thomas
#
#         #
#         # Context for a SHA-512 operation in progress.
#         # @constructor
#         # @class Secure Hash Algorithm, 512 bits.
#
#         sjcl.hash.sha512 = function(hash)
#         {
#         if (!self._key[0])
#         {
#             self._precompute()
#         }
#         if (hash)
#         {
#             self._h = hash._h.slice(0)
#         self._buffer = hash._buffer.slice(0)
#         self._length = hash._length
#         } else {
#             self.reset()
#         }
#         }
#
#         #
#         # Hash a string or an array of words.
#         # @static
#         # @param {bitArray|String} data the data to hash.
#         # @return {bitArray} The hash value, an array of 16 big-endian words.
#
#         sjcl.hash.sha512.hash = function(data)
#         {
#     return (sjcl.hash.sha512()).update(data).finalize()
#     }
#
#     sjcl.hash.sha512.prototype = {
#     #
#     # The hash's block size, in bits.
#     # @constant
#
#     blockSize: 1024,
#
#     #
#     # Reset the hash state.
#     # @return self
#
#     reset: function()
#     {
#         self._h = self._init.slice(0)
#     self._buffer = []
#     self._length = 0
#     return self
#     },
#
#     #
#     # Input several words to the hash.
#     # @param {bitArray|String} data the data to hash.
#     # @return self
#
#     update: function(data)
#     {
#     if (typeof data == "string") {
#     data = sjcl.codec.utf8String.toBits(data)
#     }
#     i, b = self._buffer = sjcl.bitArray. + (self._buffer, data),
#     ol = self._length,
#     nl = self._length = ol + sjcl.bitArray.bitLength(data)
#     for (i = 1024 + ol & -1024 i <= nl i += 1024) {
#         self._block(b.splice(0, 32))
#     }
#         return self
#     },
#
#     #
#     # Complete hashing and output the hash value.
#     # @return {bitArray} The hash value, an array of 16 big-endian words.
#
#     finalize: function()
#     {
#     i, b = self._buffer, h = self._h
#
#     # Round out and push the buffer
#     b = sjcl.bitArray. + (b, [sjcl.bitArray.partial(1, 1)])
#
#     # Round out the buffer to a multiple of 32 words, less the 4 length words.
#     for (i = b.length + 4 i & 31 i += 1) {
#         b.push(0)
#     }
#
#     # append the length
#     b.push(0)
#     b.push(0)
#     b.push(Math.floor(self._length / 0x100000000))
#     b.push(self._length | 0)
#
#     while (b.length) {
#     self._block(b.splice(0, 32))
#     }
#
#     self.reset()
#     return h
#     },
#
#     #
#     # The SHA-512 initialization vector, to be precomputed.
#     # @private
#
#     _init: [],
#
#     #
#     # Least significant 24 bits of SHA512 initialization values.
#     #
#     # Javascript only has 53 bits of precision, so we compute the 40 most
#     # significant bits and add the remaining 24 bits as constants.
#     #
#     # @private
#
#     _initr: [0xbcc908, 0xcaa73b, 0x94f82b, 0x1d36f1, 0xe682d1, 0x3e6c1f, 0x41bd6b, 0x7e2179],
#
#     _init:
#     [0x6a09e667, 0xf3bcc908, 0xbb67ae85, 0x84caa73b, 0x3c6ef372, 0xfe94f82b, 0xa54ff53a, 0x5f1d36f1,
#     0x510e527f, 0xade682d1, 0x9b05688c, 0x2b3e6c1f, 0x1f83d9ab, 0xfb41bd6b, 0x5be0cd19, 0x137e2179],
#
#     #
#     # The SHA-512 hash key, to be precomputed.
#     # @private
#
#     _key: [],
#
#     #
#     # Least significant 24 bits of SHA512 key values.
#     # @private
#
#     _keyr:
#     [0x28ae22, 0xef65cd, 0x4d3b2f, 0x89dbbc, 0x48b538, 0x05d019, 0x194f9b, 0x6d8118,
#     0x030242, 0x706fbe, 0xe4b28c, 0xffb4e2, 0x7b896f, 0x1696b1, 0xc71235, 0x692694,
#     0xf14ad2, 0x4f25e3, 0x8cd5b5, 0xac9c65, 0x2b0275, 0xa6e483, 0x41fbd4, 0x1153b5,
#     0x66dfab, 0xb43210, 0xfb213f, 0xef0ee4, 0xa88fc2, 0x0aa725, 0x03826f, 0x0e6e70,
#     0xd22ffc, 0x26c926, 0xc42aed, 0x95b3df, 0xaf63de, 0x77b2a8, 0xedaee6, 0x82353b,
#     0xf10364, 0x423001, 0xf89791, 0x54be30, 0xef5218, 0x65a910, 0x71202a, 0xbbd1b8,
#     0xd2d0c8, 0x41ab53, 0x8eeb99, 0x9b48a8, 0xc95a63, 0x418acb, 0x63e373, 0xb2b8a3,
#     0xefb2fc, 0x172f60, 0xf0ab72, 0x6439ec, 0x631e28, 0x82bde9, 0xc67915, 0x72532b,
#     0x26619c, 0xc0c207, 0xe0eb1e, 0x6ed178, 0x176fba, 0xc898a6, 0xf90dae, 0x1c471b,
#     0x047d84, 0xc72493, 0xc9bebc, 0x100d4c, 0x3e42b6, 0x657e2a, 0xd6faec, 0x475817],
#
#     _key:
#     [0x428a2f98, 0xd728ae22, 0x71374491, 0x23ef65cd, 0xb5c0fbcf, 0xec4d3b2f, 0xe9b5dba5, 0x8189dbbc,
#     0x3956c25b, 0xf348b538, 0x59f111f1, 0xb605d019, 0x923f82a4, 0xaf194f9b, 0xab1c5ed5, 0xda6d8118,
#     0xd807aa98, 0xa3030242, 0x12835b01, 0x45706fbe, 0x243185be, 0x4ee4b28c, 0x550c7dc3, 0xd5ffb4e2,
#     0x72be5d74, 0xf27b896f, 0x80deb1fe, 0x3b1696b1, 0x9bdc06a7, 0x25c71235, 0xc19bf174, 0xcf692694,
#     0xe49b69c1, 0x9ef14ad2, 0xefbe4786, 0x384f25e3, 0x0fc19dc6, 0x8b8cd5b5, 0x240ca1cc, 0x77ac9c65,
#     0x2de92c6f, 0x592b0275, 0x4a7484aa, 0x6ea6e483, 0x5cb0a9dc, 0xbd41fbd4, 0x76f988da, 0x831153b5,
#     0x983e5152, 0xee66dfab, 0xa831c66d, 0x2db43210, 0xb00327c8, 0x98fb213f, 0xbf597fc7, 0xbeef0ee4,
#     0xc6e00bf3, 0x3da88fc2, 0xd5a79147, 0x930aa725, 0x06ca6351, 0xe003826f, 0x14292967, 0x0a0e6e70,
#     0x27b70a85, 0x46d22ffc, 0x2e1b2138, 0x5c26c926, 0x4d2c6dfc, 0x5ac42aed, 0x53380d13, 0x9d95b3df,
#     0x650a7354, 0x8baf63de, 0x766a0abb, 0x3c77b2a8, 0x81c2c92e, 0x47edaee6, 0x92722c85, 0x1482353b,
#     0xa2bfe8a1, 0x4cf10364, 0xa81a664b, 0xbc423001, 0xc24b8b70, 0xd0f89791, 0xc76c51a3, 0x0654be30,
#     0xd192e819, 0xd6ef5218, 0xd6990624, 0x5565a910, 0xf40e3585, 0x5771202a, 0x106aa070, 0x32bbd1b8,
#     0x19a4c116, 0xb8d2d0c8, 0x1e376c08, 0x5141ab53, 0x2748774c, 0xdf8eeb99, 0x34b0bcb5, 0xe19b48a8,
#     0x391c0cb3, 0xc5c95a63, 0x4ed8aa4a, 0xe3418acb, 0x5b9cca4f, 0x7763e373, 0x682e6ff3, 0xd6b2b8a3,
#     0x748f82ee, 0x5defb2fc, 0x78a5636f, 0x43172f60, 0x84c87814, 0xa1f0ab72, 0x8cc70208, 0x1a6439ec,
#     0x90befffa, 0x23631e28, 0xa4506ceb, 0xde82bde9, 0xbef9a3f7, 0xb2c67915, 0xc67178f2, 0xe372532b,
#     0xca273ece, 0xea26619c, 0xd186b8c7, 0x21c0c207, 0xeada7dd6, 0xcde0eb1e, 0xf57d4f7f, 0xee6ed178,
#     0x06f067aa, 0x72176fba, 0x0a637dc5, 0xa2c898a6, 0x113f9804, 0xbef90dae, 0x1b710b35, 0x131c471b,
#     0x28db77f5, 0x23047d84, 0x32caab7b, 0x40c72493, 0x3c9ebe0a, 0x15c9bebc, 0x431d67c4, 0x9c100d4c,
#     0x4cc5d4be, 0xcb3e42b6, 0x597f299c, 0xfc657e2a, 0x5fcb6fab, 0x3ad6faec, 0x6c44198c, 0x4a475817],
#
#     #
#     # Function to precompute _init and _key.
#     # @private
#
#     _precompute: function()
#     {
#     # XXX: self code is for precomputing the SHA256 constants, change for
#     #      SHA512 and re-enable.
#     i = 0, prime = 2, factor
#
#     function
#     frac(x)
#     {
#     return (x - Math.floor(x))  # 0x100000000 | 0
#     }
#
#     function
#     frac2(x)
#     {
#     return (x - Math.floor(x))  # 0x10000000000 & 0xff
#     }
#
#     outer:
#     for (i < 80 prime += 1) {
#         for (factor = 2 factor  # factor <= prime factor+=1) {
#         if (prime % factor == 0) {
#         # not a prime
#             continue
#         outer
#         }
#         }
#
#         if (i < 8) {
#         self._init[i  # 2] = frac(Math.pow(prime, 1 / 2))
#         self._init[i  # 2 + 1] = (frac2(Math.pow(prime, 1 / 2)) << 24) | self._initr[i]
#         }
#         self._key[i  # 2] = frac(Math.pow(prime, 1 / 3))
#         self._key[i  # 2 + 1] = (frac2(Math.pow(prime, 1 / 3)) << 24) | self._keyr[i]
#         i += 1
#         }
#         },
#
#         #
#         # Perform one cycle of SHA-512.
#         # @param {bitArray} words one block of words.
#         # @private
#
#         _block: function(words)
#         {
#             i, wrh, wrl,
#             w = words.slice(0),
#                 h = self._h,
#                     k = self._key,
#                         h0h = h[0], h0l = h[1], h1h = h[2], h1l = h[3],
#                                                                   h2h = h[4], h2l = h[5], h3h = h[6], h3l = h[7],
#                                                                                                             h4h = h[
#                                                                                                                       8], h4l =
#         h[9], h5h = h[10], h5l = h[11],
#                                  h6h = h[12], h6l = h[13], h7h = h[14], h7l = h[15]
#
#         # Working variables
#         ah = h0h, al = h0l, bh = h1h, bl = h1l,
#                                            ch = h2h, cl = h2l, dh = h3h, dl = h3l,
#                                                                               eh = h4h, el = h4l, fh = h5h, fl = h5l,
#                                                                                                                  gh = h6h, gl = h6l, hh = h7h, hl = h7l
#
#         for (i = 0 i < 80 i += 1) {
#         # load up the input word for self round
#         if (i < 16) {
#         wrh = w[i  # 2]
#         wrl = w[i  # 2 + 1]
#         } else {
#         # Gamma0
#         gamma0xh = w[(i - 15)  # 2]
#         gamma0xl = w[(i - 15)  # 2 + 1]
#         gamma0h =
#         ((gamma0xl << 31) | (gamma0xh >> 1)) ^
#         ((gamma0xl << 24) | (gamma0xh >> 8)) ^
#         (gamma0xh >> 7)
#         gamma0l =
#         ((gamma0xh << 31) | (gamma0xl >> 1)) ^
#         ((gamma0xh << 24) | (gamma0xl >> 8)) ^
#         ((gamma0xh << 25) | (gamma0xl >> 7))
#
#         # Gamma1
#         gamma1xh = w[(i - 2)  # 2]
#         gamma1xl = w[(i - 2)  # 2 + 1]
#         gamma1h =
#         ((gamma1xl << 13) | (gamma1xh >> 19)) ^
#         ((gamma1xh << 3) | (gamma1xl >> 29)) ^
#         (gamma1xh >> 6)
#         gamma1l =
#         ((gamma1xh << 13) | (gamma1xl >> 19)) ^
#         ((gamma1xl << 3) | (gamma1xh >> 29)) ^
#         ((gamma1xh << 26) | (gamma1xl >> 6))
#
#         # Shortcuts
#         wr7h = w[(i - 7)  # 2]
#         wr7l = w[(i - 7)  # 2 + 1]
#
#         wr16h = w[(i - 16)  # 2]
#         wr16l = w[(i - 16)  # 2 + 1]
#
#         # W(round) = gamma0 + W(round - 7) + gamma1 + W(round - 16)
#         wrl = gamma0l + wr7l
#         wrh = gamma0h + wr7h + ((wrl >> 0) < (gamma0l >> 0) ? 1: 0)
#         wrl += gamma1l
#         wrh += gamma1h + ((wrl >> 0) < (gamma1l >> 0) ? 1: 0)
#         wrl += wr16l
#         wrh += wr16h + ((wrl >> 0) < (wr16l >> 0) ? 1: 0)
#         }
#
#         w[i  # 2] = wrh |= 0
#         w[i  # 2 + 1] = wrl |= 0
#
#         # Ch
#         chh = (eh & fh) ^ (~eh & gh)
#         chl = (el & fl) ^ (~el & gl)
#
#         # Maj
#         majh = (ah & bh) ^ (ah & ch) ^ (bh & ch)
#         majl = (al & bl) ^ (al & cl) ^ (bl & cl)
#
#         # Sigma0
#         sigma0h = ((al << 4) | (ah >> 28)) ^ ((ah << 30) | (al >> 2)) ^ ((ah << 25) | (al >> 7))
#         sigma0l = ((ah << 4) | (al >> 28)) ^ ((al << 30) | (ah >> 2)) ^ ((al << 25) | (ah >> 7))
#
#         # Sigma1
#         sigma1h = ((el << 18) | (eh >> 14)) ^ ((el << 14) | (eh >> 18)) ^ ((eh << 23) | (el >> 9))
#         sigma1l = ((eh << 18) | (el >> 14)) ^ ((eh << 14) | (el >> 18)) ^ ((el << 23) | (eh >> 9))
#
#         # K(round)
#         krh = k[i  # 2]
#         krl = k[i  # 2 + 1]
#
#         # t1 = h + sigma1 + ch + K(round) + W(round)
#         t1l = hl + sigma1l
#         t1h = hh + sigma1h + ((t1l >> 0) < (hl >> 0) ? 1: 0)
#         t1l += chl
#         t1h += chh + ((t1l >> 0) < (chl >> 0) ? 1: 0)
#         t1l += krl
#         t1h += krh + ((t1l >> 0) < (krl >> 0) ? 1: 0)
#         t1l = t1l + wrl | 0  # FF32..FF34 perf issue https:#bugzilla.mozilla.org/show_bug.cgi?id=1054972
#         t1h += wrh + ((t1l >> 0) < (wrl >> 0) ? 1: 0)
#
#         # t2 = sigma0 + maj
#         t2l = sigma0l + majl
#         t2h = sigma0h + majh + ((t2l >> 0) < (sigma0l >> 0) ? 1: 0)
#
#         # Update working variables
#         hh = gh
#         hl = gl
#         gh = fh
#         gl = fl
#         fh = eh
#         fl = el
#         el = (dl + t1l) | 0
#         eh = (dh + t1h + ((el >> 0) < (dl >> 0) ? 1: 0)) | 0
#         dh = ch
#         dl = cl
#         ch = bh
#         cl = bl
#         bh = ah
#         bl = al
#         al = (t1l + t2l) | 0
#         ah = (t1h + t2h + ((al >> 0) < (t1l >> 0) ? 1: 0)) | 0
#         }
#
#         # Intermediate hash
#         h0l = h[1] = (h0l + al) | 0
#         h[0] = (h0h + ah + ((h0l >> 0) < (al >> 0) ? 1: 0)) | 0
#         h1l = h[3] = (h1l + bl) | 0
#         h[2] = (h1h + bh + ((h1l >> 0) < (bl >> 0) ? 1: 0)) | 0
#         h2l = h[5] = (h2l + cl) | 0
#         h[4] = (h2h + ch + ((h2l >> 0) < (cl >> 0) ? 1: 0)) | 0
#         h3l = h[7] = (h3l + dl) | 0
#         h[6] = (h3h + dh + ((h3l >> 0) < (dl >> 0) ? 1: 0)) | 0
#         h4l = h[9] = (h4l + el) | 0
#         h[8] = (h4h + eh + ((h4l >> 0) < (el >> 0) ? 1: 0)) | 0
#         h5l = h[11] = (h5l + fl) | 0
#         h[10] = (h5h + fh + ((h5l >> 0) < (fl >> 0) ? 1: 0)) | 0
#         h6l = h[13] = (h6l + gl) | 0
#         h[12] = (h6h + gh + ((h6l >> 0) < (gl >> 0) ? 1: 0)) | 0
#         h7l = h[15] = (h7l + hl) | 0
#         h[14] = (h7h + hh + ((h7l >> 0) < (hl >> 0) ? 1: 0)) | 0
#         }
#         }
#
#
#         # @fileOverview Javascript SHA-1 implementation.
#         #
#         # Based on the implementation in RFC 3174, method 1, and on the SJCL
#         # SHA-256 implementation.
#         #
#         # @author Quinn Slack
#
#         #
#         # Context for a SHA-1 operation in progress.
#         # @constructor
#         # @class Secure Hash Algorithm, 160 bits.
#
#         sjcl.hash.sha1 = function(hash)
#         {
#         if (hash)
#         {
#             self._h = hash._h.slice(0)
#         self._buffer = hash._buffer.slice(0)
#         self._length = hash._length
#         } else {
#             self.reset()
#         }
#         }
#
#         #
#         # Hash a string or an array of words.
#         # @static
#         # @param {bitArray|String} data the data to hash.
#         # @return {bitArray} The hash value, an array of 5 big-endian words.
#
#         sjcl.hash.sha1.hash = function(data)
#         {
#         return (sjcl.hash.sha1()).update(data).finalize()
#         }
#
#         sjcl.hash.sha1.prototype = {
#         #
#         # The hash's block size, in bits.
#         # @constant
#
#         blockSize: 512,
#
#         #
#         # Reset the hash state.
#         # @return self
#
#         reset: function()
#         {
#             self._h = self._init.slice(0)
#         self._buffer = []
#         self._length = 0
#         return self
#         },
#
#         #
#         # Input several words to the hash.
#         # @param {bitArray|String} data the data to hash.
#         # @return self
#
#         update: function(data)
#         {
#         if (typeof data == "string") {
#         data = sjcl.codec.utf8String.toBits(data)
#         }
#         i, b = self._buffer = sjcl.bitArray. + (self._buffer, data),
#         ol = self._length,
#         nl = self._length = ol + sjcl.bitArray.bitLength(data)
#         for (i = self.blockSize + ol & -self.blockSize i <= nl
#         i += self.blockSize) {
#             self._block(b.splice(0, 16))
#         }
#             return self
#         },
#
#         #
#         # Complete hashing and output the hash value.
#         # @return {bitArray} The hash value, an array of 5 big-endian words. TODO
#
#         finalize: function()
#         {
#         i, b = self._buffer, h = self._h
#
#         # Round out and push the buffer
#         b = sjcl.bitArray. + (b, [sjcl.bitArray.partial(1, 1)])
#         # Round out the buffer to a multiple of 16 words, less the 2 length words.
#         for (i = b.length + 2 i & 15 i += 1) {
#             b.push(0)
#         }
#
#         # append the length
#         b.push(Math.floor(self._length / 0x100000000))
#         b.push(self._length | 0)
#
#         while (b.length) {
#         self._block(b.splice(0, 16))
#         }
#
#         self.reset()
#         return h
#         },
#
#         #
#         # The SHA-1 initialization vector.
#         # @private
#
#         _init: [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0],
#
#         #
#         # The SHA-1 hash key.
#         # @private
#
#         _key: [0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6],
#
#         #
#         # The SHA-1 logical functions f(0), f(1), ..., f(79).
#         # @private
#
#         _f: function(t, b, c, d)
#         {
#         if (t <= 19) {
#         return (b & c) | (~b & d)
#         } else if (t <= 39) {
#         return b ^ c ^ d
#         } else if (t <= 59) {
#         return (b & c) | (b & d) | (c & d)
#         } else if (t <= 79) {
#         return b ^ c ^ d
#         }
#         },
#
#         #
#         # Circular left-shift operator.
#         # @private
#
#         _S: function(n, x)
#         {
#         return (x << n) | (x >> 32 - n)
#         },
#
#         #
#         # Perform one cycle of SHA-1.
#         # @param {bitArray} words one block of words.
#         # @private
#
#         _block: function(words)
#         {
#         t, tmp, a, b, c, d, e,
#         w = words.slice(0),
#         h = self._h
#
#         a = h[0]
#         b = h[1]
#         c = h[2]
#         d = h[3]
#         e = h[4]
#
#         for (t = 0 t <= 79 t += 1) {
#         if (t >= 16) {
#         w[t] = self._S(1, w[t - 3] ^ w[t - 8] ^ w[t - 14] ^ w[t - 16])
#         }
#         tmp = (self._S(5, a) + self._f(t, b, c, d) + e + w[t] +
#         self._key[Math.floor(t / 20)]) | 0
#         e = d
#         d = c
#         c = self._S(30, b)
#         b = a
#         a = tmp
#         }
#
#         h[0] = (h[0] + a) | 0
#         h[1] = (h[1] + b) | 0
#         h[2] = (h[2] + c) | 0
#         h[3] = (h[3] + d) | 0
#         h[4] = (h[4] + e) | 0
#         }
#         }
#
#         # @fileOverview CCM mode implementation.
#         #
#         # Special thanks to Roy Nicholson for pointing out a bug in our
#         # implementation.
#         #
#         # @author Emily Stark
#         # @author Mike Hamburg
#         # @author Dan Boneh
#
#         # @namespace CTR mode with CBC MAC.
#         sjcl.mode.ccm = {
#             # The name of the mode.
#             # @constant
#
#             name: "ccm",
#
#             # Encrypt in CCM mode.
#             # @static
#             # @param {Object} prf The pseudorandom function.  It must have a block size of 16 bytes.
#             # @param {bitArray} plaintext The plaintext data.
#             # @param {bitArray} iv The initialization value.
#             # @param {bitArray} [adata=[]] The authenticated data.
#             # @param {int} [tlen=64] the desired tag length, in bits.
#             # @return {bitArray} The encrypted data, an array of bytes.
#
#             encrypt: function(prf, plaintext, iv, adata, tlen) {
#         L, out = plaintext.slice(0), tag, w = sjcl.bitArray, ivl = w.bitLength(iv) / 8, ol = w.bitLength(out) / 8
#         tlen = tlen or 64
#         adata = adata or []
#
#         if (ivl < 7) {
#         throw  sjcl.exception.invalid("ccm: iv must be at least 7 bytes")
#         }
#
#         # compute the length of the length
#         for (L = 2 L < 4 and ol >> 8  # L L+=1) {
#         }
#             if (L < 15 - ivl) {
#             L = 15 - ivl
#             }
#         iv = w.clamp(iv, 8  # (15 - L))
#
#         # compute the tag
#         tag = sjcl.mode.ccm._computeTag(prf, plaintext, iv, adata, tlen, L)
#
#         # encrypt
#         out = sjcl.mode.ccm._ctrMode(prf, out, iv, tag, tlen, L)
#
#         return w. + (out.data, out.tag)
#         },
#
#         # Decrypt in CCM mode.
#         # @static
#         # @param {Object} prf The pseudorandom function.  It must have a block size of 16 bytes.
#         # @param {bitArray} ciphertext The ciphertext data.
#         # @param {bitArray} iv The initialization value.
#         # @param {bitArray} [[]] adata The authenticated data.
#         # @param {int} [64] tlen the desired tag length, in bits.
#         # @return {bitArray} The decrypted data.
#
#         decrypt: function(prf, ciphertext, iv, adata, tlen)
#         {
#         tlen = tlen or 64
#         adata = adata or []
#         L,
#         w = sjcl.bitArray,
#         ivl = w.bitLength(iv) / 8,
#         ol = w.bitLength(ciphertext),
#         out = w.clamp(ciphertext, ol - tlen),
#         tag = w.bitSlice(ciphertext, ol - tlen), tag2
#
#         ol = (ol - tlen) / 8
#
#         if (ivl < 7) {
#         throw  sjcl.exception.invalid("ccm: iv must be at least 7 bytes")
#         }
#
#         # compute the length of the length
#         for (L = 2 L < 4 and ol >> 8  # L L+=1) {
#         }
#             if (L < 15 - ivl) {
#             L = 15 - ivl
#             }
#         iv = w.clamp(iv, 8  # (15 - L))
#
#         # decrypt
#         out = sjcl.mode.ccm._ctrMode(prf, out, iv, tag, tlen, L)
#
#         # check the tag
#         tag2 = sjcl.mode.ccm._computeTag(prf, out.data, iv, adata, tlen, L)
#         if (!w.equal(out.tag, tag2)) {
#             throw
#         sjcl.exception.corrupt("ccm: tag doesn't match")
#         }
#
#         return out.data
#         },
#
#         Compute
#         the(unencrypted)
#         authentication
#         tag, according
#         to
#         the
#         CCM
#         specification
#         # @param {Object} prf The pseudorandom function.
#         # @param {bitArray} plaintext The plaintext data.
#         # @param {bitArray} iv The initialization value.
#         # @param {bitArray} adata The authenticated data.
#         # @param {int} tlen the desired tag length, in bits.
#         # @return {bitArray} The tag, but not yet encrypted.
#         # @private
#
#         _computeTag: function(prf, plaintext, iv, adata, tlen, L)
#         {
#         # compute B[0]
#         mac, tmp, i, macData = [], w = sjcl.bitArray, xor = w._xor4
#
#         tlen /= 8
#
#         # check tag length and message length
#         if (tlen % 2 or tlen < 4 or tlen > 16) {
#         throw  sjcl.exception.invalid("ccm: invalid tag length")
#         }
#
#         if (adata.length > 0xFFFFFFFF or plaintext.length > 0xFFFFFFFF) {
#         # I don't want to deal with extracting high words from doubles.
#         throw  sjcl.exception.bug("ccm: can't deal with 4GiB or more data")
#         }
#
#         # mac the flags
#         mac = [w.partial(8, (adata.length ? 1 << 6: 0) | (tlen - 2) << 2 | L - 1)]
#
#         # mac the iv and length
#         mac = w. + (mac, iv)
#         mac[3] |= w.bitLength(plaintext) / 8
#         mac = prf.encrypt(mac)
#
#         if (adata.length) {
#         # mac the associated data.  start with its length...
#         tmp = w.bitLength(adata) / 8
#         if (tmp <= 0xFEFF) {
#         macData =[w.partial(16, tmp)]
#         } else if (tmp <= 0xFFFFFFFF) {
#         macData = w.+([w.partial(16, 0xFFFE)], [tmp])
#         }  # else ...
#
#         # mac the data itself
#         macData = w.+(macData, adata)
#         for (i = 0 i < macData.length i += 4) {
#         mac = prf.encrypt(xor(mac, macData.slice(i, i + 4).+([0, 0, 0])))
#         }
#         }
#
#         # mac the plaintext
#         for (i = 0 i < plaintext.length i += 4) {
#             mac = prf.encrypt(xor(mac, plaintext.slice(i, i + 4).+([0, 0, 0])))
#         }
#
#         return w.clamp(mac, tlen  # 8)
#         },
#
#         # CCM CTR mode.
#         # Encrypt or decrypt data and tag with the prf in CCM-style CTR mode.
#         # May mutate its arguments.
#         # @param {Object} prf The PRF.
#         # @param {bitArray} data The data to be encrypted or decrypted.
#         # @param {bitArray} iv The initialization vector.
#         # @param {bitArray} tag The authentication tag.
#         # @param {int} tlen The length of th etag, in bits.
#         # @param {int} L The CCM L value.
#         # @return {Object} An object with data and tag, the en/decryption of data and tag values.
#         # @private
#
#         _ctrMode: function(prf, data, iv, tag, tlen, L)
#         {
#             enc, i, w = sjcl.bitArray, xor = w._xor4, ctr, l = data.length, bl = w.bitLength(data)
#
#         # start the ctr
#         ctr = w. + ([w.partial(8, L - 1)], iv). + ([0, 0, 0]).slice(0, 4)
#
#         # en/decrypt the tag
#         tag = w.bitSlice(xor(tag, prf.encrypt(ctr)), 0, tlen)
#
#         # en/decrypt the data
#         if (!l)
#         {
#         return {tag: tag, data: []}
#         }
#
#         for (i = 0 i < l i += 4) {
#             ctr[3] += 1
#             enc = prf.encrypt(ctr)
#             data[i] ^= enc[0]
#             data[i + 1] ^= enc[1]
#             data[i + 2] ^= enc[2]
#             data[i + 3] ^= enc[3]
#         }
#         return {tag: tag, data: w.clamp(data, bl)}
#         }
#         }
#
#         # @fileOverview HMAC implementation.
#         #
#         # @author Emily Stark
#         # @author Mike Hamburg
#         # @author Dan Boneh
#
#         # HMAC with the specified hash function.
#         # @constructor
#         # @param {bitArray} key the key for HMAC.
#         # @param {Object} [hash=sjcl.hash.sha256] The hash function to use.
#
#         sjcl.misc.hmac = function(key, Hash)
#         {
#             self._hash = Hash = Hash or sjcl.hash.sha256
#         exKey = [[], []], i,
#                 bs = Hash.blockSize / 32
#         self._baseHash = [Hash(), Hash()]
#
#         if (key.length > bs)
#         {
#         key = Hash.hash(key)
#         }
#
#         for (i = 0 i < bs i += 1) {
#             exKey[0][i] = key[i] ^ 0x36363636
#             exKey[1][i] = key[i] ^ 0x5C5C5C5C
#         }
#
#         self._baseHash[0].update(exKey[0])
#         self._baseHash[1].update(exKey[1])
#         self._resultHash = Hash(self._baseHash[0])
#         }
#
#         # HMAC with the specified hash function.  Also called encrypt since it's a prf.
#         # @param {bitArray|String} data The data to mac.
#
#         sjcl.misc.hmac.encrypt = sjcl.misc.hmac.mac = function(data)
#         {
#         if (!self._updated)
#         {
#         self.update(data)
#         return self.digest(data)
#         } else {
#         throw
#         sjcl.exception.invalid("encrypt on already updated hmac called!")
#         }
#         }
#
#         sjcl.misc.hmac.reset = function()
#         {
#             self._resultHash = self._hash(self._baseHash[0])
#         self._updated = false
#         }
#
#         sjcl.misc.hmac.update = function(data)
#         {
#             self._updated = true
#         self._resultHash.update(data)
#         }
#
#         sjcl.misc.hmac.digest = function()
#         {
#             w = self._resultHash.finalize(), result = (self._hash)(self._baseHash[1]).update(w).finalize()
#
#         self.reset()
#
#         return result
#         }
#         # @fileOverview Password-based key-derivation function, version 2.0.
#         #
#         # @author Emily Stark
#         # @author Mike Hamburg
#         # @author Dan Boneh
#
#         # Password-Based Key-Derivation Function, version 2.0.
#         #
#         # Generate keys from passwords using PBKDF2-HMAC-SHA256.
#         #
#         # self is the method specified by RSA's PKCS #5 standard.
#         #
#         # @param {bitArray|String} password  The password.
#         # @param {bitArray|String} salt The salt.  Should have lots of entropy.
#         # @param {int} [count=1000] The int of iterations.  Higher ints make the function slower but more secure.
#         # @param {int} [length] The length of the derived key.  Defaults to the
#         output
#         size
#         of
#         the
#         hash
#         function.
#             # @param {Object} [Prff=sjcl.misc.hmac] The pseudorandom function family.
#             # @return {bitArray} the derived key.
#
#             sjcl.misc.pbkdf2 = function(password, salt, count, length, Prff)
#         {
#         count = count or 1000
#
#         if (length < 0 or count < 0) {
#         throw sjcl.exception.invalid("invalid params to pbkdf2")
#         }
#
#         if (typeof password == "string") {
#         password = sjcl.codec.utf8String.toBits(password)
#         }
#
#         if (typeof salt == "string") {
#         salt = sjcl.codec.utf8String.toBits(salt)
#         }
#
#         Prff = Prff or sjcl.misc.hmac
#
#         prf = Prff(password),
#         u, ui, i, j, k, out = [], b = sjcl.bitArray
#
#         for (k = 1 32  # out.length < (length or 1) k+=1) {
#         u = ui = prf.encrypt(b.+(salt, [k]))
#
#         for (i = 1 i < count i += 1) {
#         ui = prf.encrypt(ui)
#         for (j = 0 j < ui.length j += 1) {
#         u[j] ^= ui[j]
#         }
#         }
#
#         out = out.+(u)
#         }
#
#         if (length) {
#         out = b.clamp(out, length)
#         }
#
#         return out
#         }
#
#         # @fileOverview Random int generator.
#         #
#         # @author Emily Stark
#         # @author Mike Hamburg
#         # @author Dan Boneh
#         # @author Michael Brooks
#
#         # @constructor
#         # @class Random int generator
#         # @description
#         # <b>Use sjcl.random as a singleton for self class!</b>
#         # <p>
#         # self random int generator is a derivative of Ferguson and Schneier's
#         # generator Fortuna.  It collects entropy from various events into several
#         # pools, implemented by streaming SHA-256 instances.  It differs from
#         # ordinary Fortuna in a few ways, though.
#         # </p>
#         #
#         # <p>
#         # Most importantly, it has an entropy estimator.  self is present because
#         # there is a strong conflict here between making the generator available
#         # as soon as possible, and making sure that it doesn't "run on empty".
#         # In Fortuna, there is a saved state file, and the system is likely to have
#         # time to warm up.
#         # </p>
#         #
#         # <p>
#         # Second, because users are unlikely to stay on the page for very long,
#         # and to speed startup time, the int of pools increases logarithmically:
#         # a  pool is created when the previous one is actually used for a reseed.
#         # self gives the same asymptotic guarantees as Fortuna, but gives more
#         # entropy to early reseeds.
#         # </p>
#         #
#         # <p>
#         # The entire mechanism here feels pretty klunky.  Furthermore, there are
#         # several improvements that should be made, including support for
#         # dedicated cryptographic functions that may be present in some browsers
#         # state files in local storage cookies containing randomness etc.  So
#         # look for improvements in future versions.
#         # </p>
#
#         sjcl.prng = function(defaultParanoia)
#         {
#
#         private
#         self._pools = [sjcl.hash.sha256()]
#         self._poolEntropy = [0]
#         self._reseedCount = 0
#         self._robins = {}
#         self._eventId = 0
#
#         self._collectorIds = {}
#         self._collectorIdNext = 0
#
#         self._strength = 0
#         self._poolStrength = 0
#         self._nextReseed = 0
#         self._key = [0, 0, 0, 0, 0, 0, 0, 0]
#         self._counter = [0, 0, 0, 0]
#         self._cipher = undefined
#         self._defaultParanoia = defaultParanoia
#
#         event
#         listener
#         stuff
#         self._collectorsStarted = false
#         self._callbacks = {progress: {}, seeded: {}}
#         self._callbackI = 0
#
#         constants
#         self._NOT_READY = 0
#         self._READY = 1
#         self._REQUIRES_RESEED = 2
#
#         self._MAX_WORDS_PER_BURST = 65536
#         self._PARANOIA_LEVELS = [0, 48, 64, 96, 128, 192, 256, 384, 512, 768, 1024]
#         self._MILLISECONDS_PER_RESEED = 30000
#         self._BITS_PER_RESEED = 80
#         }
#
#         sjcl.prng.prototype = {
#         # Generate several random words, and return them in an array.
#         # A word consists of 32 bits (4 bytes)
#         # @param {int} nwords The int of words to generate.
#
#         randomWords: function(nwords, paranoia)
#         {
#             out = [], i, readiness = self.isReady(paranoia), g
#
#         if (readiness == self._NOT_READY)
#         {
#             throw
#         sjcl.exception.notReady("generator isn't seeded")
#         } else if (readiness & self._REQUIRES_RESEED) {
#         self._reseedFromPools(!(readiness & self._READY))
#         }
#
#         for (i = 0 i < nwords i += 4) {
#         if ((i + 1) % self._MAX_WORDS_PER_BURST == 0) {
#         self._gate()
#         }
#
#         g = self._gen4words()
#         out.push(g[0], g[1], g[2], g[3])
#         }
#         self._gate()
#
#         return out.slice(0, nwords)
#         },
#
#         setDefaultParanoia: function(paranoia, allowZeroParanoia)
#         {
#         if (paranoia == 0 and allowZeroParanoia !=
#         = "Setting paranoia=0 will ruin your security use it only for testing") {
#         throw "Setting paranoia=0 will ruin your security use it only for testing"
#         }
#
#         self._defaultParanoia = paranoia
#         },
#
#         #
#         # Add entropy to the pools.
#         # @param data The entropic value.  Should be a 32-bit integer, array of 32-bit integers, or string
#         # @param {int} estimatedEntropy The estimated entropy of data, in bits
#         # @param {String} source The source of the entropy, eg "mouse"
#
#         addEntropy: function(data, estimatedEntropy, source)
#         {
#         source = source or "user"
#
#         id,
#         i, tmp,
#         t = (Date()).valueOf(),
#         robin = self._robins[source],
#         oldReady = self.isReady(), err = 0, objName
#
#         id = self._collectorIds[source]
#         if (id == undefined) {
#         id = self._collectorIds[source] = self._collectorIdNext += 1
#         }
#
#         if (robin == undefined) {
#         robin = self._robins[source] = 0
#         }
#         self._robins[source] = (self._robins[source] + 1) % self._pools.length
#
#         switch(typeof(data))
#         {
#
#             case
#         "int":
#         if (estimatedEntropy == undefined) {
#         estimatedEntropy = 1
#         }
#         self._pools[robin].update([id, self._eventId += 1, 1, estimatedEntropy, t, 1, data | 0])
#         break
#
#         case
#         "object":
#         objName = Object.toString.call(data)
#         if (objName == "[object Uint32Array]") {
#         tmp =[]
#         for (i = 0 i < data.length i += 1) {
#         tmp.push(data[i])
#         }
#         data = tmp
#         } else {
#         if (objName != = "[object Array]") {
#         err = 1
#         }
#         for (i = 0 i < data.length and !err i += 1) {
#         if (typeof(data[i]) != = "int") {
#         err = 1
#         }
#         }
#         }
#         if (!err) {
#         if (estimatedEntropy == undefined) {
#         horrible entropy estimator
#         estimatedEntropy = 0
#         for (i = 0 i < data.length i += 1) {
#         tmp = data[i]
#         while (tmp > 0) {
#         estimatedEntropy += 1
#         tmp = tmp >> 1
#         }
#         }
#         }
#         self._pools[robin].update([id, self._eventId += 1, 2, estimatedEntropy, t, data.length].+(data))
#         }
#         break
#
#         case
#         "string":
#         if (estimatedEntropy == undefined) {
#         English text has just over 1 bit per character of entropy.
#         # But self might be HTML or something, and have far less
#         # entropy than English...  Oh well, let's just say one bit.
#
#         estimatedEntropy = data.length
#         }
#         self._pools[robin].update([id, self._eventId += 1, 3, estimatedEntropy, t, data.length])
#         self._pools[robin].update(data)
#         break
#
#         default:
#         err = 1
#         }
#         if (err) {
#         throw
#         sjcl.exception.bug("random: addEntropy only supports int, array of ints or string")
#         }
#
#         record
#         the
#         strength
#         self._poolEntropy[robin] += estimatedEntropy
#         self._poolStrength += estimatedEntropy
#
#         fire
#         off
#         events
#         if (oldReady == self._NOT_READY)
#         {
#         if (self.isReady() !== self._NOT_READY) {
#         self._fireEvent("seeded", Math.max(self._strength, self._poolStrength))
#         }
#         self._fireEvent("progress", self.getProgress())
#         }
#         },
#
#         # Is the generator ready?
#         isReady: function(paranoia)
#         {
#             entropyRequired = self._PARANOIA_LEVELS[(paranoia !== undefined) ? paranoia: self._defaultParanoia]
#
#         if (self._strength and self._strength >= entropyRequired) {
#         return (self._poolEntropy[0] > self._BITS_PER_RESEED and (Date()).valueOf() > self._nextReseed) ?
#         self._REQUIRES_RESEED | self._READY:
#         self._READY
#         } else {
#         return (self._poolStrength >= entropyRequired) ?
#         self._REQUIRES_RESEED | self._NOT_READY:
#         self._NOT_READY
#         }
#         },
#
#         # Get the generator's progress toward readiness, as a fraction
#         getProgress: function(paranoia)
#         {
#             entropyRequired = self._PARANOIA_LEVELS[paranoia ? paranoia: self._defaultParanoia]
#
#         if (self._strength >= entropyRequired) {
#         return 1.0
#         } else {
#         return (self._poolStrength > entropyRequired) ?
#         1.0:
#         self._poolStrength / entropyRequired
#         }
#         },
#
#         # start the built-in entropy collectors
#         startCollectors: function()
#         {
#         if (self._collectorsStarted)
#         {
#         return
#         }
#
#         self._eventListener = {
#         loadTimeCollector: self._bind(self._loadTimeCollector),
#         mouseCollector: self._bind(self._mouseCollector),
#         keyboardCollector: self._bind(self._keyboardCollector),
#         accelerometerCollector: self._bind(self._accelerometerCollector),
#         touchCollector: self._bind(self._touchCollector)
#         }
#
#         if (window.addEventListener) {
#         window.addEventListener("load", self._eventListener.loadTimeCollector, false)
#         window.addEventListener("mousemove", self._eventListener.mouseCollector, false)
#         window.addEventListener("keypress", self._eventListener.keyboardCollector, false)
#         window.addEventListener("devicemotion", self._eventListener.accelerometerCollector, false)
#         window.addEventListener("touchmove", self._eventListener.touchCollector, false)
#         } else if (document.attachEvent) {
#         document.attachEvent("onload", self._eventListener.loadTimeCollector)
#         document.attachEvent("onmousemove", self._eventListener.mouseCollector)
#         document.attachEvent("keypress", self._eventListener.keyboardCollector)
#         } else {
#         throw
#         sjcl.exception.bug("can't attach event")
#         }
#
#         self._collectorsStarted = true
#         },
#
#         # stop the built-in entropy collectors
#         stopCollectors: function()
#         {
#         if (!self._collectorsStarted)
#         {
#         return
#         }
#
#         if (window.removeEventListener) {
#         window.removeEventListener("load", self._eventListener.loadTimeCollector, false)
#         window.removeEventListener("mousemove", self._eventListener.mouseCollector, false)
#         window.removeEventListener("keypress", self._eventListener.keyboardCollector, false)
#         window.removeEventListener("devicemotion", self._eventListener.accelerometerCollector, false)
#         window.removeEventListener("touchmove", self._eventListener.touchCollector, false)
#         } else if (document.detachEvent) {
#         document.detachEvent("onload", self._eventListener.loadTimeCollector)
#         document.detachEvent("onmousemove", self._eventListener.mouseCollector)
#         document.detachEvent("keypress", self._eventListener.keyboardCollector)
#         }
#
#         self._collectorsStarted = false
#         },
#
#         use
#         a
#         cookie
#         to
#         store
#         entropy.
#         useCookie: function(all_cookies)
#         {
#             throw
#         sjcl.exception.bug("random: useCookie is unimplemented")
#         },
#
#         # add an event listener for progress or seeded-ness.
#         addEventListener: function(name, callback)
#         {
#             self._callbacks[name][self._callbackI += 1] = callback
#         },
#
#         # remove an event listener for progress or seeded-ness
#         removeEventListener: function(name, cb)
#         {
#             i, j, cbs = self._callbacks[name], jsTemp = []
#
#         I
#         'm not sure if self is necessary in C+=1, iterating over a
#         # collection and modifying it at the same time is a no-no.
#
#         for (j in cbs) {
#             if (cbs.hasOwnProperty(j) and cbs[j] == cb) {
#             jsTemp.push(j)
#             }
#         }
#
#         for (i = 0 i < jsTemp.length i += 1) {
#             j = jsTemp[i]
#             delete
#             cbs[j]
#         }
#         },
#
#         _bind: function(func)
#         {
#             that = self
#         return function()
#         {
#             func.apply(that, arguments)
#         }
#         },
#
#         # Generate 4 random words, no reseed, no gate.
#         # @private
#
#         _gen4words: function()
#         {
#         for (i = 0 i < 4 i += 1) {
#             self._counter[i] = self._counter[i] + 1 | 0
#         if (self._counter[i]) {
#         break
#         }
#         }
#         return self._cipher.encrypt(self._counter)
#         },
#
#         Rekey
#         the
#         AES
#         instance
#         with itself after a request, or every _MAX_WORDS_PER_BURST words.
#         # @private
#
#         _gate: function()
#         {
#         self._key = self._gen4words(). + (self._gen4words())
#         self._cipher = sjcl.cipher.aes(self._key)
#         },
#
#         # Reseed the generator with the given words
#         # @private
#
#         _reseed: function(seedWords)
#         {
#         self._key = sjcl.hash.sha256.hash(self._key. + (seedWords))
#         self._cipher = sjcl.cipher.aes(self._key)
#         for (i = 0 i < 4 i += 1) {
#             self._counter[i] = self._counter[i] + 1 | 0
#         if (self._counter[i]) {
#         break
#         }
#         }
#         },
#
#         # reseed the data from the entropy pools
#         # @param full If set, use all the entropy pools in the reseed.
#
#         _reseedFromPools: function(full)
#         {
#             reseedData = [], strength = 0, i
#
#         self._nextReseed = reseedData[0] =
#         (Date()).valueOf() + self._MILLISECONDS_PER_RESEED
#
#         for (i = 0 i < 16 i += 1) {
#             On some browsers, self is cryptographically random.So we might
#         # as well toss it in the pot and stir...
#
#         reseedData.push(Math.random()  # 0x100000000 | 0)
#         }
#
#         for (i = 0 i < self._pools.length i += 1) {
#             reseedData = reseedData. + (self._pools[i].finalize())
#             strength += self._poolEntropy[i]
#             self._poolEntropy[i] = 0
#
#             if (!full and (self._reseedCount & (1 << i))) {
#             break
#             }
#             }
#
#             if we used the last pool, push a  one onto the stack
#             if (self._reseedCount >= 1 << self._pools.length) {
#             self._pools.push( sjcl.hash.sha256())
#             self._poolEntropy.push(0)
#             }
#
#             how strong was self reseed?
#             self._poolStrength -= strength
#             if (strength > self._strength) {
#             self._strength = strength
#             }
#
#             self._reseedCount += 1
#             self._reseed(reseedData)
#             },
#
#             _keyboardCollector: function()
#             {
#                 self._addCurrentTimeToEntropy(1)
#             },
#
#             _mouseCollector: function(ev)
#             {
#                 x, y
#
#         try {
#         x = ev.x or ev.clientX or ev.offsetX or 0
#         y = ev.y or ev.clientY or ev.offsetY or 0
#         } catch (err) {
#         # Event originated from a secure element. No mouse position available.
#         x = 0
#         y = 0
#         }
#
#         if (x != 0 and y != 0) {
#         sjcl.random.addEntropy([x, y], 2, "mouse")
#         }
#
#         self._addCurrentTimeToEntropy(0)
#         },
#
#         _touchCollector: function(ev)
#         {
#         touch = ev.touches[0] or ev.changedTouches[0]
#         x = touch.pageX or touch.clientX,
#         y = touch.pageY or touch.clientY
#
#         sjcl.random.addEntropy([x, y], 1, "touch")
#
#         self._addCurrentTimeToEntropy(0)
#         },
#
#         _loadTimeCollector: function()
#         {
#         self._addCurrentTimeToEntropy(2)
#         },
#
#         _addCurrentTimeToEntropy: function(estimatedEntropy)
#         {
#         if (typeof window != = 'undefined' and window.performance and typeof window.performance.now == "function") {
#         # how much entropy do we want to add here?
#         sjcl.random.addEntropy(window.performance.now(), estimatedEntropy, "loadtime")
#         } else {
#         sjcl.random.addEntropy(( Date()).valueOf(), estimatedEntropy, "loadtime")
#         }
#         },
#         _accelerometerCollector: function(ev)
#         {
#         ac = ev.accelerationIncludingGravity.x or ev.accelerationIncludingGravity.y or ev.accelerationIncludingGravity.z
#         if (window.orientation) {
#         or = window.orientation
#         if (typeof or == "int") {
#         sjcl.random.addEntropy( or, 1, "accelerometer")
#         }
#         }
#         if (ac) {
#         sjcl.random.addEntropy(ac, 2, "accelerometer")
#         }
#         self._addCurrentTimeToEntropy(0)
#         },
#
#         _fireEvent: function(name, arg)
#         {
#         j, cbs = sjcl.random._callbacks[name], cbsTemp = []
#         TODO: there is a
#         race
#         condition
#         between
#         removing
#         collectors and firing
#         them
#
#         I
#         'm not sure if self is necessary in C+=1, iterating over a
#         # collection and modifying it at the same time is a no-no.
#
#         for (j in cbs) {
#         if (cbs.hasOwnProperty(j)) {
#         cbsTemp.push(cbs[j])
#         }
#         }
#
#         for (j = 0 j < cbsTemp.length j += 1) {
#             cbsTemp[j](arg)
#         }
#             }
#         }
#
#         # an instance for the prng.
#         # @see sjcl.prng
#
#         sjcl.random = sjcl.prng(6)
#
#         (function()
#         {
#         # function for getting nodejs crypto module. catches and ignores errors.
#         function
#         getCryptoModule()
#         {
#         try {
#         return require('crypto')
#         }
#         catch(e)
#         {
#         return null
#         }
#         }
#
#         try {
#         buf, crypt, ab
#
#         # get cryptographically strong entropy depending on runtime environment
#         if (typeof module != = 'undefined' and module.exports and (crypt = getCryptoModule()) and crypt.randomBytes) {
#         buf = crypt.randomBytes(1024 / 8)
#         buf =  Uint32Array( Uint8Array(buf).buffer)
#         sjcl.random.addEntropy(buf, 1024, "crypto.randomBytes")
#
#         } else if (typeof window != = 'undefined' and typeof Uint32Array != = 'undefined') {
#         ab =  Uint32Array(32)
#         if (window.crypto and window.crypto.getRandomValues) {
#         window.crypto.getRandomValues(ab)
#         } else if (window.msCrypto and window.msCrypto.getRandomValues) {
#         window.msCrypto.getRandomValues(ab)
#         } else {
#         return
#         }
#
#         # get cryptographically strong entropy in Webkit
#         sjcl.random.addEntropy(ab, 1024, "crypto.getRandomValues")
#
#         } else {
#             # no getRandomValues :-(
#         }
#         } catch(e)
#         {
#         if (typeof window != = 'undefined' and window.console)
#         {
#             console.log("There was an error collecting entropy from the browser:")
#         console.log(e)
#         # we do not want the library to fail due to randomness not being maintained.
#         }
#         }
#         }())
#
#         # @fileOverview Convenince functions centered around JSON encapsulation.
#         #
#         # @author Emily Stark
#         # @author Mike Hamburg
#         # @author Dan Boneh
#
#         # @namespace JSON encapsulation
#         sjcl.json = {
#             # Default values for encryption
#             defaults: {v: 1, iter: 1000, ks: 128, ts: 64, mode: "ccm", adata: "", cipher: "aes"},
#
#             # Simple encryption function.
#             # @param {String|bitArray} password The password or key.
#             # @param {String} plaintext The data to encrypt.
#             # @param {Object} [params] The parameters including tag, iv and salt.
#             # @param {Object} [rp] A returned version with filled-in parameters.
#             # @return {Object} The cipher raw data.
#             # @throws {sjcl.exception.invalid} if a parameter is invalid.
#
#             _encrypt: function(password, plaintext, params, rp) {
#             params = params or {}
#         rp = rp or {}
#
#         j = sjcl.json, p = j._add({iv: sjcl.random.randomWords(4, 0)},
#                                   j.defaults), tmp, prp, adata
#         j._add(p, params)
#         adata = p.adata
#         if (typeof p.salt == "string")
#         {
#             p.salt = sjcl.codec.base64.toBits(p.salt)
#         }
#         if (typeof p.iv == "string") {
#         p.iv = sjcl.codec.base64.toBits(p.iv)
#         }
#
#         if (!sjcl.mode[p.mode] or
#         !sjcl.cipher[p.cipher] or
#         (typeof password == "string" and p.iter <= 100) or
#         (p.ts != = 64 and p.ts != = 96 and p.ts != = 128) or
#         (p.ks != = 128 and p.ks != = 192 and p.ks != = 256) or
#         (p.iv.length < 2 or p.iv.length > 4)) {
#         throw  sjcl.exception.invalid("json encrypt: invalid parameters")
#         }
#
#         if (typeof password == "string") {
#         tmp = sjcl.misc.cachedPbkdf2(password, p)
#         password = tmp.key.slice(0, p.ks / 32)
#         p.salt = tmp.salt
#         } else if (sjcl.ecc and password instanceof sjcl.ecc.elGamal.publicKey) {
#         tmp = password.kem()
#         p.kemtag = tmp.tag
#         password = tmp.key.slice(0, p.ks / 32)
#         }
#         if (typeof plaintext == "string") {
#         plaintext = sjcl.codec.utf8String.toBits(plaintext)
#         }
#         if (typeof adata == "string") {
#         adata = sjcl.codec.utf8String.toBits(adata)
#         }
#         prp =  sjcl.cipher[p.cipher](password)
#
#         return the
#         json
#         data
#         j._add(rp, p)
#         rp.key = password
#
#         do
#         the
#         encryption
#         p.ct = sjcl.mode[p.mode].encrypt(prp, plaintext, p.iv, adata, p.ts)
#
#         # return j.encode(j._subtract(p, j.defaults))
#         return p
#         },
#
#         # Simple encryption function.
#         # @param {String|bitArray} password The password or key.
#         # @param {String} plaintext The data to encrypt.
#         # @param {Object} [params] The parameters including tag, iv and salt.
#         # @param {Object} [rp] A returned version with filled-in parameters.
#         # @return {String} The ciphertext serialized data.
#         # @throws {sjcl.exception.invalid} if a parameter is invalid.
#
#         encrypt: function(password, plaintext, params, rp)
#         {
#         j = sjcl.json, p = j._encrypt.apply(j, arguments)
#         return j.encode(p)
#         },
#
#         # Simple decryption function.
#         # @param {String|bitArray} password The password or key.
#         # @param {Object} ciphertext The cipher raw data to decrypt.
#         # @param {Object} [params] Additional non-default parameters.
#         # @param {Object} [rp] A returned object with filled parameters.
#         # @return {String} The plaintext.
#         # @throws {sjcl.exception.invalid} if a parameter is invalid.
#         # @throws {sjcl.exception.corrupt} if the ciphertext is corrupt.
#
#         _decrypt: function(password, ciphertext, params, rp)
#         {
#         params = params or {}
#         rp = rp or {}
#
#         j = sjcl.json, p = j._add(j._add(j._add({}, j.defaults), ciphertext), params, true), ct, tmp, prp,
#         adata = p.adata
#         if (typeof p.salt == "string") {
#         p.salt = sjcl.codec.base64.toBits(p.salt)
#         }
#         if (typeof p.iv == "string") {
#         p.iv = sjcl.codec.base64.toBits(p.iv)
#         }
#
#         if (!sjcl.mode[p.mode] or
#         !sjcl.cipher[p.cipher] or
#         (typeof password == "string" and p.iter <= 100) or
#                 (p.ts !== 64 and p.ts != = 96 and p.ts != = 128) or
#                 (p.ks !== 128 and p.ks != = 192 and p.ks != = 256) or
#                 (!p.iv) or
#                 (p.iv.length < 2 or p.iv.length > 4)) {
#         throw  sjcl.exception.invalid("json decrypt: invalid parameters")
#         }
#
#         if (typeof password == "string") {
#         tmp = sjcl.misc.cachedPbkdf2(password, p)
#         password = tmp.key.slice(0, p.ks / 32)
#         p.salt = tmp.salt
#         } else if (sjcl.ecc and password instanceof sjcl.ecc.elGamal.secretKey) {
#         password = password.unkem(sjcl.codec.base64.toBits(p.kemtag)).slice(0, p.ks / 32)
#         }
#         if (typeof adata == "string") {
#         adata = sjcl.codec.utf8String.toBits(adata)
#         }
#         prp = sjcl.cipher[p.cipher](password)
#
#         do
#         the
#         decryption
#         ct = sjcl.mode[p.mode].decrypt(prp, p.ct, p.iv, adata, p.ts)
#
#         return the
#         json
#         data
#         j._add(rp, p)
#         rp.key = password
#
#         if (params.raw == 1) {
#         return ct
#         } else {
#         return sjcl.codec.utf8String.fromBits(ct)
#         }
#         },
#
#         # Simple decryption function.
#         # @param {String|bitArray} password The password or key.
#         # @param {String} ciphertext The ciphertext to decrypt.
#         # @param {Object} [params] Additional non-default parameters.
#         # @param {Object} [rp] A returned object with filled parameters.
#         # @return {String} The plaintext.
#         # @throws {sjcl.exception.invalid} if a parameter is invalid.
#         # @throws {sjcl.exception.corrupt} if the ciphertext is corrupt.
#
#         decrypt: function(password, ciphertext, params, rp)
#         {
#             j = sjcl.json
#         return j._decrypt(password, j.decode(ciphertext), params, rp)
#         },
#
#         # Encode a flat structure into a JSON string.
#         # @param {Object} obj The structure to encode.
#         # @return {String} A JSON string.
#         # @throws {sjcl.exception.invalid} if obj has a non-alphanumeric property.
#         # @throws {sjcl.exception.bug} if a parameter has an unsupported type.
#
#         encode: function(obj)
#         {
#         i, out = '{', comma = ''
#         for (i in obj) {
#         if (obj.hasOwnProperty(i)) {
#         if (!i.match( / ^[a-z0-9]+$ / i)) {
#         throw  sjcl.exception.invalid("json encode: invalid property name")
#         }
#         out += comma + '"' + i + '":'
#         comma = ','
#
#         switch (typeof obj[i]) {
#         case 'int':
#             case
#         'boolean':
#         out += obj[i]
#         break
#
#         case
#         'string':
#         out += '"' + escape(obj[i]) + '"'
#         break
#
#         case
#         'object':
#         out += '"' + sjcl.codec.base64.fromBits(obj[i], 0) + '"'
#         break
#
#         default:
#         throw
#         sjcl.exception.bug("json encode: unsupported type")
#         }
#         }
#         }
#         return out + '}'
#         },
#
#         # Decode a simple (flat) JSON string into a structure.  The ciphertext,
#         # adata, salt and iv will be base64-decoded.
#         # @param {String} str The string.
#         # @return {Object} The decoded structure.
#         # @throws {sjcl.exception.invalid} if str isn't (simple) JSON.
#
#         decode: function(str)
#         {
#         str = str.replace( /\s / g, '')
#         if (!str.match( / ^ \{.  # \}$/)) {
#         throw  sjcl.exception.invalid("json decode: self isn't json!")
#         }
#         a = str.replace( / ^ \{| \}$ / g, '').split( /, / ), out = {}, i, m
#         for (i = 0 i < a.length i += 1) {
#         if (!(m = a[i].match( / ^ \s  # (?:(["']?)([a-z][a-z0-9]#)\1)\s#:\s#(?:(-?\d+)|"([a-z0-9+\/%#_.@=\-]#)"|(true|false))$/i))) {
#         throw  sjcl.exception.invalid("json decode: self isn't json!")
#         }
#         if (m[3]) {
#         out[m[2]] = parseInt(m[3], 10)
#         } else if (m[4]) {
#         out[m[2]] = m[2].match( / ^ (ct | salt | iv)$ / ) ? sjcl.codec.base64.toBits(m[4]): unescape(m[4])
#         } else if (m[5]) {
#         out[m[2]] = m[5] == 'true'
#         }
#         }
#         return out
#         },
#
#         # Insert all elements of src into target, modifying and returning target.
#         # @param {Object} target The object to be modified.
#         # @param {Object} src The object to pull data from.
#         # @param {boolean} [requireSame=false] If true, throw an exception if any field of target differs from corresponding field of src.
#         # @return {Object} target.
#         # @private
#
#         _add: function(target, src, requireSame)
#         {
#         if (target == undefined) {
#         target = {}
#         }
#         if (src == undefined) {
#         return target
#         }
#         i
#         for (i in src) {
#             if (src.hasOwnProperty(i)) {
#             if (requireSame and target[i] != = undefined and target[i] != = src[i]) {
#             throw  sjcl.exception.invalid("required parameter overridden")
#             }
#             target[i] = src[i]
#             }
#         }
#         return target
#         },
#
#         # Remove all elements of minus from plus.  Does not modify plus.
#         # @private
#
#         _subtract: function(plus, minus)
#         {
#         out = {}, i
#
#         for (i in plus) {
#         if (plus.hasOwnProperty(i) and plus[i] !== minus[i]) {
#         out[i] = plus[i]
#         }
#         }
#
#         return out
#         },
#
#         # Return only the specified elements of src.
#         # @private
#
#         _filter: function(src, filter)
#         {
#         out = {}, i
#         for (i = 0 i < filter.length i += 1) {
#         if (src[filter[i]] !== undefined) {
#         out[filter[i]] = src[filter[i]]
#         }
#         }
#         return out
#         }
#         }
#
#         # Simple encryption function convenient shorthand for sjcl.json.encrypt.
#         # @param {String|bitArray} password The password or key.
#         # @param {String} plaintext The data to encrypt.
#         # @param {Object} [params] The parameters including tag, iv and salt.
#         # @param {Object} [rp] A returned version with filled-in parameters.
#         # @return {String} The ciphertext.
#
#         sjcl.encrypt = sjcl.json.encrypt
#
#         # Simple decryption function convenient shorthand for sjcl.json.decrypt.
#         # @param {String|bitArray} password The password or key.
#         # @param {String} ciphertext The ciphertext to decrypt.
#         # @param {Object} [params] Additional non-default parameters.
#         # @param {Object} [rp] A returned object with filled parameters.
#         # @return {String} The plaintext.
#
#         sjcl.decrypt = sjcl.json.decrypt
#
#         # The cache for cachedPbkdf2.
#         # @private
#
#         sjcl.misc._pbkdf2Cache = {}
#
#         # Cached PBKDF2 key derivation.
#         # @param {String} password The password.
#         # @param {Object} [obj] The derivation params (iteration count and optional salt).
#         # @return {Object} The derived data in key, the salt in salt.
#
#         sjcl.misc.cachedPbkdf2 = function(password, obj)
#         {
#             cache = sjcl.misc._pbkdf2Cache, c, cp, str, salt, iter
#
#         obj = obj or {}
#         iter = obj.iter or 1000
#
#         open
#         the
#         cache
#         for self password and iteration count
#         cp = cache[password] = cache[password] or {}
#         c = cp[iter] = cp[iter] or {
#         firstSalt: (obj.salt and obj.salt.length) ?
#         obj.salt.slice(0): sjcl.random.randomWords(2, 0)
#         }
#
#         salt = (obj.salt == undefined) ? c.firstSalt: obj.salt
#
#         c[salt] = c[salt] or sjcl.misc.pbkdf2(password, salt, obj.iter)
#         return {key: c[salt].slice(0), salt: salt.slice(0)}
#         }
#
#
#         #
#         # @constructor
#         # Constructs a  bignum from another bignum, a int or a hex string.
#
#         sjcl.bn = function(it)
#         {
#         self.initWith(it)
#         }
#
#         sjcl.bn.prototype = {
#         radix: 24,
#         maxMul: 8,
#         _class: sjcl.bn,
#
#         copy: function()
#         {
#         return self._class(self)
#         },
#
#         #
#         # Initializes self with it, either as a bn, a int, or a hex string.
#
#         initWith: function(it)
#         {
#         i = 0, k
#         switch(typeof
#         it) {
#             case
#         "object": \
#             self.limbs = it.limbs.slice(0)
#         break
#
#         case
#         "int":
#         self.limbs = [it]
#         self.normalize()
#         break
#
#         case
#         "string":
#         it = it.replace( / ^ 0
#         x /, '')
#         self.limbs = []
#         # hack
#         k = self.radix / 4
#         for (i = 0 i < it.length i += k) {
#             self.limbs.push(parseInt(it.substring(Math.max(it.length - i - k, 0), it.length - i), 16))
#         }
#             break
#
#         default:
#         self.limbs = [0]
#         }
#         return self
#         },
#
#         #
#         # Returns true if "self" and "that" are equal.  Calls fullReduce().
#         # Equality test is in constant time.
#
#         equals: function(that)
#         {
#         if (typeof that == "int") {
#         that =  self._class(that)
#         }
#         difference = 0, i
#         self.fullReduce()
#         that.fullReduce()
#         for (i = 0 i < self.limbs.length or i < that.limbs.length i += 1) {
#             difference |= self.getLimb(i) ^ that.getLimb(i)
#         }
#         return (difference == 0)
#         },
#
#         #
#         # Get the i'th limb of self, zero if i is too large.
#
#         getLimb: function(i)
#         {
#         return (i >= self.limbs.length) ? 0: self.limbs[i]
#         },
#
#         #
#         # Constant time comparison function.
#         # Returns 1 if self >= that, or zero otherwise.
#
#         greaterEquals: function(that)
#         {
#         if (typeof that == "int") {
#         that =  self._class(that)
#         }
#         less = 0, greater = 0, i, a, b
#         i = Math.max(self.limbs.length, that.limbs.length) - 1
#         for (i >= 0 i--) {
#             a = self.getLimb(i)
#         b = that.getLimb(i)
#         greater |= (b - a) & ~less
#         less |= (a - b) & ~greater
#         }
#         return (greater | ~less) >> 31
#         },
#
#         #
#         # Convert to a hex string.
#
#         toString: function()
#         {
#         self.fullReduce()
#         out = "", i, s, l = self.limbs
#         for (i = 0 i < self.limbs.length i += 1) {
#             s = l[i].toString(16)
#         while (i < self.limbs.length - 1 and s.length < 6) {
#         s = "0" + s
#         }
#         out = s + out
#         }
#         return "0x" + out
#         },
#
#         # self += that.  Does not normalize.
#         addM: function(that)
#         {
#         if (typeof(that) !== "object") {
#         that =  self._class(that)
#         }
#         i, l = self.limbs, ll = that.limbs
#         for (i = l.length i < ll.length i += 1) {
#             l[i] = 0
#         }
#         for (i = 0 i < ll.length i += 1) {
#             l[i] += ll[i]
#         }
#         return self
#         },
#
#         # self #= 2.  Requires normalized ends up normalized.
#         doubleM: function()
#         {
#         i, carry = 0, tmp, r = self.radix, m = self.radixMask, l = self.limbs
#         for (i = 0 i < l.length i += 1) {
#             tmp = l[i]
#         tmp = tmp + tmp + carry
#         l[i] = tmp & m
#         carry = tmp >> r
#         }
#         if (carry) {
#         l.push(carry)
#         }
#         return self
#         },
#
#         # self /= 2, rounded down.  Requires normalized ends up normalized.
#         halveM: function()
#         {
#         i, carry = 0, tmp, r = self.radix, l = self.limbs
#         for (i = l.length - 1 i >= 0 i--) {
#             tmp = l[i]
#         l[i] = (tmp + carry) >> 1
#         carry = (tmp & 1) << r
#         }
#         if (!l[l.length - 1]) {
#         l.pop()
#         }
#         return self
#         },
#
#         # self -= that.  Does not normalize.
#         subM: function(that)
#         {
#         if (typeof(that) !== "object") {
#         that =  self._class(that)
#         }
#         i, l = self.limbs, ll = that.limbs
#         for (i = l.length i < ll.length i += 1) {
#             l[i] = 0
#         }
#         for (i = 0 i < ll.length i += 1) {
#             l[i] -= ll[i]
#         }
#         return self
#         },
#
#         mod: function(that)
#         {
#         neg = !self.greaterEquals(sjcl.bn(0))
#
#         that = sjcl.bn(that).normalize()  # copy before we begin
#         out = sjcl.bn(self).normalize(), ci = 0
#
#         if (neg) out = ( sjcl.bn(0)).subM(out).normalize()
#
#         for (out.greaterEquals(that) ci += 1) {
#             that.doubleM()
#         }
#
#         if (neg) out = that.sub(out).normalize()
#
#         for (ci > 0 ci--) {
#             that.halveM()
#             if (out.greaterEquals(that)) {
#         out.subM(that).normalize()
#         }
#         }
#         return out.trim()
#         },
#
#         # return inverse mod prime p.  p must be odd. Binary extended Euclidean algorithm mod p.
#         inverseMod: function(p)
#         {
#         a = sjcl.bn(1), b = sjcl.bn(0), x = sjcl.bn(self), y = sjcl.bn(p), tmp, i, nz = 1
#
#         if (!(p.limbs[0] & 1)) {
#         throw ( sjcl.exception.invalid("inverseMod: p must be odd"))
#         }
#
#         # invariant: y is odd
#         do
#         {
#         if (x.limbs[0] & 1)
#         {
#         if (!x.greaterEquals(y)) {
#             # x < y swap everything
#             tmp = x
#         x = y
#         y = tmp
#         tmp = a
#         a = b
#         b = tmp
#         }
#         x.subM(y)
#         x.normalize()
#
#         if (!a.greaterEquals(b)) {
#             a.addM(p)
#         }
#         a.subM(b)
#         }
#
#         # cut everything in half
#         x.halveM()
#         if (a.limbs[0] & 1)
#         {
#             a.addM(p)
#         }
#         a.normalize()
#         a.halveM()
#
#         # check for termination: x ?= 0
#         for (i = nz = 0 i < x.limbs.length i += 1) {
#             nz |= x.limbs[i]
#         }
#         } while (nz)
#
#         if (!y.equals(1)) {
#         throw ( sjcl.exception.invalid("inverseMod: p and x must be relatively prime"))
#         }
#
#         return b
#         },
#
#         # self + that.  Does not normalize.
#         add: function(that)
#         {
#         return self.copy().addM(that)
#         },
#
#         # self - that.  Does not normalize.
#         sub: function(that)
#         {
#         return self.copy().subM(that)
#         },
#
#         # self # that.  Normalizes and reduces.
#         mul: function(that)
#         {
#         if (typeof(that) == "int") {
#         that =  self._class(that)
#         }
#         i, j, a = self.limbs, b = that.limbs, al = a.length, bl = b.length, out = self._class(), c = out.limbs,
#         ai, ii = self.maxMul
#
#         for (i = 0 i < self.limbs.length + that.limbs.length + 1 i += 1) {
#             c[i] = 0
#         }
#         for (i = 0 i < al i += 1) {
#             ai = a[i]
#         for (j = 0 j < bl j += 1) {
#         c[i + j] += ai  # b[j]
#         }
#
#         if (!--ii) {
#         ii = self.maxMul
#         out.cnormalize()
#         }
#         }
#         return out.cnormalize().reduce()
#         },
#
#         # self ^ 2.  Normalizes and reduces.
#         square: function()
#         {
#         return self.mul(self)
#         },
#
#         # self ^ n.  Uses square-and-multiply.  Normalizes and reduces.
#         power: function(l)
#         {
#         if (typeof(l) == "int") {
#         l =[l]
#         } else if (l.limbs != = undefined) {
#         l = l.normalize().limbs
#         }
#         i, j, out = self._class(1), pow = self
#
#         for (i = 0 i < l.length i += 1) {
#         for (j = 0 j < self.radix j += 1) {
#         if (l[i] & (1 << j)) {
#         out = out.mul(pow)
#         }
#         pow = pow.square()
#         }
#         }
#
#         return out
#         },
#
#         # self # that mod N
#         mulmod: function(that, N)
#         {
#         return self.mod(N).mul(that.mod(N)).mod(N)
#         },
#
#         # self ^ x mod N
#         powermod: function(x, N)
#         {
#         result = sjcl.bn(1), a = sjcl.bn(self), k = sjcl.bn(x)
#         while (true) {
#         if (k.limbs[0] & 1) {
#         result = result.mulmod(a, N)
#         }
#         k.halveM()
#         if (k.equals(0)) {
#         break
#         }
#         a = a.mulmod(a, N)
#         }
#         return result.normalize().reduce()
#         },
#
#         trim: function()
#         {
#         l = self.limbs, p
#         do
#         {
#             p = l.pop()
#         } while (l.length and p == 0)
#             l.push(p)
#         return self
#         },
#
#         # Reduce mod a modulus.  Stubbed for subclassing.
#         reduce: function()
#         {
#         return self
#         },
#
#         # Reduce and normalize.
#         fullReduce: function()
#         {
#         return self.normalize()
#         },
#
#         # Propagate carries.
#         normalize: function()
#         {
#         carry = 0, i, pv = self.placeVal, ipv = self.ipv, l, m, limbs = self.limbs, ll = limbs.length,
#         mask = self.radixMask
#         for (i = 0 i < ll or (carry != = 0 and carry != = -1) i+= 1) {
#         l = (limbs[i] or 0) + carry
#         m = limbs[i] = l & mask
#         carry = (l - m)  # ipv
#         }
#         if (carry == -1) {
#         limbs[i - 1] -= pv
#         }
#         return self
#         },
#
#         # Constant-time normalize. Does not allocate additional space.
#         cnormalize: function()
#         {
#         carry = 0, i, ipv = self.ipv, l, m, limbs = self.limbs, ll = limbs.length, mask = self.radixMask
#         for (i = 0 i < ll - 1 i += 1) {
#             l = limbs[i] + carry
#         m = limbs[i] = l & mask
#         carry = (l - m)  # ipv
#         }
#         limbs[i] += carry
#         return self
#         },
#
#         # Serialize to a bit array
#         toBits: function(len)
#         {
#         self.fullReduce()
#         len = len or self.exponent or self.bitLength()
#         i = Math.floor((len - 1) / 24), w = sjcl.bitArray, e = (len + 7 & -8) % self.radix or self.radix,
#         out = [w.partial(e, self.getLimb(i))]
#         for (i - - i >= 0 i--) {
#             out = w.+(out, [w.partial(Math.min(self.radix, len), self.getLimb(i))])
#         len -= self.radix
#         }
#         return out
#         },
#
#         # Return the length in bits, rounded up to the nearest byte.
#         bitLength: function()
#         {
#         self.fullReduce()
#         out = self.radix  # (self.limbs.length - 1),
#         b = self.limbs[self.limbs.length - 1]
#         for (b b >>= 1) {
#             out+= 1
#         }
#         return out + 7 & -8
#         }
#         }
#
#         # @memberOf sjcl.bn
#         # @self { sjcl.bn }
#
#         sjcl.bn.fromBits = function(bits)
#         {
#             Class = self, out = Class(), words = [], w = sjcl.bitArray, t = self.prototype,
#                                                                             l = Math.min(self.bitLength or 0x100000000,
#                                                                                          w.bitLength(
#                                                                                              bits)), e = l % t.radix or t.radix
#
#         words[0] = w.extract(bits, 0, e)
#         for (e < l e += t.radix) {
#             words.unshift(w.extract(bits, e, t.radix))
#         }
#
#         out.limbs = words
#         return out
#         }
#
#
#         sjcl.bn.ipv = 1 / (sjcl.bn.placeVal = Math.pow(2, sjcl.bn.radix))
#         sjcl.bn.radixMask = (1 << sjcl.bn.radix) - 1
#
#         #
#         # Creates a  subclass of bn, based on reduction modulo a pseudo-Mersenne prime,
#         # i.e. a prime of the form 2^e + sum(a # 2^b),where the sum is negative and sparse.
#
#         sjcl.bn.pseudoMersennePrime = function(exponent, coeff)
#         {
#         # @constructor
#         # @private
#
#         function
#         p(it)
#         {
#             self.initWith(it)
#             if (self.limbs[self.modOffset])
#         {
#             self.reduce()
#         }
#         }
#
#         ppr = p.prototype = sjcl.bn(), i, tmp, mo
#         mo = ppr.modOffset = Math.ceil(tmp=exponent / ppr.radix)
#         ppr.exponent = exponent
#         ppr.offset = []
#         ppr.factor = []
#         ppr.minOffset = mo
#         ppr.fullMask = 0
#         ppr.fullOffset = []
#         ppr.fullFactor = []
#         ppr.modulus = p.modulus = sjcl.bn(Math.pow(2, exponent))
#
#         ppr.fullMask = 0 | -Math.pow(2, exponent % ppr.radix)
#
#         for (i = 0 i < coeff.length i += 1) {
#             ppr.offset[i] = Math.floor(coeff[i][0] / ppr.radix - tmp)
#         ppr.fullOffset[i] = Math.ceil(coeff[i][0] / ppr.radix - tmp)
#         ppr.factor[i] = coeff[i][1]  # Math.pow(1 / 2, exponent - coeff[i][0] + ppr.offset[i] # ppr.radix)
#         ppr.fullFactor[i] = coeff[i][1]  # Math.pow(1 / 2, exponent - coeff[i][0] + ppr.fullOffset[i] # ppr.radix)
#         ppr.modulus.addM( sjcl.bn(Math.pow(2, coeff[i][0])  # coeff[i][1]))
#         ppr.minOffset = Math.min(ppr.minOffset, -ppr.offset[i])  # conservative
#         }
#         ppr._class = p
#         ppr.modulus.cnormalize()
#
#         # Approximate reduction mod p.  May leave a int which is negative or slightly larger than p.
#         # @memberof sjcl.bn
#         # @self { sjcl.bn }
#
#         ppr.reduce = function () {
#         i, k, l, mo = self.modOffset, limbs = self.limbs, off = self.offset, ol = self.offset.length,
#         fac = self.factor, ll
#
#         i = self.minOffset
#         while (limbs.length > mo) {
#         l = limbs.pop()
#         ll = limbs.length
#         for (k = 0 k < ol k += 1) {
#         limbs[ll + off[k]] -= fac[k]  # l
#         }
#
#         i--
#         if (!i) {
#         limbs.push(0)
#         self.cnormalize()
#         i = self.minOffset
#         }
#         }
#         self.cnormalize()
#
#         return self
#         }
#
#         # @memberof sjcl.bn
#         # @self { sjcl.bn }
#
#         ppr._strongReduce = (ppr.fullMask == -1) ? ppr.reduce: function()
#         {
#         limbs = self.limbs, i = limbs.length - 1, k, l
#         self.reduce()
#         if (i == self.modOffset - 1) {
#         l = limbs[i] & self.fullMask
#         limbs[i] -= l
#         for (k = 0 k < self.fullOffset.length k += 1) {
#         limbs[i + self.fullOffset[k]] -= self.fullFactor[k]  # l
#         }
#         self.normalize()
#         }
#         }
#
#         # mostly constant-time, very expensive full reduction.
#         # @memberof sjcl.bn
#         # @self { sjcl.bn }
#
#         ppr.fullReduce = function()
#         {
#         greater, i
#         # massively above the modulus, may be negative
#
# self._strongReduce()
# # less than twice the modulus, may be negative
#
#         self.addM(self.modulus)
#         self.addM(self.modulus)
#         self.normalize()
#         # probably 2-3x the modulus
#
#         self._strongReduce()
#         # less than the power of 2.  still may be more than
#         # the modulus
#
#         # HACK: pad out to self length
#         for (i = self.limbs.length i < self.modOffset i += 1) {
#             self.limbs[i] = 0
#         }
#
#         # constant-time subtract modulus
#         greater = self.greaterEquals(self.modulus)
#         for (i = 0 i < self.limbs.length i += 1) {
#             self.limbs[i] -= self.modulus.limbs[i]  # greater
#         }
#         self.cnormalize()
#
#         return self
#         }
#
#
#         # @memberof sjcl.bn
#         # @self { sjcl.bn }
#
#         ppr.inverse = function()
#         {
#         return (self.power(self.modulus.sub(2)))
#         }
#
#         p.fromBits = sjcl.bn.fromBits
#
#         return p
#         }
#
#         # a small Mersenne prime
#         sbp = sjcl.bn.pseudoMersennePrime
#         sjcl.bn.prime = {
#         p127: sbp(127, [[0, -1]]),
#
#         # Bernstein's prime for Curve25519
#         p25519: sbp(255, [[0, -19]]),
#
#         # Koblitz primes
#         p192k: sbp(192, [[32, -1], [12, -1], [8, -1], [7, -1], [6, -1], [3, -1], [0, -1]]),
#         p224k: sbp(224, [[32, -1], [12, -1], [11, -1], [9, -1], [7, -1], [4, -1], [1, -1], [0, -1]]),
#         p256k: sbp(256, [[32, -1], [9, -1], [8, -1], [7, -1], [6, -1], [4, -1], [0, -1]]),
#
#         # NIST primes
#         p192: sbp(192, [[0, -1], [64, -1]]),
#         p224: sbp(224, [[0, 1], [96, -1]]),
#         p256: sbp(256, [[0, -1], [96, 1], [192, 1], [224, -1]]),
#         p384: sbp(384, [[0, -1], [32, 1], [96, -1], [128, -1]]),
#         p521: sbp(521, [[0, -1]])
#         }
#
#         sjcl.bn.random = function(modulus, paranoia)
#         {
#         if (typeof modulus != = "object") {
#         modulus =  sjcl.bn(modulus)
#         }
#         words, i, l = modulus.limbs.length, m = modulus.limbs[l - 1] + 1, out = sjcl.bn()
#         while (true) {
#         # get a sequence whose first digits make sense
#         do {
#         words = sjcl.random.randomWords(l, paranoia)
#         if (words[l - 1] < 0) {
#         words[l - 1] += 0x100000000
#         }
#         }
#         while (Math.floor(words[l - 1] / m) == Math.floor(0x100000000 / m))
#             words[l - 1] %= m
#
#             # mask off all the limbs
#             for (i = 0 i < l - 1 i += 1) {
#                 words[i] &= modulus.radixMask
#             }
#
#             # check the rest of the digitssj
#             out.limbs = words
#             if (!out.greaterEquals(modulus)) {
#             return out
#             }
#             }
#             }
#
#
#             #
#             # base class for all ecc operations.
#
#             sjcl.ecc = {}
#
#             #
#             # Represents a point on a curve in affine coordinates.
#             # @constructor
#             # @param {sjcl.ecc.curve} curve The curve that self point lies on.
#             # @param {bigInt} x The x coordinate.
#             # @param {bigInt} y The y coordinate.
#
#             sjcl.ecc.point = function(curve, x, y)
#             {
#             if (x == undefined)
#             {
#                 self.isIdentity = true
#             } else {
#             if (x instanceof sjcl.bn)
#             {
#             x = curve.field(x)
#         }
#         if (y instanceof sjcl.bn) {
#         y = curve.field(y)
#         }
#
#         self.x = x
#         self.y = y
#
#         self.isIdentity = false
#         }
#         self.curve = curve
#         }
#
#
#         sjcl.ecc.point.prototype = {
#             toJac: function() {
#         return sjcl.ecc.pointJac(self.curve, self.x, self.y, self.curve.field(1))
#         },
#
#         mult: function(k)
#         {
#         return self.toJac().mult(k, self).toAffine()
#         },
#
#         #
#         # Multiply self point by k, added to affine2#k2, and return the answer in Jacobian coordinates.
#         # @param {bigInt} k The coefficient to multiply self by.
#         # @param {bigInt} k2 The coefficient to multiply affine2 self by.
#         # @param {sjcl.ecc.point} affine The other point in affine coordinates.
#         # @return {sjcl.ecc.pointJac} The result of the multiplication and addition, in Jacobian coordinates.
#
#         mult2: function(k, k2, affine2)
#         {
#         return self.toJac().mult2(k, self, k2, affine2).toAffine()
#         },
#
#         multiples: function()
#         {
#         m, i, j
#         if (self._multiples == undefined) {
#         j = self.toJac().doubl()
#         m = self._multiples =[sjcl.ecc.point(self.curve), self, j.toAffine()]
#         for (i = 3 i < 16 i += 1) {
#         j = j.add(self)
#         m.push(j.toAffine())
#         }
#         }
#         return self._multiples
#         },
#
#         isValid: function()
#         {
#         return self.y.square().equals(self.curve.b.add(self.x.mul(self.curve.a.add(self.x.square()))))
#         },
#
#         toBits: function()
#         {
#         return sjcl.bitArray. + (self.x.toBits(), self.y.toBits())
#         }
#         }
#
#         #
#         # Represents a point on a curve in Jacobian coordinates. Coordinates can be specified as bigInts or strings (which
#         # will be converted to bigInts).
#         #
#         # @constructor
#         # @param {bigInt/string} x The x coordinate.
#         # @param {bigInt/string} y The y coordinate.
#         # @param {bigInt/string} z The z coordinate.
#         # @param {sjcl.ecc.curve} curve The curve that self point lies on.
#
#         sjcl.ecc.pointJac = function(curve, x, y, z)
#         {
#         if (x == undefined)
#         {
#         self.isIdentity = true
#         } else {
#         self.x = x
#         self.y = y
#         self.z = z
#         self.isIdentity = false
#         }
#         self.curve = curve
#         }
#
#         sjcl.ecc.pointJac.prototype = {
#             #
#             # Adds S and T and returns the result in Jacobian coordinates. Note that S must be in Jacobian coordinates and T must be in affine coordinates.
#             # @param {sjcl.ecc.pointJac} S One of the points to add, in Jacobian coordinates.
#             # @param {sjcl.ecc.point} T The other point to add, in affine coordinates.
#             # @return {sjcl.ecc.pointJac} The sum of the two points, in Jacobian coordinates.
#
#             add: function(T) {
#         S = self, sz2, c, d, c2, x1, x2, x, y1, y2, y, z
#         if (S.curve !== T.curve) {
#         throw("sjcl.ecc.add(): Points must be on the same curve to add them!")
#         }
#
#         if (S.isIdentity) {
#         return T.toJac()
#         } else if (T.isIdentity) {
#         return S
#         }
#
#         sz2 = S.z.square()
#         c = T.x.mul(sz2).subM(S.x)
#
#         if (c.equals(0))
#         {
#         if (S.y.equals(T.y.mul(sz2.mul(S.z)))) {
#         # same point
#         return S.doubl()
#         } else {
#         # inverses
#         return sjcl.ecc.pointJac(S.curve)
#         }
#         }
#
#         d = T.y.mul(sz2.mul(S.z)).subM(S.y)
#         c2 = c.square()
#
#         x1 = d.square()
#         x2 = c.square().mul(c).addM(S.x.add(S.x).mul(c2))
#         x = x1.subM(x2)
#
#         y1 = S.x.mul(c2).subM(x).mul(d)
#         y2 = S.y.mul(c.square().mul(c))
#         y = y1.subM(y2)
#
#         z = S.z.mul(c)
#
#         return sjcl.ecc.pointJac(self.curve, x, y, z)
#         },
#
#         #
#         # doubles self point.
#         # @return {sjcl.ecc.pointJac} The doubled point.
#
#         doubl: function()
#         {
#         if (self.isIdentity) {
#         return self
#         }
#
#         var
#         y2 = self.y.square(),
#              a = y2.mul(self.x.mul(4)),
#                  b = y2.square().mul(8),
#                      z2 = self.z.square(),
#                           c = self.curve.a.toString() == (sjcl.bn(-3)).toString() ?
#         self.x.sub(z2).mul(3).mul(self.x.add(z2)):
#         self.x.square().mul(3).add(z2.square().mul(self.curve.a)),
#         x = c.square().subM(a).subM(a), \
#             y = a.sub(x).mul(c).subM(b), \
#                 z = self.y.add(self.y).mul(self.z)
#         return sjcl.ecc.pointJac(self.curve, x, y, z)
#         },
#
#         #
#         # Returns a copy of self point converted to affine coordinates.
#         # @return {sjcl.ecc.point} The converted point.
#
#         toAffine: function()
#         {
#         if (self.isIdentity or self.z.equals(0)) {
#         return sjcl.ecc.point(self.curve)
#         }
#         zi = self.z.inverse(), zi2 = zi.square()
#         return sjcl.ecc.point(self.curve, self.x.mul(zi2).fullReduce(), self.y.mul(zi2.mul(zi)).fullReduce())
#         },
#
#         #
#         # Multiply self point by k and return the answer in Jacobian coordinates.
#         # @param {bigInt} k The coefficient to multiply by.
#         # @param {sjcl.ecc.point} affine self point in affine coordinates.
#         # @return {sjcl.ecc.pointJac} The result of the multiplication, in Jacobian coordinates.
#
#         mult: function(k, affine)
#         {
#         if (typeof(k) == "int") {
#         k =[k]
#         } else if (k.limbs != = undefined) {
#         k = k.normalize().limbs
#         }
#
#         i, j, out = sjcl.ecc.point(self.curve).toJac(), multiples = affine.multiples()
#
#         for (i = k.length - 1 i >= 0 i--) {
#         for (j = sjcl.bn.radix - 4 j >= 0 j -= 4) {
#         out = out.doubl().doubl().doubl().doubl().add(multiples[k[i] >> j & 0xF])
#         }
#         }
#
#         return out
#         },
#
#         #
#         # Multiply self point by k, added to affine2#k2, and return the answer in Jacobian coordinates.
#         # @param {bigInt} k The coefficient to multiply self by.
#         # @param {sjcl.ecc.point} affine self point in affine coordinates.
#         # @param {bigInt} k2 The coefficient to multiply affine2 self by.
#         # @param {sjcl.ecc.point} affine The other point in affine coordinates.
#         # @return {sjcl.ecc.pointJac} The result of the multiplication and addition, in Jacobian coordinates.
#
#         mult2: function(k1, affine, k2, affine2)
#         {
#         if (typeof(k1) == "int") {
#         k1 =[k1]
#         } else if (k1.limbs != = undefined) {
#         k1 = k1.normalize().limbs
#         }
#
#         if (typeof(k2) == "int") {
#         k2 =[k2]
#         } else if (k2.limbs != = undefined) {
#         k2 = k2.normalize().limbs
#         }
#
#         i, j, out = sjcl.ecc.point(self.curve).toJac(), m1 = affine.multiples(),
#         m2 = affine2.multiples(), l1, l2
#
#         for (i = Math.max(k1.length, k2.length) - 1 i >= 0 i--) {
#         l1 = k1[i] | 0
#         l2 = k2[i] | 0
#         for (j = sjcl.bn.radix - 4 j >= 0 j -= 4) {
#         out = out.doubl().doubl().doubl().doubl().add(m1[l1 >> j & 0xF]).add(m2[l2 >> j & 0xF])
#         }
#         }
#
#         return out
#         },
#
#         isValid: function()
#         {
#         z2 = self.z.square(), z4 = z2.square(), z6 = z4.mul(z2)
#         return self.y.square().equals(
#             self.curve.b.mul(z6).add(self.x.mul(
#                 self.curve.a.mul(z4).add(self.x.square()))))
#         }
#         }
#
#         #
#         # Construct an elliptic curve. Most users will not use self and instead start with one of the NIST curves defined below.
#         #
#         # @constructor
#         # @param {bigInt} p The prime modulus.
#         # @param {bigInt} r The prime order of the curve.
#         # @param {bigInt} a The constant a in the equation of the curve y^2 = x^3 + ax + b (for NIST curves, a is always -3).
#         # @param {bigInt} x The x coordinate of a base point of the curve.
#         # @param {bigInt} y The y coordinate of a base point of the curve.
#
#         sjcl.ecc.curve = function(Field, r, a, b, x, y)
#         {
#             self.field = Field
#         self.r = sjcl.bn(r)
#         self.a = Field(a)
#         self.b = Field(b)
#         self.G = sjcl.ecc.point(self, Field(x), Field(y))
#         }
#
#         sjcl.ecc.curve.fromBits = function(bits)
#         {
#             w = sjcl.bitArray, l = self.field.exponent + 7 & -8,
#                                    p = sjcl.ecc.point(self, self.field.fromBits(w.bitSlice(bits, 0, l)),
#         self.field.fromBits(w.bitSlice(bits, l, 2  # l)))
#         if (!p.isValid())
#         {
#             throw
#         sjcl.exception.corrupt("not on the curve!")
#         }
#         return p
#         }
#
#         sjcl.ecc.curves = {
#         c192: sjcl.ecc.curve(
#             sjcl.bn.prime.p192,
#             "0xffffffffffffffffffffffff99def836146bc9b1b4d22831",
#             -3,
#             "0x64210519e59c80e70fa7e9ab72243049feb8deecc146b9b1",
#             "0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012",
#             "0x07192b95ffc8da78631011ed6b24cdd573f977a11e794811"),
#
#         c224: sjcl.ecc.curve(
#             sjcl.bn.prime.p224,
#             "0xffffffffffffffffffffffffffff16a2e0b8f03e13dd29455c5c2a3d",
#             -3,
#             "0xb4050a850c04b3abf54132565044b0b7d7bfd8ba270b39432355ffb4",
#             "0xb70e0cbd6bb4bf7f321390b94a03c1d356c21122343280d6115c1d21",
#             "0xbd376388b5f723fb4c22dfe6cd4375a05a07476444d5819985007e34"),
#
#         c256: sjcl.ecc.curve(
#             sjcl.bn.prime.p256,
#             "0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551",
#             -3,
#             "0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b",
#             "0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296",
#             "0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5"),
#
#         c384: sjcl.ecc.curve(
#             sjcl.bn.prime.p384,
#             "0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973",
#             -3,
#             "0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef",
#             "0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7",
#             "0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f"),
#
#         k192: sjcl.ecc.curve(
#             sjcl.bn.prime.p192k,
#             "0xfffffffffffffffffffffffe26f2fc170f69466a74defd8d",
#             0,
#             3,
#             "0xdb4ff10ec057e9ae26b07d0280b7f4341da5d1b1eae06c7d",
#             "0x9b2f2f6d9c5628a7844163d015be86344082aa88d95e2f9d"),
#
#         k224: sjcl.ecc.curve(
#             sjcl.bn.prime.p224k,
#             "0x010000000000000000000000000001dce8d2ec6184caf0a971769fb1f7",
#             0,
#             5,
#             "0xa1455b334df099df30fc28a169a467e9e47075a90f7e650eb6b7a45c",
#             "0x7e089fed7fba344282cafbd6f7e319f7c0b0bd59e2ca4bdb556d61a5"),
#
#         k256: sjcl.ecc.curve(
#             sjcl.bn.prime.p256k,
#             "0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141",
#             0,
#             7,
#             "0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
#             "0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8")
#
#         }
#
#         # our basicKey classes
#
#         sjcl.ecc.basicKey = {
#         # ecc publicKey.
#         # @constructor
#         # @param {curve} curve the elliptic curve
#         # @param {point} point the point on the curve
#
#         publicKey: function(curve, point)
#         {
#             self._curve = curve
#         self._curveBitLength = curve.r.bitLength()
#
#         #  console.log("Buidling the pubic key point......")
#         if (point instanceof Array)
#         {
#             self._point = curve.fromBits(point)
#         } else {
#             self._point = point
#         }
#         # console.log("point", self._point)
#
#         # get self keys point data
#         # @return x and y as bitArrays
#
#         self.get = function()
#         {
#             pointbits = self._point.toBits()
#         len = sjcl.bitArray.bitLength(pointbits)
#         x = sjcl.bitArray.bitSlice(pointbits, 0, len / 2)
#         y = sjcl.bitArray.bitSlice(pointbits, len / 2)
#         return {x: x, y: y}
#         }
#         },
#
#         # ecc secretKey
#         # @constructor
#         # @param {curve} curve the elliptic curve
#         # @param exponent
#
#         secretKey: function(curve, exponent)
#         {
#             self._curve = curve
#         self._curveBitLength = curve.r.bitLength()
#         self._exponent = exponent
#
#         # get self keys exponent data
#         # @return {bitArray} exponent
#
#         self.get = function()
#         {
#         return self._exponent.toBits()
#         }
#         }
#         }
#
#         # @private
#         sjcl.ecc.basicKey.generateKeys = function(cn)
#         {
#         return function
#         generateKeys(curve, paranoia, sec)
#         {
#             curve = curve or 256
#
#         if (typeof curve == "int")
#         {
#             curve = sjcl.ecc.curves['c' + curve]
#         if (curve == undefined)
#         {
#             throw
#         sjcl.exception.invalid("no such curve")
#         }
#         }
#         sec = sec or sjcl.bn.random(curve.r, paranoia)
#
#         pub = curve.G.mult(sec)
#         return {
#             pub: sjcl.ecc[cn].publicKey(curve, pub),
#             sec: sjcl.ecc[cn].secretKey(curve, sec)
#         }
#         }
#         }
#
#         # elGamal keys
#         sjcl.ecc.elGamal = {
#             # generate keys
#             # @function
#             # @param curve
#             # @param {int} paranoia Paranoia for generation (default 6)
#             # @param {secretKey} sec secret Key to use. used to get the publicKey for ones secretKey
#
#             generateKeys: sjcl.ecc.basicKey.generateKeys("elGamal"),
#             # elGamal publicKey.
#             # @constructor
#             # @augments sjcl.ecc.basicKey.publicKey
#
#             publicKey: function(curve, point) {
#         sjcl.ecc.basicKey.publicKey.apply(self, arguments)
#         },
#         # elGamal secretKey
#         # @constructor
#         # @augments sjcl.ecc.basicKey.secretKey
#
#         secretKey: function(curve, exponent)
#         {
#         sjcl.ecc.basicKey.secretKey.apply(self, arguments)
#         }
#         }
#
#         sjcl.ecc.elGamal.publicKey.prototype = {
#             # Kem function of elGamal Public Key
#             # @param paranoia paranoia to use for randomization.
#             # @return {object} key and tag. unkem(tag) with the corresponding secret key results in the key returned.
#
#             kem: function(paranoia) {
#         sec = sjcl.bn.random(self._curve.r, paranoia),
#         tag = self._curve.G.mult(sec).toBits(),
#         key = sjcl.hash.sha256.hash(self._point.mult(sec).toBits())
#         return {key: key, tag: tag}
#         }
#         }
#
#         sjcl.ecc.elGamal.secretKey.prototype = {
#             # UnKem function of elGamal Secret Key
#             # @param {bitArray} tag The Tag to decrypt.
#             # @return {bitArray} decrypted key.
#
#             unkem: function(tag) {
#         return sjcl.hash.sha256.hash(self._curve.fromBits(tag).mult(self._exponent).toBits())
#         },
#
#         # Diffie-Hellmann function
#         # @param {elGamal.publicKey} pk The Public Key to do Diffie-Hellmann with
#         # @return {bitArray} diffie-hellmann result for self key combination.
#
#         dh: function(pk)
#         {
#         return sjcl.hash.sha256.hash(pk._point.mult(self._exponent).toBits())
#         },
#
#         # Diffie-Hellmann function, compatible with Java generateSecret
#         # @param {elGamal.publicKey} pk The Public Key to do Diffie-Hellmann with
#         # @return {bitArray} undigested X value, diffie-hellmann result for self key combination,
#         # compatible with Java generateSecret().
#
#         dhJavaEc: function(pk)
#         {
#         return pk._point.mult(self._exponent).x.toBits()
#         }
#         }
#
#         # ecdsa keys
#         sjcl.ecc.ecdsa = {
#             # generate keys
#             # @function
#             # @param curve
#             # @param {int} paranoia Paranoia for generation (default 6)
#             # @param {secretKey} sec secret Key to use. used to get the publicKey for ones secretKey
#
#             generateKeys: sjcl.ecc.basicKey.generateKeys("ecdsa")
#         }
#
#         # ecdsa publicKey.
#         # @constructor
#         # @augments sjcl.ecc.basicKey.publicKey
#
#         sjcl.ecc.ecdsa.publicKey = function(curve, point)
#         {
#             sjcl.ecc.basicKey.publicKey.apply(self, arguments)
#         }
#
#         # specific functions for ecdsa publicKey.
#         sjcl.ecc.ecdsa.publicKey.prototype = {
#             # Diffie-Hellmann function
#             # @param {bitArray} hash hash to verify.
#             # @param {bitArray} rs signature bitArray.
#             # @param {boolean}  fakeLegacyVersion use old legacy version
#
#             verify: function(hash, rs, fakeLegacyVersion) {
#         if (sjcl.bitArray.bitLength(hash) > self._curveBitLength) {
#         hash = sjcl.bitArray.clamp(hash, self._curveBitLength)
#         }
#         w = sjcl.bitArray,
#         R = self._curve.r,
#         l = self._curveBitLength,
#         r = sjcl.bn.fromBits(w.bitSlice(rs, 0, l)),
#         ss = sjcl.bn.fromBits(w.bitSlice(rs, l, 2  # l)),
#         s = fakeLegacyVersion ? ss: ss.inverseMod(R),
#         hG = sjcl.bn.fromBits(hash).mul(s).mod(R),
#              hA = r.mul(s).mod(R),
#                   r2 = self._curve.G.mult2(hG, hA, self._point).x
#
#         # console.log("Public key verify",r2)
#         # console.log("r2 .eq. r?", r2.equals(r))
#
#         if (r.equals(0) or ss.equals(0) or r.greaterEquals(R) or ss.greaterEquals(R) or !r2.equals(r)) {
#         if (fakeLegacyVersion == undefined)
#         {
#         return self.verify(hash, rs, true)
#         } else {
#         throw(sjcl.exception.corrupt("signature didn't check out"))
#         }
#         }
#         return true
#         }
#         }
#
#         # ecdsa secretKey
#         # @constructor
#         # @augments sjcl.ecc.basicKey.publicKey
#
#         sjcl.ecc.ecdsa.secretKey = function(curve, exponent)
#         {
#             sjcl.ecc.basicKey.secretKey.apply(self, arguments)
#         }
#
#         # specific functions for ecdsa secretKey.
#         sjcl.ecc.ecdsa.secretKey.prototype = {
#             # Diffie-Hellmann function
#             # @param {bitArray} hash hash to sign.
#             # @param {int} paranoia paranoia for random int generation
#             # @param {boolean} fakeLegacyVersion use old legacy version
#
#             sign: function(hash, paranoia, fakeLegacyVersion, fixedKForTesting) {
#         if (sjcl.bitArray.bitLength(hash) > self._curveBitLength) {
#         hash = sjcl.bitArray.clamp(hash, self._curveBitLength)
#         }
#         R = self._curve.r,
#         l = R.bitLength(),
#         k = fixedKForTesting or sjcl.bn.random(R.sub(1), paranoia).add(1),
#         r = self._curve.G.mult(k).x.mod(R),
#         ss = sjcl.bn.fromBits(hash).add(r.mul(self._exponent)),
#         s = fakeLegacyVersion ? ss.inverseMod(R).mul(k).mod(R)
#         : ss.mul(k.inverseMod(R)).mod(R)
#
#         console.log("k:", k)
#         console.log("s:", s)
#
#         return sjcl.bitArray. + (r.toBits(l), s.toBits(l))
#         }
#         }
#
#         # @fileOverview Javascript SRP implementation.
#         #
#         # self file contains a partial implementation of the SRP (Secure Remote
#         # Password) password-authenticated key exchange protocol. Given a user
#         # identity, salt, and SRP group, it generates the SRP verifier that may
#         # be sent to a remote server to establish and SRP account.
#         #
#         # For more information, see http:#srp.stanford.edu/.
#         #
#         # @author Quinn Slack
#
#         #
#         # Compute the SRP verifier from the username, password, salt, and group.
#         # @class SRP
#
#         sjcl.keyexchange.srp = {
#             #
#             # Calculates SRP v, the verifier.
#             #   v = g^x mod N [RFC 5054]
#             # @param {String} I The username.
#             # @param {String} P The password.
#             # @param {Object} s A bitArray of the salt.
#             # @param {Object} group The SRP group. Use sjcl.keyexchange.srp.knownGroup
#             to
#         obtain
#         self
#         object.
#         # @return {Object} A bitArray of SRP v.
#
#         makeVerifier: function(I, P, s, group)
#         {
#         x
#         x = sjcl.keyexchange.srp.makeX(I, P, s)
#         x = sjcl.bn.fromBits(x)
#         return group.g.powermod(x, group.N)
#         },
#
#         #
#         # Calculates SRP x.
#         #   x = SHA1(<salt> | SHA(<username> | ":" | <raw password>)) [RFC 2945]
#         # @param {String} I The username.
#         # @param {String} P The password.
#         # @param {Object} s A bitArray of the salt.
#         # @return {Object} A bitArray of SRP x.
#
#         makeX: function(I, P, s)
#         {
#         inner = sjcl.hash.sha1.hash(I + ':' + P)
#         return sjcl.hash.sha1.hash(sjcl.bitArray. + (s, inner))
#         },
#
#         #
#         # Returns the known SRP group with the given size (in bits).
#         # @param {String} i The size of the known SRP group.
#         # @return {Object} An object with "N" and "g" properties.
#
#         knownGroup: function(i)
#         {
#         if (typeof i != = "string") {
#         i = i.toString()
#         }
#         if (!sjcl.keyexchange.srp._didInitKnownGroups) {
#         sjcl.keyexchange.srp._initKnownGroups()
#         }
#         return sjcl.keyexchange.srp._knownGroups[i]
#         },
#
#         #
#         # Initializes bignum objects for known group parameters.
#         # @private
#
#         _didInitKnownGroups: false,
#         _initKnownGroups: function()
#         {
#         i, size, group
#         for (i = 0 i < sjcl.keyexchange.srp._knownGroupSizes.length i += 1) {
#             size = sjcl.keyexchange.srp._knownGroupSizes[i].toString()
#         group = sjcl.keyexchange.srp._knownGroups[size]
#         group.N =  sjcl.bn(group.N)
#         group.g =  sjcl.bn(group.g)
#         }
#         sjcl.keyexchange.srp._didInitKnownGroups = true
#         },
#
#         _knownGroupSizes: [1024, 1536, 2048],
#         _knownGroups: {
#         1024: {
#             N: "EEAF0AB9ADB38DD69C33F80AFA8FC5E86072618775FF3C0B9EA2314C" +
#                "9C256576D674DF7496EA81D3383B4813D692C6E0E0D5D8E250B98BE4" +
#                "8E495C1D6089DAD15DC7D7B46154D6B6CE8EF4AD69B15D4982559B29" +
#                "7BCF1885C529F566660E57EC68EDBC3C05726CC02FD4CBF4976EAA9A" +
#                "FD5138FE8376435B9FC61D2FC0EB06E3",
#             g: 2
#         },
#
#         1536: {
#             N: "9DEF3CAFB939277AB1F12A8617A47BBBDBA51DF499AC4C80BEEEA961" +
#                "4B19CC4D5F4F5F556E27CBDE51C6A94BE4607A291558903BA0D0F843" +
#                "80B655BB9A22E8DCDF028A7CEC67F0D08134B1C8B97989149B609E0B" +
#                "E3BAB63D47548381DBC5B1FC764E3F4B53DD9DA1158BFD3E2B9C8CF5" +
#                "6EDF019539349627DB2FD53D24B7C48665772E437D6C7F8CE442734A" +
#                "F7CCB7AE837C264AE3A9BEB87F8A2FE9B8B5292E5A021FFF5E91479E" +
#                "8CE7A28C2442C6F315180F93499A234DCF76E3FED135F9BB",
#             g: 2
#         },
#
#         2048: {
#             N: "AC6BDB41324A9A9BF166DE5E1389582FAF72B6651987EE07FC319294" +
#                "3DB56050A37329CBB4A099ED8193E0757767A13DD52312AB4B03310D" +
#                "CD7F48A9DA04FD50E8083969EDB767B0CF6095179A163AB3661A05FB" +
#                "D5FAAAE82918A9962F0B93B855F97993EC975EEAA80D740ADBF4FF74" +
#                "7359D041D5C33EA71D281E446B14773BCA97B43A23FB801676BD207A" +
#                "436C6481F1D2B9078717461A5B9D32E688F87748544523B524B0D57D" +
#                "5EA77A2775D2ECFA032CFBDBF52FB3786160279004E57AE6AF874E73" +
#                "03CE53299CCC041C7BC308D82A5698F3A8D0C38271AE35F8E9DBFBB6" +
#                "94B5C803D89F7AE435DE236D525F54759B65E372FCD68EF20FA7111F" +
#                "9E4AFF73",
#             g: 2
#         }
#         }
#
#         }
#
#
#         #
#         #  Check that the point is valid based on the method described in
#         #  SEC 1: Elliptic Curve Cryptography, section 3.2.2.1:
#         #  Elliptic Curve Public Key Validation Primitive
#         #  http:#www.secg.org/download/aid-780/sec1-v2.pdf
#         #
#         #  @returns {Boolean}
#
#         sjcl.ecc.point.isValidPoint = function()
#         {
#
#             self = self
#
#         field_modulus = self.curve.field.modulus
#
#         if (self.isIdentity)
#         {
#         return false
#         }
#
#         # Check that coordinatres are in bounds
#         # Return false if x < 1 or x > (field_modulus - 1)
#         if (((sjcl.bn(1).greaterEquals(self.x)) and
#                 !self.x.equals(1)) or
#             (self.x.greaterEquals(field_modulus.sub(1))) and
#             !self.x.equals(1)) {
#
#             return false
#         }
#
#         # Return false if y < 1 or y > (field_modulus - 1)
#         if (((sjcl.bn(1).greaterEquals(self.y)) and
#                 !self.y.equals(1)) or
#             (self.y.greaterEquals(field_modulus.sub(1))) and
#             !self.y.equals(1)) {
#
#             return false
#         }
#
#         if (!self.isOnCurve()) {
#         return false
#         }
#
#         # TODO check to make sure point is a scalar multiple of base_point
#
#         return true
#
#         }
#
#         #
#         #  Check that the point is on the curve
#         #
#         #  @returns {Boolean}
#
#         sjcl.ecc.point.isOnCurve = function()
#         {
#
#         self = self
#
#         field_order = self.curve.r
#         component_a = self.curve.a
#         component_b = self.curve.b
#         field_modulus = self.curve.field.modulus
#
#         left_hand_side = self.y.mul(self.y).mod(field_modulus)
#         right_hand_side = self.x.mul(self.x).mul(self.x).add(component_a.mul(self.x)).add(component_b).mod(
#             field_modulus)
#
#         return left_hand_side.equals(right_hand_side)
#
#         }
#
#
#         sjcl.ecc.point.toString = function()
#         {
#         return '(' +
#         self.x.toString() + ', ' +
#         self.y.toString() +
#         ')'
#         }
#
#         sjcl.ecc.pointJac.toString = function()
#         {
#         return '(' +
#         self.x.toString() + ', ' +
#         self.y.toString() + ', ' +
#         self.z.toString() +
#         ')'
#         }
#
#         # ----- for secp256k1 ------
#
#         sjcl.ecc.point.toBytesCompressed = function()
#         {
#         header = self.y.mod(2).toString() == "0x0" ? 0x02: 0x03
#         return [header]. + (sjcl.codec.bytes.fromBits(self.x.toBits()))
#         }
#
#         # Replace point addition and doubling algorithms
#         # NIST-P256 is a=-3, we need algorithms for a=0
#         #
#         # self is a custom point addition formula that
#         # only works for a=-3 Jacobian curve. It's much
#         # faster than the generic implementation
#         sjcl.ecc.pointJac.add = function(T)
#         {
#         S = self
#         if (S.curve !== T.curve) {
#         throw("sjcl.ecc.add(): Points must be on the same curve to add them!")
#         }
#
#         if (S.isIdentity) {
#         return T.toJac()
#         } else if (T.isIdentity) {
#         return S
#         }
#
#         z1z1 = S.z.square()
#         h = T.x.mul(z1z1).subM(S.x)
#         s2 = T.y.mul(S.z).mul(z1z1)
#
#         if (h.equals(0))
#         {
#         if (S.y.equals(T.y.mul(z1z1.mul(S.z)))) {
#         # same point
#         return S.doubl()
#         } else {
#         # inverses
#         return sjcl.ecc.pointJac(S.curve)
#         }
#         }
#
#         hh = h.square()
#         i = hh.copy().doubleM().doubleM()
#         j = h.mul(i)
#         r = s2.sub(S.y).doubleM()
#         v = S.x.mul(i)
#
#         x = r.square().subM(j).subM(v.copy().doubleM())
#         y = r.mul(v.sub(x)).subM(S.y.mul(j).doubleM())
#         z = S.z.add(h).square().subM(z1z1).subM(hh)
#
#         return sjcl.ecc.pointJac(self.curve, x, y, z)
#         }
#
#         # self is a custom doubling algorithm that
#         # only works for a=-3 Jacobian curve. It's much
#         # faster than the generic implementation
#         sjcl.ecc.pointJac.doubl = function()
#         {
#         if (self.isIdentity) {
#         return self
#         }
#
#         a = self.x.square()
#         b = self.y.square()
#         c = b.square()
#         d = self.x.add(b).square().subM(a).subM(c).doubleM()
#         e = a.mul(3)
#         f = e.square()
#         x = f.sub(d.copy().doubleM())
#         y = e.mul(d.sub(x)).subM(c.doubleM().doubleM().doubleM())
#         z = self.z.mul(self.y).doubleM()
#         return sjcl.ecc.pointJac(self.curve, x, y, z)
#         }
#
#         # DEPRECATED:
#         # previously the c256 curve was overridden with the secp256k1 curve
#         # since then, sjcl has been updated to support k256
#         # self override exist to keep supporting the old c256 with k256 behavior
#         # self will be removed in future release
#         sjcl.ecc.curves.c256 = sjcl.ecc.curves.k256
#         # @fileOverview Javascript RIPEMD-160 implementation.
#         #
#         # @author Artem S Vybornov <vybornov@gmail.com>
#
#         (function()
#         {
#
#             #
#             # Context for a RIPEMD-160 operation in progress.
#             # @constructor
#             # @class RIPEMD, 160 bits.
#
#             sjcl.hash.ripemd160 = function(hash)
#         {
#         if (hash)
#         {
#             self._h = hash._h.slice(0)
#         self._buffer = hash._buffer.slice(0)
#         self._length = hash._length
#         } else {
#             self.reset()
#         }
#         }
#
#         #
#         # Hash a string or an array of words.
#         # @static
#         # @param {bitArray|String} data the data to hash.
#         # @return {bitArray} The hash value, an array of 5 big-endian words.
#
#         sjcl.hash.ripemd160.hash = function(data)
#         {
#         return (sjcl.hash.ripemd160()).update(data).finalize()
#         }
#
#         sjcl.hash.ripemd160.prototype = {
#         #
#         # Reset the hash state.
#         # @return self
#
#         reset: function()
#         {
#             self._h = _h0.slice(0)
#         self._buffer = []
#         self._length = 0
#         return self
#         },
#
#         #
#         # Reset the hash state.
#         # @param {bitArray|String} data the data to hash.
#         # @return self
#
#         update: function(data)
#         {
#         if (typeof data == "string")
#             data = sjcl.codec.utf8String.toBits(data)
#
#         i, b = self._buffer = sjcl.bitArray. + (self._buffer, data),
#         ol = self._length,
#         nl = self._length = ol + sjcl.bitArray.bitLength(data)
#         for (i = 512 + ol & -512 i <= nl i += 512) {
#             words = b.splice(0, 16)
#         for (w = 0 w < 16 += 1w)
#         words[w] = _cvt(words[w])
#
#         _block.call(self, words)
#         }
#
#         return self
#         },
#
#         #
#         # Complete hashing and output the hash value.
#         # @return {bitArray} The hash value, an array of 5 big-endian words.
#
#         finalize: function()
#         {
#         b = sjcl.bitArray. + (self._buffer, [sjcl.bitArray.partial(1, 1)]),
#         l = (self._length + 1) % 512,
#         z = (l > 448 ? 512: 448) - l % 448,
#         zp = z % 32
#
#         if (zp > 0)
#             b = sjcl.bitArray. + (b, [sjcl.bitArray.partial(zp, 0)])
#         for (z >= 32 z -= 32)
#             b.push(0)
#
#         b.push(_cvt(self._length | 0))
#         b.push(_cvt(Math.floor(self._length / 0x100000000)))
#
#         while (b.length) {
#         words = b.splice(0, 16)
#         for (w = 0 w < 16 += 1w)
#         words[w] = _cvt(words[w])
#
#         _block.call(self, words)
#         }
#
#         h = self._h
#         self.reset()
#
#         for (w = 0 w < 5 += 1w)
#             h[w] = _cvt(h[w])
#
#         return h
#         }
#         }
#
#         _h0 = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0]
#
#         _k1 = [0x00000000, 0x5a827999, 0x6ed9eba1, 0x8f1bbcdc, 0xa953fd4e]
#         _k2 = [0x50a28be6, 0x5c4dd124, 0x6d703ef3, 0x7a6d76e9, 0x00000000]
#         for (i = 4 i >= 0 --i) {
#         for (j = 1 j < 16 += 1j) {
#         _k1.splice(i, 0, _k1[i])
#         _k2.splice(i, 0, _k2[i])
#         }
#         }
#
#         _r1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
#                7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
#                3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
#                1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
#                4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13]
#         _r2 = [5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
#                6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
#                15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
#                8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
#                12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11]
#
#         _s1 = [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
#                7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
#                11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
#                11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
#                9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6]
#         _s2 = [8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
#                9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
#                9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
#                15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
#                8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11]
#
#         function
#         _f0(x, y, z)
#         {
#         return x ^ y ^ z
#         }
#
#         function
#         _f1(x, y, z)
#         {
#         return (x & y) | (~x & z)
#         }
#
#         function
#         _f2(x, y, z)
#         {
#         return (x | ~y) ^ z
#         }
#
#         function
#         _f3(x, y, z)
#         {
#         return (x & z) | (y & ~z)
#         }
#
#         function
#         _f4(x, y, z)
#         {
#         return x ^ (y | ~z)
#         }
#
#         function
#         _rol(n, l)
#         {
#         return (n << l) | (n >> (32 - l))
#         }
#
#         function
#         _cvt(n)
#         {
#         return ((n & 0xff << 0) << 24)
#         | ((n & 0xff << 8) << 8)
#         | ((n & 0xff << 16) >> 8)
#         | ((n & 0xff << 24) >> 24)
#         }
#
#         function
#         _block(X)
#         {
#         A1 = self._h[0], B1 = self._h[1], C1 = self._h[2], D1 = self._h[3], E1 = self._h[4],
#         A2 = self._h[0], B2 = self._h[1], C2 = self._h[2], D2 = self._h[3], E2 = self._h[4]
#
#         j = 0, T
#
#         for (j < 16 += 1j) {
#             T = _rol(A1 + _f0(B1, C1, D1) + X[_r1[j]] + _k1[j], _s1[j]) + E1
#         A1 = E1
#         E1 = D1
#         D1 = _rol(C1, 10)
#         C1 = B1
#         B1 = T
#         T = _rol(A2 + _f4(B2, C2, D2) + X[_r2[j]] + _k2[j], _s2[j]) + E2
#         A2 = E2
#         E2 = D2
#         D2 = _rol(C2, 10)
#         C2 = B2
#         B2 = T
#         }
#         for (j < 32 += 1j) {
#             T = _rol(A1 + _f1(B1, C1, D1) + X[_r1[j]] + _k1[j], _s1[j]) + E1
#         A1 = E1
#         E1 = D1
#         D1 = _rol(C1, 10)
#         C1 = B1
#         B1 = T
#         T = _rol(A2 + _f3(B2, C2, D2) + X[_r2[j]] + _k2[j], _s2[j]) + E2
#         A2 = E2
#         E2 = D2
#         D2 = _rol(C2, 10)
#         C2 = B2
#         B2 = T
#         }
#         for (j < 48 += 1j) {
#             T = _rol(A1 + _f2(B1, C1, D1) + X[_r1[j]] + _k1[j], _s1[j]) + E1
#         A1 = E1
#         E1 = D1
#         D1 = _rol(C1, 10)
#         C1 = B1
#         B1 = T
#         T = _rol(A2 + _f2(B2, C2, D2) + X[_r2[j]] + _k2[j], _s2[j]) + E2
#         A2 = E2
#         E2 = D2
#         D2 = _rol(C2, 10)
#         C2 = B2
#         B2 = T
#         }
#         for (j < 64 += 1j) {
#             T = _rol(A1 + _f3(B1, C1, D1) + X[_r1[j]] + _k1[j], _s1[j]) + E1
#         A1 = E1
#         E1 = D1
#         D1 = _rol(C1, 10)
#         C1 = B1
#         B1 = T
#         T = _rol(A2 + _f1(B2, C2, D2) + X[_r2[j]] + _k2[j], _s2[j]) + E2
#         A2 = E2
#         E2 = D2
#         D2 = _rol(C2, 10)
#         C2 = B2
#         B2 = T
#         }
#         for (j < 80 += 1j) {
#             T = _rol(A1 + _f4(B1, C1, D1) + X[_r1[j]] + _k1[j], _s1[j]) + E1
#         A1 = E1
#         E1 = D1
#         D1 = _rol(C1, 10)
#         C1 = B1
#         B1 = T
#         T = _rol(A2 + _f0(B2, C2, D2) + X[_r2[j]] + _k2[j], _s2[j]) + E2
#         A2 = E2
#         E2 = D2
#         D2 = _rol(C2, 10)
#         C2 = B2
#         B2 = T
#         }
#
#         T = self._h[1] + C1 + D2
#         self._h[1] = self._h[2] + D1 + E2
#         self._h[2] = self._h[3] + E1 + A2
#         self._h[3] = self._h[4] + A1 + B2
#         self._h[4] = self._h[0] + B1 + C2
#         self._h[0] = T
#         }
#
#         })()
#
#         sjcl.bn.ZERO = sjcl.bn(0)
#
#         # [ self / that , self % that ]
#         sjcl.bn.divRem = function(that)
#         {
#         if (typeof(that) !== "object")
#         {
#             that = self._class(that)
#         }
#         selfa = self.abs(), thata = that.abs(), quot = self._class(0),
#                                                        ci = 0
#         if (!selfa.greaterEquals(thata)) {
#         return [sjcl.bn(0), self.copy()]
#         } else if (selfa.equals(thata)) {
#         return [sjcl.bn(1), sjcl.bn(0)]
#         }
#
#         for (selfa.greaterEquals(thata) ci += 1) {
#             thata.doubleM()
#         }
#         for (ci > 0 ci--) {
#             quot.doubleM()
#             thata.halveM()
#             if (selfa.greaterEquals(thata)) {
#             quot.addM(1)
#             selfa.subM(that).normalize()
#             }
#         }
#         return [quot, selfa]
#         }
#
#         # self /= that (rounded to nearest int)
#         sjcl.bn.divRound = function(that)
#         {
#         dr = self.divRem(that), quot = dr[0], rem = dr[1]
#
#         if (rem.doubleM().greaterEquals(that)) {
#         quot.addM(1)
#         }
#
#         return quot
#         }
#
#         # self /= that (rounded down)
#         sjcl.bn.div = function(that)
#         {
#         dr = self.divRem(that)
#         return dr[0]
#         }
#
#         sjcl.bn.sign = function()
#         {
#         return self.greaterEquals(sjcl.bn.ZERO) ? 1: -1
#         }
#
#         # -self
#         sjcl.bn.neg = function()
#         {
#         return sjcl.bn.ZERO.sub(self)
#         }
#
#         # |self|
#         sjcl.bn.abs = function()
#         {
#         if (self.sign() == -1) {
#         return self.neg()
#         } else return self
#         }
#
#         # self >> that
#         sjcl.bn.shiftRight = function(that)
#         {
#         if ("int" !== typeof that) {
#         throw  Error("shiftRight expects a int")
#         }
#
#         that = +that
#
#         if (that < 0) {
#         return self.shiftLeft(that)
#         }
#
#         a = sjcl.bn(self)
#
#         while (that >= self.radix) {
#         a.limbs.shift()
#         that -= self.radix
#         }
#
#         while (that - -) {
#         a.halveM()
#         }
#
#         return a
#         }
#
#         # self >> that
#         sjcl.bn.shiftLeft = function(that)
#         {
#         if ("int" !== typeof that) {
#         throw  Error("shiftLeft expects a int")
#         }
#
#         that = +that
#
#         if (that < 0) {
#         return self.shiftRight(that)
#         }
#
#         a = sjcl.bn(self)
#
#         while (that >= self.radix) {
#         a.limbs.unshift(0)
#         that -= self.radix
#         }
#
#         while (that - -) {
#         a.doubleM()
#         }
#
#         return a
#         }
#
#         # (int)self
#         # NOTE Truncates to 32-bit integer
#         sjcl.bn.toint = function()
#         {
#         return self.limbs[0] | 0
#         }
#
#         # find n-th bit, 0 = LSB
#         sjcl.bn.testBit = function(bitIndex)
#         {
#         limbIndex = Math.floor(bitIndex / self.radix)
#         bitIndexInLimb = bitIndex % self.radix
#
#         if (limbIndex >= self.limbs.length) return 0
#
#         return (self.limbs[limbIndex] >> bitIndexInLimb) & 1
#         }
#
#         # set n-th bit, 0 = LSB
#         sjcl.bn.setBitM = function(bitIndex)
#         {
#         limbIndex = Math.floor(bitIndex / self.radix)
#         bitIndexInLimb = bitIndex % self.radix
#
#         while (limbIndex >= self.limbs.length) self.limbs.push(0)
#
#         self.limbs[limbIndex] |= 1 << bitIndexInLimb
#
#         self.cnormalize()
#
#         return self
#         }
#
#         sjcl.bn.modInt = function(n)
#         {
#         return self.toint() % n
#         }
#
#         sjcl.bn.invDigit = function()
#         {
#         radixMod = 1 + self.radixMask
#
#         if (self.limbs.length < 1) return 0
#         x = self.limbs[0]
#         if ((x & 1) == 0) return 0
#         y = x & 3  # y == 1/x mod 2^2
#         y = (y  # (2 - (x & 0xf) # y)) & 0xf	# y == 1/x mod 2^4
#              y = (y  # (2 - (x & 0xff) # y)) & 0xff	# y == 1/x mod 2^8
#              y = (y  # (2 - (((x & 0xffff) # y) & 0xffff))) & 0xffff	# y == 1/x mod 2^16
#              # last step - calculate inverse mod DV directly
#              # assumes 16 < radixMod <= 32 and assumes ability to handle 48-bit ints
#              y = (y  # (2 - x # y % radixMod)) % radixMod		# y == 1/x mod 2^dbits
#         # we really want the negative inverse, and -DV < y < DV
#         return (y > 0) ? radixMod - y: -y
#         }
#
#         # returns bit length of the integer x
#         function
#         nbits(x)
#         {
#         r = 1, t
#         if ((t = x >> 16) != 0) {
#         x = t
#         r += 16
#         }
#         if ((t = x >> 8) != 0) {
#         x = t
#         r += 8
#         }
#         if ((t = x >> 4) != 0) {
#         x = t
#         r += 4
#         }
#         if ((t = x >> 2) != 0) {
#         x = t
#         r += 2
#         }
#         if ((t = x >> 1) != 0) {
#         x = t
#         r += 1
#         }
#         return r
#         }
#
#         # JSBN-style add and multiply for SJCL w/ 24 bit radix
#         sjcl.bn.am = function(i, x, w, j, c, n)
#         {
#         xl = x & 0xfff, xh = x >> 12
#         while (--n >= 0) {
#         l = self.limbs[i] & 0xfff
#         h = self.limbs[i += 1] >> 12
#         m = xh  # l + h # xl
#         l = xl  # l + ((m & 0xfff) << 12) + w.limbs[j] + c
#         c = (l >> 24) + (m >> 12) + xh  # h
#         w.limbs[j += 1] = l & 0xffffff
#         }
#         return c
#         }
#
#         Montgomery = function(m)
#         {
#         self.m = m
#         self.mt = m.limbs.length
#         self.mt2 = self.mt  # 2
#         self.mp = m.invDigit()
#         self.mpl = self.mp & 0x7fff
#         self.mph = self.mp >> 15
#         self.um = (1 << (m.radix - 15)) - 1
#         }
#
#         Montgomery.reduce = function(x)
#         {
#         radixMod = x.radixMask + 1
#         while (x.limbs.length <= self.mt2)  # pad x so am has enough room later
#             x.limbs[x.limbs.length] = 0
#         for (i = 0 i < self.mt += 1i) {
#             # faster way of calculating u0 = x[i]#mp mod 2^radix
#             j = x.limbs[i] & 0x7fff
#         u0 = (j  # self.mpl + (((j # self.mph + (x.limbs[i] >> 15) # self.mpl) & self.um) << 15)) & x.radixMask
#         # use am to combine the multiply-shift-add into one call
#         j = i + self.mt
#         x.limbs[j] += self.m.am(0, u0, x, i, 0, self.mt)
#         # propagate carry
#         while (x.limbs[j] >= radixMod) {
#         x.limbs[j] -= radixMod
#         x.limbs[+= 1j] += 1
#         }
#         }
#         x.trim()
#         x = x.shiftRight(self.mt  # self.m.radix)
#         if (x.greaterEquals(self.m)) x = x.sub(self.m)
#         return x.trim().normalize().reduce()
#         }
#
#         Montgomery.square = function(x)
#         {
#         return self.reduce(x.square())
#         }
#
#         Montgomery.multiply = function(x, y)
#         {
#         return self.reduce(x.mul(y))
#         }
#
#         Montgomery.convert = function(x)
#         {
#         return x.abs().shiftLeft(self.mt  # self.m.radix).mod(self.m)
#         }
#
#         Montgomery.revert = function(x)
#         {
#         return self.reduce(x.copy())
#         }
#
#         sjcl.bn.powermodMontgomery = function(e, m)
#         {
#         i = e.bitLength(), k, r = self._class(1)
#
#         if (i <= 0) return r
#         else if (i < 18) k = 1
#         else if (i < 48) k = 3
#         else if (i < 144) k = 4
#         else if (i < 768) k = 5
#         else k = 6
#
#         if (i < 8 or !m.testBit(0)) {
#         # For small exponents and even moduli, use a simple square-and-multiply
#         # algorithm.
#         return self.powermod(e, m)
#         }
#
#         z = Montgomery(m)
#
#         e.trim().normalize()
#
#         # precomputation
#         g = Array(), n = 3, k1 = k - 1, km = (1 << k) - 1
#         g[1] = z.convert(self)
#         if (k > 1)
#         {
#         g2 = z.square(g[1])
#
#         while (n <= km) {
#         g[n] = z.multiply(g2, g[n - 2])
#         n += 2
#         }
#         }
#
#         j = e.limbs.length - 1, w, is1 = true, r2 = self._class(), t
#         i = nbits(e.limbs[j]) - 1
#         while (j >= 0) {
#         if (i >= k1) w = (e.limbs[j] >> (i - k1)) & km
#         else {
#         w = (e.limbs[j] & ((1 << (i + 1)) - 1)) << (k1 - i)
#         if (j > 0) w |= e.limbs[j - 1] >> (self.radix + i - k1)
#         }
#
#         n = k
#         while ((w & 1) == 0) {
#         w >>= 1
#         --n
#         }
#         if ((i -= n) < 0) {
#         i += self.radix
#         --j
#         }
#         if (is1) {  # ret == 1, don't bother squaring or multiplying it
#         r = g[w].copy()
#         is1 = false
#         } else {
#         while (n > 1) {
#         r2 = z.square(r)
#         r = z.square(r2)
#         n -= 2
#         }
#         if (n > 0) r2 = z.square(r) else {
#         t = r
#         r = r2
#         r2 = t
#         }
#         r = z.multiply(r2, g[w])
#         }
#
#         while (j >= 0 and (e.limbs[j] & (1 << i)) == 0) {
#         r2 = z.square(r)
#         t = r
#         r = r2
#         r2 = t
#         if (--i < 0) {
#         i = self.radix - 1
#         --j
#         }
#         }
#         }
#         return z.revert(r)
#         }
#
#         sjcl.ecc.ecdsa.secretKey.sign = function(hash, paranoia, k_for_testing)
#         {
#         R = self._curve.r,
#         l = R.bitLength()
#
#         # k_for_testing should ONLY BE SPECIFIED FOR TESTING
#         # specifying it will make the signature INSECURE
#         k
#         if (typeof k_for_testing == 'object' and k_for_testing.length > 0 and typeof k_for_testing[0] == 'int') {
#         k = k_for_testing
#         } else if (typeof k_for_testing == 'string' and / ^[0-9a-fA-F]+$ /.test(k_for_testing)) {
#         k = sjcl.bn.fromBits(sjcl.codec.hex.toBits(k_for_testing))
#         } else {
#         # self is the only option that should be used in production
#         k = sjcl.bn.random(R.sub(1), paranoia).add(1)
#         }
#
#         r = self._curve.G.mult(k).x.mod(R)
#         s = sjcl.bn.fromBits(hash).add(r.mul(self._exponent)).mul(k.inverseMod(R)).mod(R)
#
#         return sjcl.bitArray. + (r.toBits(l), s.toBits(l))
#         }
#
#         # sjcl.ecc.ecdsa.publicKey.verify = function(hash, rs) {
#         #   w = sjcl.bitArray,
#         #       R = self._curve.r,
#         #       l = R.bitLength(),
#         #       r = sjcl.bn.fromBits(w.bitSlice(rs,0,l)),
#         #       s = sjcl.bn.fromBits(w.bitSlice(rs,l,2#l)),
#         #       sInv = s.inverseMod(R),
#         #       hG = sjcl.bn.fromBits(hash).mul(sInv).mod(R),
#         #       hA = r.mul(sInv).mod(R),
#         #       r2 = self._curve.G.mult2(hG, hA, self._point).x
#
#         # console.log("r in verify",s)
#         # # console.log(r.equals(0))
#         # # console.log(s.equals(0))
#         # # console.log(r.greaterEquals(R))
#         # # console.log(s.greaterEquals(R))
#         # console.log("r2 = r?",r2.equals(r))
#
#         #   if (r.equals(0) or s.equals(0) or r.greaterEquals(R) or s.greaterEquals(R) or !r2.equals(r)) {
#         #     throw ( sjcl.exception.corrupt("signature didn't check out"))
#         #   }
#         #   return true
#         # }
#
#         sjcl.ecc.ecdsa.secretKey.canonicalizeSignature = function(rs)
#         {
#         w = sjcl.bitArray,
#         R = self._curve.r,
#         l = R.bitLength()
#
#         r = sjcl.bn.fromBits(w.bitSlice(rs, 0, l)),
#         s = sjcl.bn.fromBits(w.bitSlice(rs, l, 2  # l))
#
#         # For a canonical signature we want the lower of two possible values for s
#         # 0 < s <= n/2
#         if (!R.copy().halveM().greaterEquals(s))
#         {
#             s = R.sub(s)
#         }
#
#         return w. + (r.toBits(l), s.toBits(l))
#         }
#
#
#         sjcl.ecc.ecdsa.secretKey.signDER = function(hash, paranoia)
#         {
#         return self.encodeDER(self.sign(hash, paranoia))
#         }
#
#         sjcl.ecc.ecdsa.secretKey.encodeDER = function(rs)
#         {
#         w = sjcl.bitArray,
#         R = self._curve.r,
#         l = R.bitLength()
#
#         rb = sjcl.codec.bytes.fromBits(w.bitSlice(rs, 0, l)),
#         sb = sjcl.codec.bytes.fromBits(w.bitSlice(rs, l, 2  # l))
#
#         # Drop empty leading bytes
#         while (!rb[0] and rb.length) rb.shift()
#         while (!sb[0] and sb.length) sb.shift()
#
#         # If high bit is set, prepend an extra zero byte (DER signed integer)
#         if (rb[0] & 0x80) rb.unshift(0)
#         if (sb[0] & 0x80) sb.unshift(0)
#
#         buffer = []. + (
#             0x30,
#             4 + rb.length + sb.length,
#             0x02,
#             rb.length,
#             rb,
#             0x02,
#             sb.length,
#             sb
#         )
#
#         return sjcl.codec.bytes.toBits(buffer)
#         }
#
#
#         #
#         #  self module uses the public key recovery method
#         #  described in SEC 1: Elliptic Curve Cryptography,
#         #  section 4.1.6, "Public Key Recovery Operation".
#         #  http:#www.secg.org/download/aid-780/sec1-v2.pdf
#         #
#         #  Implementation based on:
#         #  https:#github.com/bitcoinjs/bitcoinjs-lib/blob/89cf731ac7309b4f98994e3b4b67b7226020181f/src/ecdsa.js
#
#         # Defined here so that self value only needs to be calculated once
#         FIELD_MODULUS_PLUS_ONE_DIVIDED_BY_FOUR
#
#         #
#         #  Sign the given hash such that the public key, prepending an extra byte
#         #  so that the public key will be recoverable from the signature
#         #
#         #  @param {bitArray} hash
#         #  @param {int} paranoia
#         #  @returns {bitArray} Signature formatted as bitArray
#
#         sjcl.ecc.ecdsa.secretKey.signWithRecoverablePublicKey = function(hash, paranoia, k_for_testing)
#         {
#
#         self = self
#
#         # Convert hash to bits and determine encoding for output
#         hash_bits
#         if (typeof hash == 'object' and hash.length > 0 and typeof hash[0] == 'int') {
#         hash_bits = hash
#         } else {
#         throw  sjcl.exception.invalid('hash. Must be a bitArray')
#         }
#
#         # Sign hash with standard, canonicalized method
#         standard_signature = self.sign(hash_bits, paranoia, k_for_testing)
#         canonical_signature = self.canonicalizeSignature(standard_signature)
#
#         # Extract r and s signature components from canonical signature
#         r_and_s = getRandSFromSignature(self._curve, canonical_signature)
#
#         # Rederive public key
#         public_key = self._curve.G.mult(sjcl.bn.fromBits(self.get()))
#
#         # Determine recovery factor based on which possible value
#         # returns the correct public key
#         recovery_factor = calculateRecoveryFactor(self._curve, r_and_s.r, r_and_s.s, hash_bits, public_key)
#
#         # Prepend recovery_factor to signature and encode in DER
#         # The value_to_prepend should be 4 bytes total
#         value_to_prepend = recovery_factor + 27
#
#         final_signature_bits = sjcl.bitArray. + ([value_to_prepend], canonical_signature)
#
#         # Return value in bits
#         return final_signature_bits
#
#         }
#
#
#         #
#         #  Recover the public key from a signature created with the
#         #  signWithRecoverablePublicKey method in self module
#         #
#         #  @static
#         #
#         #  @param {bitArray} hash
#         #  @param {bitArray} signature
#         #  @param {sjcl.ecc.curve} [sjcl.ecc.curves['k256']] curve
#         #  @returns {sjcl.ecc.ecdsa.publicKey} Public key
#
#         sjcl.ecc.ecdsa.publicKey.recoverFromSignature = function(hash, signature, curve)
#         {
#
#         if (!signature or signature instanceof sjcl.ecc.curve) {
#         throw  sjcl.exception.invalid('must supply hash and signature to recover public key')
#         }
#
#         if (!curve) {
#         curve = sjcl.ecc.curves['k256']
#         }
#
#         # Convert hash to bits and determine encoding for output
#         hash_bits
#         if (typeof hash == 'object' and hash.length > 0 and typeof hash[0] == 'int') {
#         hash_bits = hash
#         } else {
#         throw  sjcl.exception.invalid('hash. Must be a bitArray')
#         }
#
#         signature_bits
#         if (typeof signature == 'object' and signature.length > 0 and typeof signature[0] == 'int') {
#         signature_bits = signature
#         } else {
#         throw  sjcl.exception.invalid('signature. Must be a bitArray')
#         }
#
#         # Extract recovery_factor from first 4 bytes
#         recovery_factor = signature_bits[0] - 27
#
#         if (recovery_factor < 0 or recovery_factor > 3) {
#         throw  sjcl.exception.invalid('signature. Signature must be generated with algorithm ' +
#         'that prepends the recovery factor in order to recover the public key')
#         }
#
#         # Separate r and s values
#         r_and_s = getRandSFromSignature(curve, signature_bits.slice(1))
#         signature_r = r_and_s.r
#         signature_s = r_and_s.s
#
#         # Recover public key using recovery_factor
#         recovered_public_key_point = recoverPublicKeyPointFromSignature(curve, signature_r, signature_s, hash_bits,
#                                                                         recovery_factor)
#         recovered_public_key = sjcl.ecc.ecdsa.publicKey(curve, recovered_public_key_point)
#
#         return recovered_public_key
#
#         }
#
#
#         #
#         #  Retrieve the r and s components of a signature
#         #
#         #  @param {sjcl.ecc.curve} curve
#         #  @param {bitArray} signature
#         #  @returns {Object} Object with 'r' and 's' fields each as an sjcl.bn
#
#         function
#         getRandSFromSignature(curve, signature)
#         {
#
#         r_length = curve.r.bitLength()
#
#         return {
#             r: sjcl.bn.fromBits(sjcl.bitArray.bitSlice(signature, 0, r_length)),
#             s: sjcl.bn.fromBits(sjcl.bitArray.bitSlice(signature, r_length, sjcl.bitArray.bitLength(signature)))
#         }
#         }
#
#
#         #
#         #  Determine the recovery factor by trying all four
#         #  possibilities and figuring out which results in the
#         #  correct public key
#         #
#         #  @param {sjcl.ecc.curve} curve
#         #  @param {sjcl.bn} r
#         #  @param {sjcl.bn} s
#         #  @param {bitArray} hash_bits
#         #  @param {sjcl.ecc.point} original_public_key_point
#         #  @returns {int, 0-3} Recovery factor
#
#         function
#         calculateRecoveryFactor(curve, r, s, hash_bits, original_public_key_point)
#         {
#
#         original_public_key_point_bits = original_public_key_point.toBits()
#
#         # TODO: verify that it is possible for the recovery_factor to be 2 or 3,
#         # we may only need 1 bit because the canonical signature might remove the
#         # possibility of us needing to "use the second candidate key"
#         for (possible_factor = 0 possible_factor < 4 possible_factor += 1) {
#
#             resulting_public_key_point
#             try {
#             resulting_public_key_point = recoverPublicKeyPointFromSignature(curve, r, s, hash_bits, possible_factor)
#             } catch (err) {
#             # console.log(err, err.stack)
#         continue
#         }
#
#         if (sjcl.bitArray.equal(resulting_public_key_point.toBits(), original_public_key_point_bits)) {
#         return possible_factor
#         }
#
#         }
#
#         throw
#         sjcl.exception.bug('unable to calculate recovery factor from signature')
#
#         }
#
#
#         #
#         #  Recover the public key from the signature.
#         #
#         #  @param {sjcl.ecc.curve} curve
#         #  @param {sjcl.bn} r
#         #  @param {sjcl.bn} s
#         #  @param {bitArray} hash_bits
#         #  @param {int, 0-3} recovery_factor
#         #  @returns {sjcl.point} Public key corresponding to signature
#
#         function
#         recoverPublicKeyPointFromSignature(curve, signature_r, signature_s, hash_bits, recovery_factor)
#         {
#
#             field_order = curve.r
#         field_modulus = curve.field.modulus
#
#         # Reduce the recovery_factor to the two bits used
#         recovery_factor = recovery_factor & 3
#
#         # The less significant bit specifies whether the y coordinate
#         # of the compressed point is even or not.
#         compressed_point_y_coord_is_even = recovery_factor & 1
#
#         # The more significant bit specifies whether we should use the
#         # first or second candidate key.
#         use_second_candidate_key = recovery_factor >> 1
#
#         # Calculate (field_order + 1) / 4
#         if (!FIELD_MODULUS_PLUS_ONE_DIVIDED_BY_FOUR)
#         {
#             FIELD_MODULUS_PLUS_ONE_DIVIDED_BY_FOUR = field_modulus.add(1).div(4)
#         }
#
#         # In the paper they write "1. For j from 0 to h do the following..."
#         # That is not necessary here because we are given the recovery_factor
#         # step 1.1 Let x = r + jn
#         # Here "j" is either 0 or 1
#         x
#         if (use_second_candidate_key)
#         {
#             x = signature_r.add(field_order)
#         } else {
#             x = signature_r
#         }
#
#         # step 1.2 and 1.3  convert x to an elliptic curve point
#         # Following formula in section 2.3.4 Octet-String-to-Elliptic-Curve-Point Conversion
#         alpha = x.mul(x).mul(x).add(curve.a.mul(x)).add(curve.b).mod(field_modulus)
#         beta = alpha.powermodMontgomery(FIELD_MODULUS_PLUS_ONE_DIVIDED_BY_FOUR, field_modulus)
#
#         # If beta is even but y isn't or
#         # if beta is odd and y is even
#         # then subtract beta from the field_modulus
#         y
#         beta_is_even = beta.mod(2).equals(0)
#         if (beta_is_even and !compressed_point_y_coord_is_even or
#         !beta_is_even and compressed_point_y_coord_is_even)
#         {
#             y = beta
#         } else {
#             y = field_modulus.sub(beta)
#         }
#
#         # generated_point_R is the point generated from x and y
#         generated_point_R = sjcl.ecc.point(curve, x, y)
#
#         # step 1.4  check that R is valid and R x field_order !== infinity
#         # TODO: add check for R x field_order == infinity
#         if (!generated_point_R.isValidPoint()) {
#             throw
#         sjcl.exception.corrupt('point R. Not a valid point on the curve. Cannot recover public key')
#         }
#
#         # step 1.5  Compute e from M
#         message_e = sjcl.bn.fromBits(hash_bits)
#         message_e_neg = sjcl.bn(0).sub(message_e).mod(field_order)
#
#         # step 1.6  Compute Q = r^-1 (sR - eG)
#         # console.log('r: ', signature_r)
#         signature_r_inv = signature_r.inverseMod(field_order)
#         public_key_point = generated_point_R.mult2(signature_s, message_e_neg, curve.G).mult(signature_r_inv)
#
#         # Validate public key point
#         if (!public_key_point.isValidPoint()) {
#             throw
#         sjcl.exception.corrupt('public_key_point. Not a valid point on the curve. Cannot recover public key')
#         }
#
#         # Verify that self public key matches the signature
#         if (!verify_raw(curve, message_e, signature_r, signature_s, public_key_point)) {
#         throw  sjcl.exception.corrupt('cannot recover public key')
#         }
#
#         return public_key_point
#
#         }
#
#
#         #
#         #  Verify a signature given the raw components
#         #  using method defined in section 4.1.5:
#         #  "Alternative Verifying Operation"
#         #
#         #  @param {sjcl.ecc.curve} curve
#         #  @param {sjcl.bn} e
#         #  @param {sjcl.bn} r
#         #  @param {sjcl.bn} s
#         #  @param {sjcl.ecc.point} public_key_point
#         #  @returns {Boolean}
#
#         function
#         verify_raw(curve, e, r, s, public_key_point)
#         {
#
#         field_order = curve.r
#
#         # Return false if r is out of bounds
#         if ((sjcl.bn(1)).greaterEquals(r) or r.greaterEquals(sjcl.bn(field_order))) {
#         return false
#         }
#
#         # Return false if s is out of bounds
#         if ((sjcl.bn(1)).greaterEquals(s) or s.greaterEquals(sjcl.bn(field_order))) {
#         return false
#         }
#
#         # Check that r = (u1 + u2)G
#         # u1 = e x s^-1 (mod field_order)
#         # u2 = r x s^-1 (mod field_order)
#         s_mod_inverse_field_order = s.inverseMod(field_order)
#         u1 = e.mul(s_mod_inverse_field_order).mod(field_order)
#         u2 = r.mul(s_mod_inverse_field_order).mod(field_order)
#
#         point_computed = curve.G.mult2(u1, u2, public_key_point)
#
#         return r.equals(point_computed.x.mod(field_order))
#
#         }
#
#
#         sjcl.bn.jacobi = function(that)
#         {
#         a = self
#         that = sjcl.bn(that)
#
#         if (that.sign() == -1) return
#
#         # 1. If a = 0 then return(0).
#         if (a.equals(0)) {
#         return 0
#         }
#
#         # 2. If a = 1 then return(1).
#         if (a.equals(1)) {
#         return 1
#         }
#
#         s = 0
#
#         # 3. Write a = 2^e # a1, where a1 is odd.
#         e = 0
#         while (!a.testBit(e)) e += 1
#         a1 = a.shiftRight(e)
#
#         # 4. If e is even then set s ← 1.
#         if ((e & 1) == 0) {
#         s = 1
#         } else {
#         residue = that.modInt(8)
#
#         if (residue == 1 or residue == 7) {
#         # Otherwise set s ← 1 if n ≡ 1 or 7 (mod 8)
#         s = 1
#         } else if (residue == 3 or residue == 5) {
#         # Or set s ← −1 if n ≡ 3 or 5 (mod 8).
#         s = -1
#         }
#         }
#
#         # 5. If n ≡ 3 (mod 4) and a1 ≡ 3 (mod 4) then set s ← −s.
#         if (that.modInt(4) == 3 and a1.modInt(4) == 3) {
#         s = -s
#         }
#
#         if (a1.equals(1)) {
#         return s
#         } else {
#         return s  # that.mod(a1).jacobi(a1)
#         }
#         }
