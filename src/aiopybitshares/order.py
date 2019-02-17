# -*- coding: utf-8 -*-
from .grambitshares import GramBitshares, default_node
from src.extra.customexceptions import OrderNotFilled, AuthorizedAsset, UnknownOrderException


class Order(GramBitshares):
    error_msgs = {
        'unspecified: Assert Exception: !op.fill_or_kill || filled: ': OrderNotFilled,
        'unspecified: Assert Exception: is_authorized_asset( d, *_seller, *_sell_asset ): ': AuthorizedAsset,
    }

    def __init__(self):
        super().__init__()
        self._gram = None

    async def connect(self, ws_node=default_node):
        self._gram = await super().connect(ws_node)

        return self

    async def create_order(self, *args):
        raw_data = await self._gram.call_method('sell_asset', *args)

        try:
            raw_data['result']

        except KeyError:
            raise self.error_msgs.get(raw_data['error']['message'], KeyError)()

        except UnknownOrderException:
            raise
