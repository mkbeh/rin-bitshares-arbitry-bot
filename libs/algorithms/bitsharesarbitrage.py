# -*- coding: utf-8 -*-
import array
import asyncio

from decimal import Decimal, localcontext, ROUND_HALF_UP

from libs.baserin import BaseRin
from libs.limitsandfees.limitsandfees import GatewayPairFee, VolLimits, DefaultBTSFee
from libs.aiopybitshares.market import Market
from libs import utils

from pprint import pprint
from datetime import datetime


# start = datetime.now()
# end = datetime.now()
# delta = end - start
# print(delta.microseconds / 1000000)


class BitsharesArbitrage(BaseRin):
    def __init__(self, loop):
        self._ioloop = loop
        self._file_with_chains = '/home/cyberpunk/PycharmProjects/rin-bitshares-arbitry-bot/' \
                                 'output/chains-05-01-2019-15-35-09.lst'

    @staticmethod
    async def split_pair_raw_on_assets(pair):
        return pair.split(':')

    @staticmethod
    async def run_chain_data_thorough_algo(arr):
        price0, quote0, base0, price1, quote1, base1, price2, quote2, base2 = arr

        with localcontext() as ctx:
            ctx.prec = 12
            ctx.rounding = ROUND_HALF_UP

            if quote0 > base1:
                quote0 = base1
                base0 = Decimal(quote0) * Decimal(price0)

            elif quote0 < base1:
                base1 = quote0
                quote1 = Decimal(base1) / Decimal(price1)

            if quote1 > base2:
                quote1 = base2
                base1 = Decimal(quote1) * Decimal(price1)
                quote0 = base1
                base0 = Decimal(quote0) * Decimal(price0)

            elif quote1 < base2:
                base2 = quote1
                quote2 = Decimal(base2) / Decimal(price2)

            if base0 < quote2:
                print(base0, quote2)

                profit = Decimal(quote2) - Decimal(base0)
                print(f'Profit = {profit}! Set orders!\n')

    @staticmethod
    async def _get_orders_data_for_chain(chain, gram_markets):
        arr = array.array('d')

        async def get_order_data_for_pair(pair, market_gram):
            base_asset, quote_asset = pair.split(':')
            raw_order_data = (await market_gram.get_order_book(base_asset, quote_asset, 'bids'))[0]
            order_data = (float(data) for data in raw_order_data.values())

            return order_data

        pairs_orders_data = await asyncio.gather(
            *[get_order_data_for_pair(pair, market) for pair, market in zip(chain, gram_markets)]
        )

        [arr.extend(pairs_orders_data[i]) for i in range(len(chain))]

        return arr

    async def _algorithm_testing(self, chain):
        markets = [Market() for _ in range(len(chain))]
        [await market.alternative_connect() for market in markets]
        arr = await self._get_orders_data_for_chain(chain, markets)
        await self.run_chain_data_thorough_algo(arr)

        [await market.close() for market in markets]

    def start_arbitrage(self):
        chains = self._get_chains(self._file_with_chains)
        tasks = [self._ioloop.create_task(self._algorithm_testing(chain)) for chain in chains]
        self._ioloop.run_until_complete(asyncio.gather(*tasks))
