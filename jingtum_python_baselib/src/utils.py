# coding=gbk
"""
 * User: 蔡正龙
 * Date: 2018/5/16
 * Time: 11:25
 * Description: 钱包依赖的模块
"""
# import random
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
