# coding=utf-8
"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/8
 * Time: 14:57
 * Description:
"""
import sys
sys.path.append("..")

import re

from jingtum_python_baselib.wallet import Wallet
from src.config import Config



def is_number(s):
    """
    判断字符串是否是数字类型
    :param s:
    :return:
    """
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False



LEDGER_STATES = ['current', 'closed', 'validated']

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

class utils:
    # input num may contain one '.' and one '-'
    def is_num(amount):
        return str(amount).replace('.', '', 1).replace('-', '', 1).isdigit()

    def is_valid_currency(currency):
        CURRENCY_RE = '^([a-zA-Z0-9]{3,6}|[A-F0-9]{40})$'
        if (not currency or not isinstance(currency, str) or currency == ''):
            return False
        if re.search(CURRENCY_RE, currency):  # 判断字符串是否符合某一正则表达式
            return True
        else:
            return False

    """
     * check {value: '', currency:'', issuer: ''}
     * @param amount
     * @returns {boolean}
    """
    def is_valid_amount(amount):
        if (not amount):
            return False
        # check amount value
        if ((not amount.__contains__('value') and amount['value'] != 0) or not utils.is_num(amount['value'])):
            return False
        # check amount currency
        if (not amount.__contains__('currency') or not utils.is_valid_currency(amount['currency'])):
            return False
        # native currency issuer is empty
        if (amount['currency'] == Config.currency and amount['issuer'] != ''):
            return False
        # non native currency issuer is not allowed to be empty
        if (amount['currency'] != Config.currency
                and not Wallet.is_valid_address(amount['issuer'])):
            return False
        return True

    """
     * check {currency: '', issuer: ''}
     * @param amount
     * @returns {boolean}
    """
    def is_valid_amount0(amount):
        if (not amount):
            return False
        # check amount currency
        if (not amount.__contains__('currency') or not utils.is_valid_currency(amount['currency'])):
            return False
        # native currency issuer is empty
        if (amount['currency'] == Config.currency and amount['issuer']  != ''):
            return False
        # non native currency issuer is not allowed to be empty
        if (amount['currency'] != Config.currency
                and not Wallet.is_valid_address(amount['issuer'])):
            return False
        return True


