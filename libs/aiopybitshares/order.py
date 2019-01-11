# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares, default_node


class Order(GramBitshares):
    __slots__ = ['seller', 'amount', 'sell_asset', 'min_to_receive', 'receive_asset',
                 'order_type', 'timeout', 'fillkill', 'broadcast']

    def __init__(self, gram_instance, seller, amount, sell_asset, min_to_receive, receive_asset,
                 order_type, timeout=0, fillkill=True, broadcast=False):
        super().__init__()
        self._gram = gram_instance

        self.seller = seller
        self.amount = amount
        self.sell_asset = sell_asset
        self.min_to_receive = min_to_receive
        self.receive_asset = receive_asset
        self.order_type = order_type
        self.timeout = timeout
        self.fillkill = fillkill
        self.broadcast = broadcast

    async def alternative_connect(self, ws_node=default_node):
        self._gram = await super().alternative_connect()

    async def create(self):
        if self.order_type == 'buy':
            self.sell_asset, self.receive_asset, self.amount, self.min_to_receive = \
                self.receive_asset, self.sell_asset, self.min_to_receive, self.amount

        attrs_vals = [self.__getattribute__(attr) for attr in self.__slots__ if attr != 'order_type']
        raw_data = await self._gram.call_method('sell_asset', *attrs_vals)

        try:
            return json.loads(raw_data)['result']
        except Exception as err:
            raise Exception(f'Order for pair {self.sell_asset}:{self.receive_asset} failed with error.', err)
