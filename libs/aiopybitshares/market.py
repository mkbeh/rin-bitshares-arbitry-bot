# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares, default_node


class Market(GramBitshares):
    def __init__(self, gram_instance=None):
        super().__init__()
        self._gram = gram_instance

    async def alternative_connect(self, ws_node=default_node):
        self._gram = await super().alternative_connect(ws_node)

    async def get_order_book(self, base, quote, order_type, limit=1):
        raw_data = await self._gram.call_method('get_order_book', base.upper(), quote.upper(), limit)

        try:
            return json.loads(raw_data)['result'][order_type]
        except Exception as err:
            raise Exception(f'Fail while getting result for pair {base}:{quote}.', err)
