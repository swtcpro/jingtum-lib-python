# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/17
 * Time: 11:25
 * Description: 钱包模块
"""
from keypairs import keypairs
from elliptic import elliptic
from utils import hexToBytes, bytesToHex
#var hashjs = require('hash.js');
#from hash import hashpy
ec = elliptic.ec

def hash(message):
  return hashjs.sha512().update(message).digest().slice(0, 32)

class Wallet:
	def __init__(self, secret):
		try:
			self._keypairs = keypairs.deriveKeyPair(secret)
			self._secret = secret
		except Exception:
			self._keypairs = null
			self._secret = null

	"""
	 * static funcion
	 * generate one wallet
	 * @returns {{secret: string, address: string}}
	"""
	def generate():
		secret = keypairs.generateSeed()
		keypair = keypairs.deriveKeyPair(secret)
		address = keypairs.deriveAddress(keypair.publicKey)
		return {secret: secret, address: address}

	"""
	 * static function
	 * generate one wallet from secret
	 * @param secret
	 * @returns {*}
	"""
	def fromSecret(secret):
		try:
			keypair = keypairs.deriveKeyPair(secret)
			address = keypairs.deriveAddress(keypair.publicKey)
			return {secret: secret, address: address}
		except Exception:
			return null
			
	"""
	 * static function
	 * check if address is valid
	 * @param address
	 * @returns {boolean}
	"""
	def isValidAddress(address):
		return keypairs.checkAddress(address)

	"""
	 * static function
	 * check if secret is valid
	 * @param secret
	 * @returns {boolean}
	"""
	def isValidSecret(secret):
		try:
			keypairs.deriveKeyPair(secret)
			return true
		except Exception:
			return false

	"""
	 * sign message with wallet privatekey
	 * @param message
	 * @returns {*}
	"""
	def sign(self, message):
		if (not message or message.length == 0): 
			return null
		if (not self._keypairs): 
			return null
		privateKey = self._keypairs.privateKey;
		return bytesToHex(ec.sign(hash(message), hexToBytes(privateKey), { canonical: true }).toDER());

	"""
	 * verify signature with wallet publickey
	 * @param message
	 * @param signature
	 * @returns {*}
	"""
	def verify(self, message, signature):
		if not self._keypairs:
			return null
		publicKey = self._keypairs.publicKey
		return ec.verify(hash(message), signature, hexToBytes(publicKey))

	"""
	 * get wallet address
	 * @returns {*}
	"""
	def address(self):
		if not self._keypairs:
			return null
		address = keypairs.deriveAddress(self._keypairs.publicKey)
		return address

	"""
	 * get wallet secret
	 * @returns {*}
	"""
	def secret(self):
		if not self._keypairs: 
			return null
		return self._secret

	def toJson(self):
		if not self._keypairs:
			return null
		return {
			secret: secret(),
			address: address()
		}
