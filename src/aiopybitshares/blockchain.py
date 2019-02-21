# -*- coding: utf-8 -*-
from .grambitshares import GramBitshares, default_node


class Blockchain(GramBitshares):
    __slots__ = ['_gram']

    def __init__(self):
        super().__init__()
        self._gram = None

    async def connect(self, ws_node=default_node):
        self._gram = await super().connect(ws_node)

        return self

    async def get_global_properties(self, create_order_fee=False):
        raw_data = await self._gram.call_method('get_global_properties')

        try:
            if create_order_fee:
                return float(raw_data['result']['parameters']['current_fees']['parameters'][1][1]['fee']) / 100000

            return raw_data['result']
        except KeyError:
            raise Exception(f'Got error while getting bitshares global properties.')
