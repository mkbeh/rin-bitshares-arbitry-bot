# -*- coding: utf-8 -*-
import re
import array
import asyncio

from decimal import Decimal

from libs.aiopybitshares.market import Market
from libs import utils

from pprint import pprint
from datetime import datetime


# start = datetime.now()
# end = datetime.now()
# delta = end - start
# print(delta.microseconds / 1000000)


class BitsharesArbitrage:
    def __init__(self, loop):
        self._ioloop = loop
        self._lock = asyncio.Lock()
        # self.num_pattern = re.compile(r'(\d+([,.]?\d+)*)')
        self.file = '/home/cyberpunk/PycharmProjects/rin-bitshares-arbitry-bot/output/chains-05-01-2019-15-35-09.lst'

    # @staticmethod
    # async def _check_on_profit(arr):
    #     if arr[0] < arr[7]:
    #         print('profit', arr[7], arr[0])
    #
    # async def _compare_second_vol_limit_with_order_base_vol(self, vol_limit, arr):
    #     new_arr = array.array('d')
    #
    #     if vol_limit >= arr[3]:
    #         arr[6] = Decimal(vol_limit) / Decimal(arr[8])
    #
    #     elif vol_limit < arr[3]:
    #         arr[3] = vol_limit
    #         arr[4] = Decimal(arr[3]) * Decimal(arr[5])
    #         vol_limit1 = await self._calc_vol_limit(arr[3], arr[2])
    #         new_arr = await self._compare_first_vol_limit_with_order_base_vol(vol_limit=vol_limit1, arr=arr)
    #         new_arr[7] = Decimal(new_arr[6]) * Decimal(new_arr[8])
    #
    #     return new_arr
    #
    # @staticmethod
    # async def _compare_first_vol_limit_with_order_base_vol(vol_limit, arr):
    #     if vol_limit >= arr[0]:
    #         arr[3] = Decimal(vol_limit) / Decimal(arr[5])
    #
    #     elif vol_limit < arr[0]:
    #         arr[0] = vol_limit
    #         arr[1] = Decimal(arr[0]) * Decimal(arr[2])
    #
    #     return arr
    #
    # @staticmethod
    # async def _calc_vol_limit(dividend, divider):
    #     return Decimal(dividend) / Decimal(divider)

    @staticmethod
    async def split_pair_raw_on_assets(pair):
        return pair.split(':')

    async def _get_orders_data_for_chain(self, chain, gram_market):
        arr = array.array('d')

        async def get_order_data_for_pair(pair, market_gram):
            base_asset, quote_asset = await self.split_pair_raw_on_assets(pair)
            raw_order_data = (await market_gram.get_order_book(base_asset, quote_asset, 'bids'))[0]
            order_data = (float(data) for data in raw_order_data.values())

            return order_data

        pairs_orders_data = await asyncio.gather(
            *[get_order_data_for_pair(pair, market) for pair, market in zip(chain, gram_market)]
        )

        [arr.extend(pairs_orders_data[i]) for i in range(len(chain))]

        return arr

    async def _algorithm_testing(self, chain):
        # x1=0 | y1=1 | z1=2 | x2=3 | y2=4 | z2=5 | x3=6 | y3=7 | z3=8
        markets = [Market() for _ in range(len(chain))]
        [await market.alternative_connect() for market in markets]
        arr = await self._get_orders_data_for_chain(chain, markets)

        [await market.close() for market in markets]

        # vol_limit1 = await self._calc_vol_limit(arr[3], arr[2])
        # vol_limit2 = await self._calc_vol_limit(arr[6], arr[5])
        # new_arr = await self._compare_first_vol_limit_with_order_base_vol(vol_limit=vol_limit1, arr=arr)
        # final_arr = await self._compare_second_vol_limit_with_order_base_vol(vol_limit=vol_limit2, arr=new_arr)
        #
        # await self._check_on_profit(final_arr)

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
