# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 钱包依赖的模块
"""
# from elliptic import ec
#import sha512
# ec=EC('secp256k1')

import hashlib

"""
 * Scalar multiplication to find one 256 bit number
 * where it is less than the order of the curve.
 * @param bytes
 * @param discrim
 * @returns {*}
 * @constructor
"""
def ScalarMultiple(bytes, discrim):
	order = ec.curve.n
	"""
	function BaseCurve(type, conf) {
  this.type = type;
  this.p = new BN(conf.p, 16);

  // Use Montgomery, when there is no fast reduction for the prime
  this.red = conf.prime ? BN.red(conf.prime) : BN.mont(this.p);

  // Useful for many curves
  this.zero = new BN(0).toRed(this.red);
  this.one = new BN(1).toRed(this.red);
  this.two = new BN(2).toRed(this.red);

  // Curve configuration, optional
  this.n = conf.n && new BN(conf.n, 16);
  """
  
	i = 0
	while i <= 0xFFFFFFFF:
		#We hash the bytes to find a 256 bit number, looping until we are sure it
		# is less than the order of the curve.
		hasher = hashlib.sha512().add(bytes)
		# If the optional discriminator index was passed in, update the hash.
		if discrim:
			hasher.addU32(discrim)
		hasher.addU32(i)
		key = hasher.first256BN()
		if (key.cmpn(0) > 0 and key.cmp(order) < 0):
			return key
		i += 1
	Error('impossible space search')
