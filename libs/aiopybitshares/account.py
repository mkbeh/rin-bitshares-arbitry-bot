# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares, default_node


class Account(GramBitshares):
    def __init__(self, gram_instance):
        super().__init__()
        self._gram = gram_instance

    async def alternative_connect(self, ws_node=default_node):
        self._gram = await super().alternative_connect()

    def create_account(self):
        pass
