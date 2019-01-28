# -*- coding: utf-8 -*-
import json
import asyncio
import websockets


default_node = 'wss://bitshares.openledger.info/ws'


class GramBitshares:
    def __init__(self, node=default_node):
        self._node = node
        self._ws = None

    async def connect(self):
        try:
            self._ws = await websockets.connect(self._node)
        except ConnectionRefusedError:
            await self.reconnect()

    async def alternative_connect(self, ws_node=default_node):
        gram = GramBitshares(ws_node)
        await gram.connect()
        self._ws = gram._ws

        return gram

    async def reconnect(self):
        await asyncio.sleep(30)
        await self.alternative_connect()

    async def close(self):
        await self._ws.close()

    async def call_method(self, method, *args):
        message = json.dumps({'id': 0, 'method': '{}'.format(method), 'params': [*args]})
        await self._ws.send(message)

        return await self._ws.recv()

