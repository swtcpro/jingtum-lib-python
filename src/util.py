"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/30
 * Time: 23:35
 * Description: 
"""

from numbers import Number

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


def process_affect_node(node):
    result = dict()

    for node_action in ["CreatedNode", "ModifiedNode", "DeletedNode"]:
        if node[node_action]:
            result.diffType = node_action

    if not result.diffType:
        return None

    node = node[result.diffType]
    result.entryType = node.LedgerEntryType
    result.ledgerIndex = node.LedgerIndex
    result.fields = {**{**node.PreviousFields, **node.NewFields}, **node.FinalFields}
    result.fieldsPrev = node.PreviousFields or {}
    result.fieldsNew = node.NewFields or {}
    result.fieldsFinal = node.FinalFields or {}
    result.PreviousTxnID = node.PreviousTxnID

    return result


def affected_accounts(data):
    """
    get effect accounts
    :param data:
    :return: {Array}
    """
    accounts = dict()
    accounts[data.transaction.Account] = 1
    if data.transaction.Destination:
        accounts[data.transaction.Destination] = 1
    if data.transaction.LimitAmount:
        accounts[data.transaction.LimitAmount.issuer] = 1
    if data.meta and data.meta.TransactionResult == 'tesSUCCESS':
        for node in data.meta.AffectedNodes:
            node = process_affect_node(node)
            if node.entryType == 'AccountRoot' and node.fields.Account:
                accounts[node.fields.Account] = 1
            if node.entryType == 'SkywellState':
                if node.fields.HighLimit.issuer:
                    accounts[node.fields.HighLimit.issuer] = 1
                if node.fields.LowLimit.issuer:
                    accounts[node.fields.LowLimit.issuer] = 1
            if node.entryType == 'Offer' and node.fields.Account:
                accounts[node.fields.Account] = 1

    return dict.keys(accounts)


def txn_type(tx, account):
    pass


def parse_amount(Amount):
    pass


def reverse_amount(LimitAmount, Account):
    pass


def format_args(Args):
    pass


def process_tx(txn, account):
    """
    process transaction in view of account
    get basic transaction information,
    and transaction effects
    :param txn:
    :param account:
    :return:
    """
    tx = txn.tx or txn.transaction or txn
    meta = txn.meta
    result = dict()
    result.date = (tx.date or tx.Timestamp) + 0x386D4380  # unix time
    result.hash = tx.hash
    result.type = txn_type(tx, account)
    # 此处同样有疑问 float 和 Number 的用法
    result.fee = str(float(tx.Fee) / 1000000.0)
    result.result = meta.TransactionResult if meta else 'failed'
    result.memos = []

    if result.type == 'sent':
        result.counterparty = tx.Destination
        result.amount = parse_amount(tx.Amount)

    elif result.type == 'received':
        result.counterparty = tx.Account
        result.amount = parse_amount(tx.Amount)

    elif result.type == 'trusted':
        result.counterparty = tx.Account
        result.amount = reverse_amount(tx.LimitAmount, tx.Account)

    elif result.type == 'trusting':
        result.counterparty = tx.LimitAmount.issuer
        result.amount = tx.LimitAmount

    elif result.type == 'convert':
        result.spent = parse_amount(tx.SendMax)
        result.amount = parse_amount(tx.Amount)

    elif result.type == 'offernew':
        # result.offertype = tx.Flags & Transaction.flags.OfferCreate.Sell ? 'sell': 'buy'
        result.gets = parse_amount(tx.TakerGets)
        result.pays = parse_amount(tx.TakerPays)
        result.seq = tx.Sequence

    elif result.type == 'offercancel':
        result.offerseq = tx.Sequence

    elif result.type == 'relationset':
        if account == tx.Target:
            result.counterparty = tx.Account
        else:
            result.counterparty = tx.Target

        if tx.RelationType == 3:
            result.relationtype = 'freeze'
        else:
            result.relationtype = 'authorize'

        if account == tx.Target:
            result.isactive = False
        else:
            result.isactive = True
        result.amount = parse_amount(tx.LimitAmount)

    elif result.type == 'configcontract':
        result.params = format_args(tx.Args)
        if tx.Method == 0:
            result.method = 'deploy'
            result.payload = tx.Payload
        elif tx.Method == 1:
            result.method = 'call'
            result.destination = tx.Destination

    # add memo
    from encodings.utf_8 import decode
    if isinstance(tx.Memos, list) and tx.Memos.__len__() > 0:
        for Memo in tx.Memos:  # 此处认定数组Memos中的元素为字典
            for key in Memo:
                try:
                    Memo[key] = decode(__hexToString(Memo[key]))
                except:
                    Memo[key] = Memo[key]
        result.memos.append(Memo)

    result.effects = []
    # no effect, return now
