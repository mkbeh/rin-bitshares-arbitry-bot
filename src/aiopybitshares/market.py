# -*- coding: utf-8 -*-
from .grambitshares import GramBitshares, default_node


class Market(GramBitshares):
    def __init__(self):
        super().__init__()
        self._gram = None

    async def connect(self, ws_node=default_node):
        self._gram = await super().connect(ws_node)

        return self

    async def get_order_book(self, base, quote, order_type, limit=1):
        data = await self._gram.call_method('get_order_book', base.upper(), quote.upper(), limit)

        try:
            return data['result'][order_type]
        except Exception as err:
            raise Exception(f'Fail while getting result for pair {base}:{quote}.', err)
