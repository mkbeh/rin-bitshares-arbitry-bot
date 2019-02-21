# -*- coding: utf-8 -*-
from .grambitshares import GramBitshares, default_node


class Account(GramBitshares):
    def __init__(self):
        super().__init__()
        self._gram = None

    async def connect(self, ws_node=default_node):
        self._gram = await super().connect(ws_node)

        return self

    async def get_account_balances(self, account_id, *args):
        """
        :param account_id: ID of the account to get balances for
        :param args: IDs of the assets to get balances of; if empty, get all assets account has a balance in
        :return:
        """
        raw_data = await self._gram.call_method('get_account_balances', account_id, args)

        try:
            return raw_data['result']
        except KeyError:
            pass
