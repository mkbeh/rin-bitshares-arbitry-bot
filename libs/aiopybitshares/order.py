# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares


class Order(GramBitshares):
    __slots__ = ['seller', 'amount', 'sell_asset', 'min_to_receive', 'receive_asset',
                 'timeout', 'fillkill', 'broadcast']

    def __init__(self, gram_instance, seller, amount, sell_asset, min_to_receive, receive_asset,
                 timeout=0, fillkill=True, broadcast=False):
        super().__init__()
        self.gram = gram_instance

        self.seller = seller
        self.amount = amount
        self.sell_asset = sell_asset
        self.min_to_receive = min_to_receive
        self.receive_asset = receive_asset
        self.timeout = timeout
        self.fillkill = fillkill
        self.broadcast = broadcast

    async def buy(self):
        raw_data = await self.gram.call_method('sell_asset', self.seller, self.min_to_receive, self.receive_asset,
                                               self.amount, self.sell_asset, self.timeout,
                                               self.fillkill, self.broadcast)
        try:
            return json.loads(raw_data)['result']
        except Exception as err:
            raise Exception(f'Order for pair {self.receive_asset}:{self.sell_asset} failed with error.', err)

    async def sell(self):
        raw_data = await self.gram.call_method('sell_asset', self.seller, self.amount, self.sell_asset,
                                               self.min_to_receive, self.receive_asset, self.timeout,
                                               self.fillkill, self.broadcast)
        try:
            return json.loads(raw_data)['result']
        except Exception as err:
            raise Exception(f'Order for pair {self.sell_asset}:{self.receive_asset} failed with error.', err)
