"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/30
 * Time: 23:35
 * Description: 
"""

import re

from jingtum_python_baselib.wallet import Wallet
from src.config import Config

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


def hexToString(h):
    a = []
    i = 0
    strLength = len(h)

    if strLength % 2:
        a.extend(chr(int(h[0: 1], 16)))
        i = 1

    for index in range(i, strLength, 2):
        a.extend(chr(int(h[index: index + 2], 16)))

    # print('hexToString result is', a)
    return ''.join(a)


def stringToHex(s):
    result = ''
    for c in s:
        b = ord(c)
        # 转换成16进制的ASCII码
        if b < 16:
            result += '0' + hex(b).replace('0x', '')
        else:
            result += hex(b).replace('0x', '')

    return result


# print(bytes(hexToString('e7bb996a44556a716f445a4c687a78344443663670765369766a6b6a677452455359363263e694afe4bb98302e357377742e')).decode('utf8'))

def is_valid_address(account):
    """
    直接调用baselib中的isValidAddress方法，该方法由蔡正龙编写
    :param account:
    :return:
    """
    return Wallet.is_valid_address(account)


HASH__RE = '^[A-F0-9]{64}$'


def is_valid_hash(hash):
    """
     hash check for tx and ledger hash
    :param hash:
    :return: {boolean}
    """
    if not hash or not isinstance(hash, str) or hash == '':
        return False
    return re.match(re.compile(HASH__RE), hash)


def process_affect_node(node):
    result = dict()

    for node_action in ["CreatedNode", "ModifiedNode", "DeletedNode"]:
        if node.__contains__(node_action):
            result['diffType'] = node_action

    if not result['diffType']:
        return None

    node = node[result['diffType']]
    result['entryType'] = node['LedgerEntryType']
    result['ledgerIndex'] = node['LedgerIndex']
    # result['fields'] = {**{**node['PreviousFields'], **node['NewFields']}, **node['FinalFields']}
    if node.__contains__('PreviousFields'):
        result['fields'] = node['PreviousFields']
        result['fieldsPrev'] = node['PreviousFields'] or {}
    if node.__contains__('NewFields'):
        result['fields'] = node['NewFields']
        result['fieldsNew'] = node['NewFields'] or {}
    if node.__contains__('FinalFields'):
        result['fields'] = node['FinalFields']
        result['fieldsFinal'] = node['FinalFields'] or {}
    # result['fieldsPrev'] = node['PreviousFields'] or {}
    # result['fieldsNew'] = node['NewFields'] or {}
    # result['fieldsFinal'] = node['FinalFields'] or {}
    if node.__contains__('PreviousTxnID'):
        result['PreviousTxnID'] = node['PreviousTxnID']
    return result


def affected_accounts(tx):
    """
    get effect accounts
    :param tx:
    :return: {Array}
    """
    accounts = dict()
    accounts[tx['transaction']['Account']] = 1
    if tx['transaction']['Destination']:
        accounts[tx['transaction']['Destination']] = 1
    if tx['transaction']['LimitAmount']:
        accounts[tx['transaction']['LimitAmount']['issuer']] = 1
    if tx['meta'] and tx['meta']['TransactionResult'] == 'tesSUCCESS':
        for node in tx['meta']['AffectedNodes']:
            node = process_affect_node(node)
            if node['entryType'] == 'AccountRoot' and node['fields']['Account']:
                accounts[node['fields']['Account']] = 1
            if node['entryType'] == 'SkywellState':
                if node['fields']['HighLimit']['issuer']:
                    accounts[node['fields']['HighLimit']['issuer']] = 1
                if node['fields']['LowLimit']['issuer']:
                    accounts['fields']['LowLimit']['issuer'] = 1
            if node['entryType'] == 'Offer' and node['fields']['Account']:
                accounts[node['fields']['Account']] = 1

    return dict.keys(accounts)


def txn_type(tx, account):
    if tx['Account'] == account or (tx.__contains__('Target') and tx['Target'] == account) or (tx['Destination'] and tx['Destination'] == account) \
            or (tx['LimitAmount'] and tx['LimitAmount']['issuer'] == account):
        if tx['TransactionType'] == 'Payment':
            if tx['Account'] == account and tx['Destination'] == account:
                return 'convert'
            if tx['Account'] == account and tx['Destination'] != account:
                return 'sent'
            if tx['Account'] != account and tx['Destination'] != account:
                return 'received'
        elif tx['TransactionType'] == 'OfferCreate':
            return 'offernew'
        elif tx['TransactionType'] == 'OfferCancel':
            return 'offercancel'
        elif tx['TransactionType'] == 'TrustSet':
            if tx['Account'] == account:
                return 'trusting'
            else:
                return 'trusted'
        elif tx['TransactionType'] == 'ConfigContract':
            return tx['TransactionType'].lower()
        else:
            return 'unknown'
    else:
        return 'offereffect'


CURRENCY_RE = '^([a-zA-Z0-9]{3,6}|[A-F0-9]{40})$'


def is_valid_currency(currency):
    if (not currency or not isinstance(currency, str) or currency == ''):
        return False
    if re.search(CURRENCY_RE, currency):  # 判断字符串是否符合某一正则表达式
        return True
    else:
        return False


# input num may contain one '.' and one '-'
def is_num(amount):
    return str(amount).replace('.', '', 1).replace('-', '', 1).isdigit()


"""
 * check {value: '', currency:'', issuer: ''}
 * @param amount
 * @returns {boolean}
