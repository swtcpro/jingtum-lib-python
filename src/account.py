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
from src import util


class Account:

    def __init__(self, remote):
        self.remote = remote
        self.emitter = EventEmitter()
        self.accounts = {}
        self.account = {}

        self.emitter.on('newListener', self.new_listener)
        self.emitter.on('removeListener', self.remove_listener)
        self.emitter.on('transaction', self.info_affected_account)

    def new_listener(self, account, listener):
        if account == 'removeListener':
            return
        if not util.is_valid_address(account):
            self.account = Exception('invalid account')
        self.accounts[account] = listener

    def remove_listener(self, account):
        if not util.is_valid_address(account):
            raise Exception('invalid account')

        del self.accounts[account]

    def info_affected_account(self, data):
        # dispatch
        accounts = util.affected_accounts(data)
        for account in accounts:
            callback = self.accounts[account]
            tx = util.process_tx(data, account)
            if callback:
                callback(tx)
