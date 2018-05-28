# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/21
 * Time: 11:25
 * Description: 测试模块
"""
import sys 
sys.path.append("../src")
from utils import utils

a=utils.hexToBytes('123344')
print(a)
a=utils.bytesToHex([0x12,0x56,35])
print(a)
