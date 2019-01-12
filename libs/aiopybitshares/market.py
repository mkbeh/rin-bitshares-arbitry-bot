# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares, default_node
from .asset import Asset


class Market(GramBitshares):
    def __init__(self, gram_instance=None):
        super().__init__()
        self._gram = gram_instance

    async def alternative_connect(self, ws_node=default_node):
        self._gram = await super().alternative_connect(ws_node)

    async def _get_base_quote_assets_id(self, **kwargs):
        base_asset, quote_asset = kwargs.values()

        if not base_asset.startswith('1.3.') or not quote_asset.startswith('1.3.'):
            base_asset, quote_asset = [await Asset(self._gram).convert_name_to_id(asset)
                                       for asset in kwargs.values()
                                       if not asset.startswith('1.3.')]

        return base_asset, quote_asset

    async def get_order_book(self, base, quote, order_type, limit=1):
        base_asset, quote_asset = await self._get_base_quote_assets_id(base=base, quote=quote)
        raw_data = await self._gram.call_method('get_order_book', base_asset, quote_asset, limit)

        try:
            return json.loads(raw_data)['result'][order_type]
        except Exception as err:
            raise Exception(f'Fail while getting result for pair {base_asset}:{quote_asset}.', err)
