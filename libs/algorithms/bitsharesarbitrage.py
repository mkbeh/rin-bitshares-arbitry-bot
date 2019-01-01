# -*- coding: utf-8 -*-
# TODO наблюдения: цены в ордерах кошелька шар округляются в большую сторону ровно до 8 знаков
# TODO 1. определиться: стоит ли округлять до 8 знаков цену или же считать как есть (склоняюсь ко 2му варианту)
import re
import array
import asyncio

from bitshares.market import Market
from libs import utils

from pprint import pprint
from datetime import datetime


class BitsharesArbitrage:
    def __init__(self, loop):
        self._ioloop = loop
        self.num_pattern = re.compile(r'(\d+([,.]?\d+)*)')
        self.file = '/home/cyberpunk/PycharmProjects/rin-bitshares-arbitry-bot/output/chains-30-12-2018-12-06-26.lst'

    async def get_cleared_orders_data(self, raw_data):
        for data in re.findall(self.num_pattern, str(raw_data)):
            yield float(data[0])

    async def _algorithm_testing(self, chain):
        arr = array.array('d')

        for pair in chain:
            raw_orders_data = Market(pair).orderbook(1)['asks']

            async for order_data in self.get_cleared_orders_data(raw_orders_data):
                arr.append(order_data)

        pprint(arr)

    @staticmethod
    def _split_chain_on_pairs(seq):
        for el in seq:
            yield el.split(' ')

    @staticmethod
    def _clear_each_str_in_seq(seq):
        for el in seq:
            yield el.replace('\n', '').strip()

    @staticmethod
    def _read_file(file):
        with open(file, 'r') as f:
            for line in f:
                yield line

    def _get_chains(self):
        return list(
            self._split_chain_on_pairs(
                self._clear_each_str_in_seq(
                    self._read_file(self.file)
                )
            )
        )

    def start_arbitrage(self):
        chains = self._get_chains()
        tasks = [self._ioloop.create_task(self._algorithm_testing(chain)) for chain in chains[:1]]
        self._ioloop.run_until_complete(asyncio.gather(*tasks))
