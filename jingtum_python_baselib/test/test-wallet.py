# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/21
 * Time: 11:25
 * Description: 测试模块
"""
#import sys
#sys.path.append("..")
from jingtum_python_baselib.src.wallet import *

w1 = Wallet.generate()
print('w1 is', w1)

w2 = Wallet.fromSecret('ss2A7yahPhoduQjmG7z9BHu3uReDk')
print('w2 is', w2)

w3 = Wallet.isValidAddress('jHCkiZVyvQe2MS8XpCpmDVXq3e1xsmqo8g')
print('isValidAddress ', w3)

w4 = Wallet.isValidSecret('ss2A7yahPhoduQjmG7z9BHu3uReDk')
print('isValidSecret ', w4)