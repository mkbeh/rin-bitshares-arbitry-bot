# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares
from .asset import Asset


class Market(GramBitshares):
    def __init__(self, gram_instance):
        super().__init__()
        self.gram = gram_instance

    async def _get_base_quote_assets_id(self, base, quote):
        base_asset = base
        quote_asset = quote

        if not base.startswith('1.3.') or not quote.startswith('1.3.'):
            base_asset = await Asset(self.gram).convert_name_to_id(base)
            quote_asset = await Asset(self.gram).convert_name_to_id(quote)

        return base_asset, quote_asset

    async def get_order_book(self, base, quote, order_type, limit=1):
        base_asset, quote_asset = await self._get_base_quote_assets_id(base, quote)
        raw_data = await self.gram.call_method('get_order_book', base_asset, quote_asset, limit)

        try:
            return json.loads(raw_data)['result'][order_type]
        except Exception as err:
            raise Exception(f'Fail while getting result for pair {base_asset}:{quote_asset}.', err)

    async def buy(self):
        pass

    async def sell(self):
        pass

    async def cancel(self):
        pass


