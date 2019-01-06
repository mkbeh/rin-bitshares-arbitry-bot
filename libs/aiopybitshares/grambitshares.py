# -*- coding: utf-8 -*-
import json
import websockets


class GramBitshares:
    _default_node = 'wss://bitshares.openledger.info/ws'

    def __init__(self, node=_default_node):
        self._node = node
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self._node)

    async def close(self):
        await self.ws.close()

    async def call_method(self, method, *args):
        message = json.dumps({'id': 0, 'method': '{}'.format(method), 'params': [*args]})
        await self.ws.send(message)

        return await self.ws.recv()
