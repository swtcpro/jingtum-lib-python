"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/30
 * Time: 23:35
 * Description: 
"""
from jingtum_python_baselib.src.wallet import Wallet

# Flags for ledger entries
LEDGER_FLAGS = {
    # Account Root
    'account_root': {
        'PasswordSpent': 0x00010000,  # True, if password set fee is spent.
        'RequireDestTag': 0x00020000,  # True, to require a DestinationTag for payments.
        'RequireAuth': 0x00040000,  # True, to require a authorization to hold IOUs.
        'DisallowSWT': 0x00080000,  # True, to disallow sending SWT.
        'DisableMaster': 0x00100000  # True, force regular key.
    },

    # Offer
    'offer': {
        'Passive': 0x00010000,
        'Sell': 0x00020000  # True, offer was placed as a sell.
    },

    # Skywell State
    'state': {
        'LowReserve': 0x00010000,  # True, if entry counts toward reserve.
        'HighReserve': 0x00020000,
        'LowAuth': 0x00040000,
        'HighAuth': 0x00080000,
        'LowNoSkywell': 0x00100000,
        'HighNoSkywell': 0x00200000
    }
}


def __hexToString(h):
    a = []
    i = 0
    strLength = len(h)

    if strLength % 2 == 0:
        a.extend(chr(int(h[0: 1], 16)))
        i = 1

    for index in range(i, strLength, 2):
        a.extend(chr(int(h[index: index + 2]), 16))

    return ''.join(a)


def __stringToHex(s):
    result = ''
    for c in s:
        b = ord(c)
        # 转换成16进制的ASCII码
        if b < 16:
            result += '0' + hex(b).replace('0x', '')
        else:
            result += hex(b).replace('0x', '')

    return result


def is_valid_address(account):
    """
    直接调用baselib中的isValidAddress方法，该方法由蔡正龙编写
    :param account:
    :return:
    """
    return Wallet.isValidAddress(account)
