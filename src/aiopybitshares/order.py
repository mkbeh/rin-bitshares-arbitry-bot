# -*- coding: utf-8 -*-
from .grambitshares import GramBitshares, default_node
from src.extra.customexceptions import OrderNotFilled, AuthorizedAsset, UnknownOrderException


class Order(GramBitshares):
    error_msgs = {
        'unspecified: Assert Exception: !op.fill_or_kill || filled: ': OrderNotFilled,
        'unspecified: Assert Exception: is_authorized_asset': AuthorizedAsset,
    }

    def __init__(self):
        super().__init__()
        self._gram = None

    async def connect(self, ws_node=default_node):
        self._gram = await super().connect(ws_node)

        return self

    async def _find_and_raise_specific_exception(self, received_err_msg):
        for err_msg, exception in self.error_msgs.items():
            if received_err_msg.startswith(err_msg):
                raise exception

    async def create_order(self, *args):
        raw_data = await self._gram.call_method('sell_asset', *args)
        print(raw_data)
        try:
            raw_data['result']

        except KeyError:
            await self._find_and_raise_specific_exception(raw_data['error']['message'])

        except UnknownOrderException:
            raise
