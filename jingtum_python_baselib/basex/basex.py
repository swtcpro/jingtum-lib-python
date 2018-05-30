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

class basex():
	def __init__():
		ALPHABET_MAP = {}
		BASE = len(ALPHABET)
		LEADER = ALPHABET[0]

		# pre-compute lookup table
		i = 0
		while i < len(ALPHABET):
			ALPHABET_MAP[ALPHABET[i]] = i
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
				digits[j] = carry % BASE
				carry = (carry / BASE) | 0
				j += 1
			i += 1

			while (carry > 0):
				digits.push(carry % BASE)
				carry = (carry / BASE) | 0

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

	def decodeUnsafe(string):
		if len(string) == 0:
			return []

		bytes = [0]
		i = 0
		while i < len(string):
			value = ALPHABET_MAP[string[i]]
			if (value == undefined):
				return

			j = 0
			carry = value
			while j < len(bytes):
				carry += bytes[j] * BASE
				bytes[j] = carry & 0xff
				carry >>= 8
				j += 1

			while (carry > 0):
				bytes.push(carry & 0xff)
				carry >>= 8
				i += 1

		# deal with leading zeros
		k = 0
		while string[k] == LEADER and k < len(string) - 1:
			bytes.push(0)
			k += 1

		return bytes.reverse()

	def decode(string):
		array = decodeUnsafe(string)
		if (array): 
			return array

		raise Exception('Non-base' + BASE + ' character')

"""
	return {
	encode: encode,
	decodeUnsafe: decodeUnsafe,
	decode: decode
	}
"""
