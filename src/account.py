"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/30
 * Time: 23:02
 * Description: account stub for subscribe accounts transaction event
   can be used for many accounts
 * @param remote
 * @constructor
"""
from eventemitter import EventEmitter
from src import utils


class Account:

    def __init__(self, remote):
        self.remote = remote
        self.emitter = EventEmitter()
        self.accounts = {}

        self.emitter.on('newListener', self.new_listener)
        self.emitter.on('removeListener', self.remove_listener)
        self.emitter.on('transaction', self.info_affected_account)

    def new_listener(self, account, listener):
        if account == 'removeListener':
            return
        if not utils.is_valid_address(account):
            # 此处有疑问，待大家一起讨论
            #
            #
            # self.account = raise Exception('invalid account')
            raise Exception('invalid account')
        self.accounts[account] = listener

    def remove_listener(self, account):
        if not utils.is_valid_address(account):
            raise Exception('invalid account')

        del self.accounts[account]

    def info_affected_account(self, data):
        # dispatch
        accounts = utils.affected_accounts(data)
        for account in accounts:
            callback = self.accounts[account]
            tx = utils.process_tx(data, account)
            if callback:
                callback(tx)
