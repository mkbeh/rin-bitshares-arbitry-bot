# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares


class Asset(GramBitshares):
    def __init__(self, gram_instance):
        super().__init__()
        self.gram = gram_instance

    async def convert_name_to_id(self, asset_name, limit=1):
        raw_data = await self.gram.call_method('list_assets', asset_name.upper(), limit)

        try:
            return json.loads(raw_data)['result'][0]['id']
        except IndexError:
            raise Exception(f'Got error while getting {asset_name} id.')
