# -*- coding: utf-8 -*-
import json
import aiohttp

from aiohttp.client_exceptions import ClientConnectionError

from src.const import WALLET_PWD


default_node = 'wss://bitshares.openledger.info/ws'


class GramBitshares:
    def __init__(self, node=default_node):
        self._node = node
        self._ws = None
        self._session = None

    async def ws_connect(self, node=default_node):
        session = aiohttp.ClientSession()

        try:
            self._ws = await session.ws_connect(node)
        except ClientConnectionError:
            await session.close()
            raise
        else:
            return session

    async def connect(self, ws_node=default_node):
        gram = GramBitshares(ws_node)
        self._session = await gram.ws_connect(ws_node)
        self._ws = gram._ws

        if ws_node != default_node and await self.is_wallet_locked():
            await self.unlock_wallet()

        return gram

    async def call_method(self, method, *args):
        message = json.dumps({'id': 0, 'method': '{}'.format(method), 'params': [*args]})
        await self._ws.send_str(message)

        return await self._ws.receive_json()

    async def is_wallet_locked(self):
        return (await self.call_method('is_locked'))['result']

    async def unlock_wallet(self):
        await self.call_method('unlock', WALLET_PWD)

    async def close(self):
        await self._session.close()