"""


def is_valid_amount(amount):
    if (not amount):
        return False
    # check amount value
    if ((not amount.__contains__('value') and amount['value'] != 0) or not is_num(amount['value'])):
        return False
    # check amount currency
    if (not amount.__contains__('currency') or not is_valid_currency(amount['currency'])):
        return False
    # native currency issuer is empty
    if (amount['currency'] == Config.currency and amount['issuer'] != ''):
        return False
    # non native currency issuer is not allowed to be empty
    if (amount['currency'] != Config.currency
            and not Wallet.is_valid_address(amount['issuer'])):
        return False
    return True


def parse_amount(amount):
    if isinstance(amount, str) and float(amount):
        value = str(float(amount) / 1000000.0)
        return {'value': value, 'currency': 'SWT', 'issuer': ''}
    elif isinstance(amount, dict) and is_valid_amount(amount):
        return amount
    pass


def reverse_amount(amount, account):
    """
    get counterparty amount
    :param amount:
    :param account:
    :return: {{value: string, currency: *, issuer: *}}
    """
    return {
        'value': str(-float(amount['value'])),
        'currency': amount['currency'],
        'issuer': account
    }
    pass


from jingtum_python_baselib import utils as base_utils


def format_args(args):
    new_args = []
    if args:
        for arg in args:
            new_args.append(base_utils.hex_to_str(arg['Arg']['Parameter']))
    return new_args


def is_amount_zero(amount):
    if not amount:
        return False
    return float(amount['value']) < 1e-12


def amount_add(amount1, amount2):
    if not amount1:
        return amount2
    if not amount2:
        return amount1
    if amount1 and amount2:
        return {
            'value': str(float(amount1['value']) - amount2['value']),
            'currency': amount1['currency'],
            'issuer': amount1['issuer']
        }


def amount_negate(amount):
    if not amount:
        return amount
    return {
        'value': str(-float(amount['value'])),
        'currency': amount['currency'],
        'issuer': amount['issuer']
    }


def amount_subtract(amount1, amount2):
    return amount_add(amount1, amount_negate(amount2))


def amount_ratio(amount1, amount2):
    return str(float(amount1['value']) / float(amount2['value']))


def get_price(effect, funded):
    if effect['got']:
        g = effect['got']
    else:
        g = effect['pays']
    if effect['paid']:
        p = effect['paid']
    else:
        p = effect['gets']
    if not funded:
        return amount_ratio(g, p)
    else:
        return amount_ratio(p, g)


def process_tx(txn, account):
    """
    process transaction in view of account
    get basic transaction information,
    and transaction effects
    :param txn:
    :param account:
    :return:
    """
    tx = txn['tx'] or txn['transaction'] or txn
    meta = txn['meta']
    result = dict()
    result['date'] = (tx['date'] or tx['Timestamp']) + 0x386D4380  # unix time
    result['hash'] = tx['hash']
    result['type'] = txn_type(tx, account)
    # 此处同样有疑问 float 和 Number 的用法
    result['fee'] = str(float(tx['Fee']) / 1000000.0)
    result['result'] = meta['TransactionResult'] if meta else 'failed'
    result['memos'] = []

    if result['type'] == 'sent':
        result['counterparty'] = tx['Destination']
        result['amount'] = parse_amount(tx['Amount'])

    elif result['type'] == 'received':
        result['counterparty'] = tx['Account']
        result['amount'] = parse_amount(tx['Amount'])

    elif result['type'] == 'trusted':
        result['counterparty'] = tx['Account']
        result['amount'] = reverse_amount(tx['LimitAmount'], tx['Account'])

    elif result['type'] == 'trusting':
        result['counterparty'] = tx['LimitAmount']['issuer']
        result['amount'] = tx['LimitAmount']

    elif result['type'] == 'convert':
        result['spent'] = parse_amount(tx['SendMax'])
        result['amount'] = parse_amount(tx['Amount'])

    elif result['type'] == 'offernew':
        # result.offertype = tx.Flags & Transaction.flags.OfferCreate.Sell ? 'sell': 'buy'
        result['gets'] = parse_amount(tx['TakerGets'])
        result['pays'] = parse_amount(tx['TakerPays'])
        result['seq'] = tx['Sequence']

    elif result['type'] == 'offercancel':
        result['offerseq'] = tx['Sequence']

    elif result['type'] == 'relationset':
        if account == tx['Target']:
            result['counterparty'] = tx['Account']
        else:
            result['counterparty'] = tx['Target']

        if tx['RelationType'] == 3:
            result['relationtype'] = 'freeze'
        else:
            result['relationtype'] = 'authorize'

        if account == tx['Target']:
            result['isactive'] = False
        else:
            result['isactive'] = True
        result['amount'] = parse_amount(tx['LimitAmount'])

    elif result['type'] == 'configcontract':
        result['params'] = format_args(tx['Args'])
        if tx['Method'] == 0:
            result['method'] = 'deploy'
            result['payload'] = tx['Payload']
        elif tx['Method'] == 1:
            result['method'] = 'call'
            result['destination'] = tx['Destination']

    # add memo
    from encodings.utf_8 import decode
    if tx.__contains__('Memos') and isinstance(tx['Memos'], list) and tx['Memos'].__len__() > 0:
        for Memo in tx['Memos']:  # 此处认定数组Memos中的元素为字典
            for key in Memo:
                try:
                    Memo[key] = decode(base_utils.hex_to_str(Memo[key]))
                except:
                    Memo[key] = Memo[key]
            result['memos'].append(Memo)

    result['effects'] = []
    # no effect, return now
    if not meta or meta['TransactionResult'] != 'tesSUCCESS':
        return result

    # process effects
    for n in meta['AffectedNodes']:
        node = process_affect_node(n)
        effect = dict()
        # now only get offer related effects, need to process other entry type
        if node['entryType'] == 'offer':
            # for new and cancelled offers
            fieldSet = node['fields']
            sell = node['fields']['Flags'] and LEDGER_FLAGS['offer']['Sell']
            # current account offer
            if node['fields']['Account'] == account:
                # 1. offer_partially_funded
                if node['diffType'] == 'ModifiedNode' or (node['diffType'] == 'DeletedNode'
                                                          and node['fieldsPrev']['TakerGets'] and not is_amount_zero(
                            parse_amount(node['fieldsFinal']['TakerGets']))):
                    effect['effect'] = 'offer_partially_funded'
                    effect['counterparty'] = {'account': tx['Account'], 'seq': tx['Sequence'], 'hash': tx['hash']}
                    if node['diffType'] != 'DeletedNode':
                        # no need partially funded must remains offers
                        effect['remaining'] = not is_amount_zero(parse_amount(node['fields']['TakerGets']))
                    else:
                        effect['cancelled'] = True

                    effect['gets'] = parse_amount(fieldSet['TakerGets'])
                    effect['pays'] = parse_amount(fieldSet['TakerPays'])
                    effect['got'] = amount_subtract(parse_amount(node['fieldsPrev']['TakerPays']),
                                                    parse_amount(node['fields']['TakerPays']))
                    effect['paid'] = amount_subtract(parse_amount(node['fieldsPrev']['TakerGets']),
                                                     parse_amount(node['fields']['TakerGets']))
                    if sell:
                        effect['type'] = 'sold'
                    else:
                        effect['type'] = 'bought'
                    # effect['type'] = 'sold' if sell else effect['type'] = 'bought'
                else:
                    # offer_funded, offer_created or offer_cancelled offer effect
                    if node['fieldsPrev']['TakerPays']:
                        node['fieldsPrev']['TakerPays'] = 'offer_funded'
                    else:
                        node['fieldsPrev']['TakerPays'] = 'offer_cancelled'

                    if node['diffType'] == 'CreatedNode':
                        effect['effect'] = 'offer_created'
                    else:
                        effect['effect'] = node['fieldsPrev']['TakerPays']

                    if effect['effect'] == 'offer_funded':
                        fieldSet = node['fieldsPrev']
                        effect['counterparty'] = {'account': tx['Account'], 'seq': tx['Sequence'], 'hash': tx['hash']}
                        effect['got'] = amount_subtract(parse_amount(node['fieldsPrev']['TakerPays']),
                                                        parse_amount(node['fields']['TakerPays']))
                        effect['paid'] = amount_subtract(parse_amount(node['fieldsPrev']['TakerGets']),
                                                         parse_amount(node['fields']['TakerGets']))
                        if sell:
                            effect['type'] = sell = 'sold'
                        else:
                            effect['type'] = sell = 'bought'

                    # 3. offer_created
                    if effect['effect'] == 'offer_created':
                        effect['gets'] = parse_amount(fieldSet['TakerGets'])
                        effect['pays'] = parse_amount(fieldSet['TakerPays'])
                        if sell:
                            effect['type'] = sell = 'sell'
                        else:
                            effect['type'] = sell = 'buy'

                    # 4. offer_cancelled
                    if effect['effect'] == 'offer_cancelled':
                        effect['hash'] = node['fields']['PreviousTxnID']
                        # collect data for cancel transaction type
                        if result['type'] == 'offercancel':
                            result['gets'] = parse_amount(fieldSet['TakerGets'])
                            result['pays'] = parse_amount(fieldSet['TakerPays'])
                        effect['gets'] = parse_amount(fieldSet['TakerGets'])
                        effect['pays'] = parse_amount(fieldSet['TakerPays'])
                        if sell:
                            effect['type'] = 'sell'
                        else:
                            effect['type'] = 'buy'
                effect['seq'] = node['fields']['Sequence']

            # 5. offer_bought
            elif tx['Account'] == account and node['fieldsPrev']:
                effect['effect'] = 'offer_bought'
                effect['counterparty'] = {
                    'account': node['fields']['Account'],
                    'seq': node['fields']['Sequence'],
                    'hash': node['PreviousTxnID'] or node['fields']['PreviousTxnID']
                }
                effect['paid'] = amount_subtract(parse_amount(node['fieldsPrev']['TakerPays']),
                                                 parse_amount(node['fields']['TakerPays']))
                effect['got'] = amount_subtract(parse_amount(node['fieldsPrev']['TakerGets']),
                                                parse_amount(node['fields']['TakerGets']))
                if sell:
                    effect.type = 'bought'
                else:
                    effect.type = 'sold'

            # add price
            if (effect['gets'] and effect['pays']) or (effect['got'] and effect['paid']):
                created = effect['effect'] == 'offer_created' and effect['type'] == 'buy'
                funded = effect['effect'] == 'offer_funded' and effect['type'] == 'bought'
                cancelled = effect['effect'] == 'offer_cancelled' and effect['type'] == 'buy'
                bought = effect['effect'] == 'offer_bought' and effect['type'] == 'bought'
                partially_funded = effect['effect'] == 'offer_partially_funded' and effect['type'] == 'bought'
                effect['price'] = get_price(effect, (created or funded or cancelled or bought or partially_funded))

        if result['type'] == 'offereffect' and node['entryType'] == 'AccountRoot':
            if node['fields']['RegularKey'] == account:
                effect['effect'] = 'set_regular_key'
                effect['type'] = 'null'
                effect['account'] = node['fields']['Account']
                effect['regularkey'] = account

        # add effect
        if effect:
            if node['diffType'] == 'DeletedNode' and effect['effect'] != 'offer_bought':
                effect['deleted'] = True
            result['effects'].append(effect)

    # check cross gateway when parse more effect, specially trust related effects, now ignore it
    return result
