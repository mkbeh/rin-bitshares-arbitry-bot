# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares, default_node


class Asset(GramBitshares):
    def __init__(self):
        super().__init__()
        self._gram = None

    async def alternative_connect(self, ws_node=default_node):
        self._gram = await super().alternative_connect(ws_node)

    async def convert_name_to_id(self, asset_name, limit=1):
        raw_data = await self._gram.call_method('list_assets', asset_name.upper(), limit)

        try:
            return json.loads(raw_data)['result'][0]['id']
        except IndexError:
            raise Exception(f'Got error while getting {asset_name} id.')

    async def get_asset(self, asset_name_or_id):
        raw_data = await self._gram.call_method('get_asset', asset_name_or_id)

        return raw_data
