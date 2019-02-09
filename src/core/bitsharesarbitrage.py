# -*- coding: utf-8 -*-
import asyncio

import numpy as np

from datetime import datetime as dt

from src.extra.baserin import BaseRin
from src.extra.customexceptions import OrderNotFilled, AuthorizedAsset, MaxRetriesOrderFilledExceeded
from src.extra import utils

from src.aiopybitshares.market import Market
from src.aiopybitshares.order import Order

from src.const import WORK_DIR, DATA_UPDATE_TIME, MIN_PROFIT_LIMITS, ACCOUNT_NAME, WALLET_URI

from .limitsandfees import ChainsWithGatewayPairFees, VolLimits, DefaultBTSFee
from src.algorithms.arbitryalgorithm import ArbitrationAlgorithm
from src.algorithms.recalculatevols import RecalculateVols


# FOR TESTING ----


# start = dt.now()
# end = dt.now()
# delta = end - start
# print(delta.microseconds)


class BitsharesArbitrage(BaseRin):
    _vol_limits = None
    _bts_default_fee = None
    _assets_blacklist_file = utils.get_file(WORK_DIR, f'assets_blacklist.lst')

    def __init__(self, loop):
        self._ioloop = loop

        # FOR TESTING ----
        # print('COMPILED', cython.compiled)

    async def _sell_assets(self, pair, base_asset_vol):
        order_obj = await Order().connect(ws_node=WALLET_URI)
        order_filled = False
        max_retries = 3

        while not order_filled:
            if max_retries == 0:
                raise MaxRetriesOrderFilledExceeded

            market_obj = await Market().connect()
            orders_arr = await self.get_order_data_for_pair(pair, market_obj, order_type='asks')
            vols_arr = await RecalculateVols(orders_arr, base_asset_vol)()

            try:
                order_obj.create_order(
                    f'{ACCOUNT_NAME}', f'{vols_arr[0]}', f'{pair[0]}',
                    f'{vols_arr[1]}', f'{pair[1]}', 0, True, True
                )
                order_filled = True
                print('Filled ok')

            except OrderNotFilled:
                pass

            finally:
                max_retries -= 1

    async def _actions_when_err_order_not_filled(self, chain, i, order_placement_data):
        pair = chain[i].split()
        base_asset_vol = order_placement_data[i][0]

        try:
            await self._sell_assets(pair, base_asset_vol)

            return True
        except MaxRetriesOrderFilledExceeded:
            return False

    async def _order_err_action(self, chain, count, order_placement_data, asset_blacklist=True):
        if asset_blacklist:
            await self.write_data(chain[count], self._assets_blacklist_file)

        if count > 0:
            for i in range(count - 1, -1, -1):
                pair = chain[i].split()[::-1]
                base_asset_vol = order_placement_data[i][1]

                try:
                    await self._sell_assets(pair, base_asset_vol)
                except MaxRetriesOrderFilledExceeded:
                    print('in _order_err_action MaxRetriesOrderFilledExceeded')
                    break

    async def _orders_setter(self, order_placement_data, chain, orders_objs):
        print('profit chain: ', chain, order_placement_data)

        for i, (vols_arr, order_obj) in enumerate(zip(order_placement_data, orders_objs)):
            splitted_pair = chain[i].split(':')

            try:
                await order_obj.create_order(
                    f'{ACCOUNT_NAME}', f'{vols_arr[0]}', f'{splitted_pair[0]}',
                    f'{vols_arr[1]}', f'{splitted_pair[1]}', 0, True, True
                )
            except OrderNotFilled:
                is_filled = await self._actions_when_err_order_not_filled(chain, i, order_placement_data)

                if is_filled:
                    continue

                else:
                    await self._order_err_action(chain, i, order_placement_data)
                    break

            except AuthorizedAsset:
                print('AuthorizedAsset')
                await self._order_err_action(chain, i, order_placement_data)
                raise

            except Exception as err:
                print(err)
                pass

    async def volumes_checker(self, order_placement_data, chain, orders_objs):
        if order_placement_data.size:
            await self._orders_setter(order_placement_data, chain, orders_objs)

    @staticmethod
    async def get_order_data_for_pair(pair, market_gram, order_type='asks', limit=5):
        base_asset, quote_asset = pair.split(':')
        raw_orders_data = await market_gram.get_order_book(base_asset, quote_asset, order_type, limit=limit)
        order_data_lst = map(
            lambda order_data: [float(value) for value in order_data.values()], raw_orders_data
        )
        arr = np.array([*order_data_lst], dtype=float)

        try:
            arr[0]
        except IndexError:
            raise

        return arr

    async def _get_orders_data_for_chain(self, chain, gram_markets):
        pairs_orders_data_arrs = await asyncio.gather(
            *(self.get_order_data_for_pair(pair, market) for pair, market in zip(chain, gram_markets))
        )

        async def get_size_of_smallest_arr(arrs_lst):
            return min(map(lambda x: len(x), arrs_lst))

        async def cut_off_extra_arrs_els(arrs_lst, required_nums_of_items):
            arr = np.array([
                *map(lambda x: x[:required_nums_of_items], arrs_lst)
            ], dtype=float)

            return arr

        try:
            pairs_orders_data_arr = np.array(pairs_orders_data_arrs, dtype=float)
        except ValueError:
            len_of_smallest_arr = await get_size_of_smallest_arr(pairs_orders_data_arrs)
            pairs_orders_data_arr = await cut_off_extra_arrs_els(pairs_orders_data_arrs, len_of_smallest_arr)

        return pairs_orders_data_arr

    @staticmethod
    async def _get_fee_or_limit(data_dict, pair):
        return data_dict.get(
            pair.split(':')[0]
        )

    async def _arbitrage_testing(self, chain, assets_fees):
        markets_objs = [await Market().connect() for _ in range(len(chain))]
        orders_objs = [await Order().connect(ws_node=WALLET_URI) for _ in range(len(chain))]

        time_start = dt.now()
        time_delta = 0

        asset_vol_limit = await self._get_fee_or_limit(self._vol_limits, chain[0])
        bts_default_fee = await self._get_fee_or_limit(self._bts_default_fee, chain[0])
        min_profit_limit = await self._get_fee_or_limit(MIN_PROFIT_LIMITS, chain[0])

        while time_delta < DATA_UPDATE_TIME:
            try:
                orders_arrs = await self._get_orders_data_for_chain(chain, markets_objs)
            except (IndexError, AuthorizedAsset):
                break

            order_placement_data = await ArbitrationAlgorithm(orders_arrs, asset_vol_limit, bts_default_fee,
                                                              assets_fees, min_profit_limit)()
            await self.volumes_checker(order_placement_data, chain, orders_objs)

            time_end = dt.now()
            time_delta = (time_end - time_start).seconds / 3600

            break

        [await market.close() for market in markets_objs]
        [await order_obj.close() for order_obj in orders_objs]

    def start_arbitrage(self):
        while True:
            chains = ChainsWithGatewayPairFees(self._ioloop).get_chains_with_fees()
            self._vol_limits = VolLimits(self._ioloop).get_volume_limits()
            self._bts_default_fee = DefaultBTSFee(self._ioloop).get_converted_default_bts_fee()

            # -- checking speed
            start = dt.now()

            tasks = (self._ioloop.create_task(self._arbitrage_testing(chain.chain, chain.fees)) for chain in chains)
            self._ioloop.run_until_complete(asyncio.gather(*tasks))

            end = dt.now()
            delta = end - start
            print('CHAINS + ALGO', delta.microseconds / 1_000_000, ' ms')
            # --\

            break
