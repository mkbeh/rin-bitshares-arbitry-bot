# -*- coding: utf-8 -*-
import os
import time
import logging
import itertools
import asyncio

import numpy as np

from datetime import datetime as dt

from aiohttp.client_exceptions import ClientConnectionError

from src.extra.baserin import BaseRin
from src.extra.customexceptions import OrderNotFilled, AuthorizedAsset, EmptyOrdersList, UnknownOrderError
from src.extra import utils

from src.aiopybitshares.market import Market
from src.aiopybitshares.order import Order
from src.aiopybitshares.asset import Asset

from src.const import WORK_DIR, DATA_UPDATE_TIME, MIN_PROFIT_LIMITS, ACCOUNT_NAME, WALLET_URI, LOG_DIR, \
    TIME_TO_RECONNECT

from .limitsandfees import ChainsWithGatewayPairFees, VolLimits, DefaultBTSFee
from src.algorithms.arbitryalgorithm import ArbitrationAlgorithm


class BitsharesArbitrage(BaseRin):
    _logger = logging.getLogger('Rin.BitsharesArbitrage')
    _vol_limits = None
    _bts_default_fee = None
    _assets_blacklist_file = utils.get_file(WORK_DIR, f'blacklist.lst')
    _is_orders_placing = False

    _client_conn_err_msg = 'Getting client connection error while arbitrage testing.'

    def __init__(self, loop):
        self._ioloop = loop
        self._profit_logger = self.setup_logger('Profit', os.path.join(LOG_DIR, 'profit.log'))

    async def _order_err_action(self, chain, count, asset_blacklist=True):
        if asset_blacklist:
            await self.write_data(chain[count][1], self._assets_blacklist_file)

    async def _orders_setter(self, orders_placement_data, chain, orders_objs):
        filled_all = True

        for i, (vols_arr, order_obj) in enumerate(zip(orders_placement_data, orders_objs)):
            splitted_pair = chain[i].split(':')

            try:
                await order_obj.create_order(
                    f'{ACCOUNT_NAME}', f'{vols_arr[0]}', f'{splitted_pair[0]}',
                    f'{vols_arr[1]}', f'{splitted_pair[1]}', 0, True, True
                )

            except OrderNotFilled:
                filled_all = False
                self._logger.warning(f'Order for pair {chain[i]} in chain '
                                     f'{chain} with volumes {vols_arr} not filled.')
                break

            except AuthorizedAsset:
                await self._order_err_action(chain, i)
                self._logger.warning(f'Got Authorized asset {chain[i][1]} '
                                     f'in chain {chain} while placing order.')
                raise

            except UnknownOrderError:
                raise

        if filled_all:
            self._logger.info(f'All orders for {chain} with volumes '
                              f'- {orders_placement_data} successfully filed.')

    async def volumes_checker(self, orders_vols, chain, orders_objs, profit):
        if orders_vols.size:
            # await self._orders_setter(order_placement_data, chain, orders_objs)
            self._profit_logger.info(f'Profit = {profit} | Chain: {chain} | '
                                     f'Volumes: {orders_vols[0][0], orders_vols[2][1]}')

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
            raise EmptyOrdersList

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
    async def _get_precisions_arr(chain):
        obj = await Asset().connect(ws_node=WALLET_URI)
        assets_arr = np.array([
            *(itertools.chain.from_iterable(
                map(lambda x: x.split(':'), chain)
            ))
        ], dtype=str)
        precisions_arr = np.array(range(4), dtype=int)

        for i, asset in enumerate(assets_arr[:4]):
            if i == 2:
                precisions_arr[i] = (precisions_arr[i - 1])
                continue

            precisions_arr[i] = (
                (await obj.get_asset_info(asset))['precision']
            )
        await obj.close()

        return np.append(precisions_arr, (precisions_arr[3], precisions_arr[0]))

    @staticmethod
    async def _get_fee_or_limit(data_dict, pair):
        return data_dict.get(
            pair.split(':')[0]
        )

    async def _arbitrage_testing(self, chain, assets_fees):
        # print(chain)
        # print(assets_fees)
        # print('\n')

        markets_objs = [await Market().connect() for _ in range(len(chain))]
        orders_objs = [await Order().connect(ws_node=WALLET_URI) for _ in range(len(chain))]

        time_start = dt.now()
        time_delta = 0

        asset_vol_limit = await self._get_fee_or_limit(self._vol_limits, chain[0])
        bts_default_fee = await self._get_fee_or_limit(self._bts_default_fee, chain[0])
        min_profit_limit = await self._get_fee_or_limit(MIN_PROFIT_LIMITS, chain[0])
        precisions_arr = await self._get_precisions_arr(chain)

        while time_delta < DATA_UPDATE_TIME:
            try:
                orders_arrs = await self._get_orders_data_for_chain(chain, markets_objs)
                orders_vols, profit = await ArbitrationAlgorithm(orders_arrs, asset_vol_limit, bts_default_fee,
                                                                 assets_fees, min_profit_limit, precisions_arr)()

                if self._is_orders_placing is False:
                    self._is_orders_placing = True
                    # await self.volumes_checker(orders_vols, chain, orders_objs, profit)
                    self._is_orders_placing = False

            except (EmptyOrdersList, AuthorizedAsset, UnknownOrderError):
                [await market.close() for market in markets_objs]
                [await order_obj.close() for order_obj in orders_objs]
                return

            time_end = dt.now()
            time_delta = (time_end - time_start).seconds / 3600

            break

        [await market.close() for market in markets_objs]
        [await order_obj.close() for order_obj in orders_objs]

    def start_arbitrage(self):
        cycle_counter = 0

        while True:
            chains = ChainsWithGatewayPairFees(self._ioloop).get_chains_with_fees()
            self._vol_limits = VolLimits(self._ioloop).get_volume_limits()
            self._bts_default_fee = DefaultBTSFee(self._ioloop).get_converted_default_bts_fee()

            # -- checking speed
            start = dt.now()
            tasks = (self._ioloop.create_task(self._arbitrage_testing(chain.chain, chain.fees)) for chain in chains)

            try:
                self._ioloop.run_until_complete(asyncio.gather(*tasks))
            except ClientConnectionError:
                self._logger.exception(self._client_conn_err_msg)
                time.sleep(TIME_TO_RECONNECT)
            else:
                self._logger.info(f'Success arbitrage cycle #{cycle_counter}.\n')
                cycle_counter += 1

            end = dt.now()
            delta = end - start
            print('CHAINS + ALGO', delta.microseconds / 1_000_000, ' ms')
            # --\

            break
