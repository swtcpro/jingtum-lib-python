# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
"""
# base-x encoding
# Forked from https:#github.com/cryptocoinjs/bs58
# Originally written by Mike Hearn for BitcoinJ
# Copyright (c) 2011 Google Inc
# Ported to JavaScript by Stefan Thomas
# Merged Buffer refactorings from base58-native by Stephen Pair
# Copyright (c) 2013 BitPay Inc
ALPHABET = 'jpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65rkm8oFqi1tuvAxyz'
BASE = len(ALPHABET)

class base58():
	def __init__(self):
		self.ALPHABET_MAP = {}
		self.LEADER = ALPHABET[0]

		# pre-compute lookup table
		i = 0
		while i < len(ALPHABET):
			self.ALPHABET_MAP[ALPHABET[i]] = i
			i += 1

	def encode (source):
		if len(source) == 0:
			return ''

		digits = [0]
		i = 0
		while i < len(source):
			j = 0
			carry = source[i]
			while j < len(digits):
				carry += digits[j] << 8
				digits.append(carry % BASE)
				carry = (carry / BASE) | 0
				j += 1

			while (carry > 0):
				digits.append(carry % BASE)
				carry = (carry / BASE) | 0

			i += 1
		string = ''

		# deal with leading zeros
		k = 0
		while source[k] == 0 and k < len(source) - 1:
			string += ALPHABET[0]
			k += 1

		# convert digits to a string
		q = len(digits) - 1
		while q >= 0:
			string += ALPHABET[digits[q]]
			q -= 1

		return string

	def decodeUnsafe(self, string):
		if len(string) == 0:
			return []

		bytes = [0]
		i = 0
		while i < len(string):
			value = self.ALPHABET_MAP[string[i]]
			if not value:
				return

			j = 0
			carry = value
			while j < len(bytes):
				carry += bytes[j] * BASE
				bytes[j] = carry & 0xff
				carry >>= 8
				j += 1

			while (carry > 0):
				bytes.append(carry & 0xff)
				carry >>= 8

			i += 1

		# deal with leading zeros
		k = 0
		while string[k] == self.LEADER and k < len(string) - 1:
			bytes.append(0)
			k += 1

		return bytes.reverse()

	def decode(self, string):
		array = self.decodeUnsafe(string)
		if (array): 
			return array

		raise Exception('Non-base' + BASE + ' character')

"""
return {
	'encode': encode,
	'decodeUnsafe': decodeUnsafe,
	'decode': decode
}
"""
