# -*- coding: utf-8 -*-
import json
import asyncio
import aiohttp


default_node = 'wss://bitshares.openledger.info/ws'


class GramBitshares:
    def __init__(self, node=default_node):
        self._node = node
        self._ws = None
        self._session = None

    async def connect(self, node=default_node):
        session = aiohttp.ClientSession()

        try:
            self._ws = await session.ws_connect(node)
        except AssertionError:
            await asyncio.sleep(10)
            self._ws = await session.ws_connect(node)

        return session

    async def alternative_connect(self, ws_node=default_node):
        gram = GramBitshares(ws_node)
        self._session = await gram.connect(ws_node)
        self._ws = gram._ws

        return gram

    async def call_method(self, method, *args):
        message = json.dumps({'id': 0, 'method': '{}'.format(method), 'params': [*args]})
        print(message)
        await self._ws.send_str(message)

        return await self._ws.receive_json()

    async def close(self):
        await self._session.close()
