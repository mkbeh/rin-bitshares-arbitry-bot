# -*- coding: utf-8 -*-
import json
import asyncio
import websockets


class PyGram:
    _default_node = 'wss://bitshares.openledger.info/ws'

    def __init__(self, node=_default_node):
        self._node = node
        self.ws = self._get_websocket()

    def _get_websocket(self):
        return asyncio.get_event_loop().run_until_complete(websockets.connect(self._node))

    async def _connect(self, call_method, *args):
        message = json.dumps({'id': 1, 'method': '{}'.format(call_method), 'params': [*args]})
        await self.ws.send(message)

        return await self.ws.recv()

    async def _get_base_quote_assets_id(self, base, quote):
        base_asset = base
        quote_asset = quote

        if not base.startswith('1.3.') or not quote.startswith('1.3.'):
            base_asset = await self.convert_name_to_id(base)
            quote_asset = await self.convert_name_to_id(quote)

        return base_asset, quote_asset

    async def get_order_book(self, base, quote, order_type, limit=1):
        base_asset, quote_asset = await self._get_base_quote_assets_id(base, quote)
        raw_data = await self._connect('get_order_book', base_asset, quote_asset, limit)

        try:
            return json.loads(raw_data)['result'][order_type]
        except Exception as err:
            raise Exception(f'Fail while getting result for pair {base}:{quote}.', err)

    async def convert_name_to_id(self, asset_name, limit=1):
        raw_data = await self._connect('list_assets', asset_name.upper(), limit)

        try:
            return json.loads(raw_data)['result'][0]['id']
        except IndexError:
            raise Exception(f'Got error while getting {asset_name} id.')

    def __del__(self):
        self.ws.close()
