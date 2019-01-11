# -*- coding: utf-8 -*-
import json
import websockets


default_node = 'wss://bitshares.openledger.info/ws'


class GramBitshares:
    def __init__(self, node=default_node):
        self._node = node
        self._ws = None

    async def alternative_connect(self, ws_node=default_node):
        gram = GramBitshares()
        await gram.connect()

        return gram

    async def connect(self):
        self._ws = await websockets.connect(self._node)

    async def close(self):
        await self._ws.close()

    async def call_method(self, method, *args):
        message = json.dumps({'id': 0, 'method': '{}'.format(method), 'params': [*args]})
        await self._ws.send(message)

        return await self._ws.recv()
