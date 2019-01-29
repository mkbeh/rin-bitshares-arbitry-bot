# -*- coding: utf-8 -*-
import array
import asyncio

from datetime import datetime as dt
from decimal import Decimal

from src.additional.baserin import BaseRin
from src.core.limitsandfees import ChainsWithGatewayPairFees, VolLimits, DefaultBTSFee
from src.aiopybitshares.market import Market
from src.const import DATA_UPDATE_TIME


# start = datetime.now()
# end = datetime.now()
# delta = end - start
# print(delta.microseconds / 1000000)


class BitsharesArbitrage(BaseRin):
    _vol_limits = None
    _bts_default_fee = None

    def __init__(self, loop):
        self._ioloop = loop
        self.chains_count = 0

    @staticmethod
    async def split_pair_raw_on_assets(pair):
        return pair.split(':')

    @staticmethod
    async def run_chain_data_thorough_algo(arr, fees, vol_limit, bts_default_fee, chain):
        price0, quote0, base0, price1, quote1, base1, price2, quote2, base2 = arr
        fee0, fee1, fee2 = fees
        volume_limit, order_fee = vol_limit, bts_default_fee

        if base0 > volume_limit:
            base0 = volume_limit
            quote0 = Decimal(base0) / Decimal(price0)

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

        new_quote0 = Decimal(quote0) - Decimal(quote0) * Decimal(fee0) / Decimal(100)
        base1 = new_quote0
        quote1 = Decimal(base1) / Decimal(price1)
        new_quote1 = Decimal(quote1) - Decimal(base1) / Decimal(price1) * Decimal(fee1) / Decimal(100)
        base2 = new_quote1
        quote2 = Decimal(base2) / Decimal(price2)
        new_quote2 = Decimal(quote2) - Decimal(base2) / Decimal(price2) * Decimal(fee2) / Decimal(100)

        if base0 < (Decimal(new_quote2) - Decimal(order_fee)):
            print(chain)
            print(base0, (Decimal(new_quote2) - Decimal(order_fee)))

            profit = Decimal(new_quote2) - Decimal(base0)
            print(f'Profit = {profit}! Set orders!\n')

    @staticmethod
    async def _get_orders_data_for_chain(chain, gram_markets):
        arr = array.array('d')

        async def get_order_data_for_pair(pair, market_gram):
            base_asset, quote_asset = pair.split(':')

            try:
                raw_order_data = (await market_gram.get_order_book(base_asset, quote_asset, 'asks'))[0]
            except IndexError:
                return

            order_data = (float(data) for data in raw_order_data.values())

            return order_data

        pairs_orders_data = await asyncio.gather(
            *(get_order_data_for_pair(pair, market) for pair, market in zip(chain, gram_markets))
        )

        try:
            [arr.extend(pairs_orders_data[i]) for i in range(len(chain))]
        except TypeError:
            return

        return arr

    @staticmethod
    async def _get_fee_or_limit(data_dict, pair):
        return data_dict.get(
            pair.split(':')[0]
        )

    async def _algorithm_testing(self, chain, assets_fees):
        markets = [Market() for _ in range(len(chain))]
        [await market.alternative_connect() for market in markets]

        time_start = dt.now()
        time_delta = 0

        asset_vol_limit = await self._get_fee_or_limit(self._vol_limits, chain[0])
        bts_default_fee = await self._get_fee_or_limit(self._bts_default_fee, chain[0])

        while time_delta < DATA_UPDATE_TIME:
            arr = await self._get_orders_data_for_chain(chain, markets)

            if not arr:
                break

            await self.run_chain_data_thorough_algo(arr, assets_fees, asset_vol_limit, bts_default_fee, chain)

            time_end = dt.now()
            time_delta = (time_end - time_start).seconds / 3600

            break

        [await market.close() for market in markets]

    def start_arbitrage(self):
        while True:
            chains = ChainsWithGatewayPairFees(self._ioloop).get_chains_with_fees()
            self._vol_limits = VolLimits(self._ioloop).get_volume_limits()
            self._bts_default_fee = DefaultBTSFee(self._ioloop).get_converted_default_bts_fee()

            tasks = (self._ioloop.create_task(self._algorithm_testing(chain.chain, chain.fees)) for chain in chains)
            self._ioloop.run_until_complete(asyncio.gather(*tasks))

            break