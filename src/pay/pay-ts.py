# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 支付与设置关系模块
"""

# below are Transaction need module	
class Transaction:
	"""
	 * set secret
	 * @param secret
	 * come from transaction.js
	 * 传入密钥
	"""
	def setSecret(self, secret):
		self._secret = secret
	
	def __stringToHex(s):
		result = '';
		i = 0
		while i<s.length:
			b = s.charCodeAt(i)
			if b<16 :
				result += '0' + b.toString(16)
			else:
				result += b.toString(16)
			i += 1
		return result

	"""
	 * just only memo data
	 * @param memo
	 * 设置备注
	"""
	def addMemo(self, memo):
		if not isinstance(memo, str):
			self.tx_json.memo_type = Error('invalid memo type')
			return self
		if (len(memo) > 2048):
			self.tx_json.memo_len = Error('memo is too long')
			return self
		_memo = {}
		_memo.MemoData = __stringToHex(memo.encode('utf-8'))
		self.tx_json.Memos = self.tx_json.Memos + Memo
		
	"""
	 * submit request to server
	 * @param callback
	 * 提交支付
	"""
	def submit(self, callback):
		for key in self.tx_json:
			if instanceof(self.tx_json[key], Error):
				return callback(self.tx_json[key].message)
        
		data = {}
		if self._remote._local_sign: #签名之后传给底层
			self.sign(Error, blob)
			if Error:
				return callback('sign error: ', Error)
			else:
				data = {
					tx_blob: self.tx_json.blob
				}
				self._remote._submit('submit', data, self._filter, callback)
		elif self.tx_json.TransactionType == 'Signer': #直接将blob传给底层
			data = {
				tx_blob: self.tx_json.blob
			};
			self._remote._submit('submit', data, self._filter, callback)
		else: #不签名交易传给底层
			data = {
				secret: self._secret,
				tx_json: self.tx_json
			}
			self._remote._submit('submit', data, self._filter, callback)
