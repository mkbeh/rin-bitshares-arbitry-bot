# -*- coding: utf-8 -*-
import os
import re
import time
import logging
import itertools
import asyncio

import numpy as np

from datetime import datetime as dt

from aiohttp.client_exceptions import ClientConnectionError

from src.extra.customexceptions import OrderNotFilled, AuthorizedAsset, EmptyOrdersList, UnknownOrderException
from src.extra import utils

from src.aiopybitshares.market import Market
from src.aiopybitshares.order import Order
from src.aiopybitshares.asset import Asset

from src.extra.baserin import BaseRin

from .limitsandfees import ChainsWithGatewayPairFees, VolLimits, DefaultBTSFee
from src.algorithms.arbitryalgorithm import ArbitrationAlgorithm


class BitsharesArbitrage(BaseRin):
    _logger = logging.getLogger('Rin.BitsharesArbitrage')
    _vol_limits = None
    _bts_default_fee = None
    _blacklisted_assets_file = utils.get_file(BaseRin.output_dir, f'blacklist.lst')
    _is_orders_placing = False

    _client_conn_err_msg = 'Getting client connection error while arbitrage testing.'

    def __init__(self, loop):
        self._ioloop = loop
        self._profit_logger = self.setup_logger('Profit', os.path.join(self.log_dir, 'profit.log'))
        self._blacklisted_assets = self.get_blacklisted_assets()

    async def _add_asset_to_blacklist(self, asset):
        if asset not in self._blacklisted_assets:
            self._blacklisted_assets.append(asset)
            await self.write_data(asset, self._blacklisted_assets_file)

    async def _orders_setter(self, orders_placement_data, chain, orders_objs):
        def convert_scientific_notation_to_decimal(val):
            pattern = re.compile(r'e-')
            splitted_val = re.split(pattern, str(val))

            if len(splitted_val) == 2:
                return '{:.12f}'.format(val).rstrip('0')

            return str(val)

        filled_all = True

        for i, (vols_arr, order_obj) in enumerate(zip(orders_placement_data, orders_objs)):
            splitted_pair = chain[i].split(':')
            converted_vols_arr = tuple(
                map(
                    convert_scientific_notation_to_decimal, vols_arr
                )
            )

            try:
                await order_obj.create_order(
                    f'{self.account_name}', f'{converted_vols_arr[0]}', f'{splitted_pair[0]}',
                    f'{converted_vols_arr[1]}', f'{splitted_pair[1]}', 0, True, True
                )

            except OrderNotFilled:
                filled_all = False
                self._logger.warning(f'Order for pair {chain[i]} in chain '
                                     f'{chain} with volumes {vols_arr} not filled.')
                break

            except AuthorizedAsset:
                await self._add_asset_to_blacklist(splitted_pair[1])
                self._logger.warning(f'Got Authorized asset {chain[i][1]} '
                                     f'in chain {chain} while placing order.')
                raise

            except UnknownOrderException:
                raise

        if filled_all:
            self._profit_logger.info(f'All orders for {chain} with volumes '
                                     f'- {orders_placement_data} successfully filed.')

    async def volumes_checker(self, orders_vols, chain, orders_objs, profit):
        if orders_vols.size:
            await self._orders_setter(orders_vols, chain, orders_objs)
            self._profit_logger.info(f'Profit = {profit} | Chain: {chain} | '
                                     f'Volumes: {orders_vols[0][0], orders_vols[2][1]}')

    async def get_order_data_for_pair(self, pair, market_gram, order_type='asks', limit=BaseRin.orders_depth):
        base_asset, quote_asset = pair.split(':')
        raw_orders_data = await market_gram.get_order_book(base_asset, quote_asset, order_type, limit=limit)
        arr = np.array([
            *map(
                lambda order_data: tuple(float(value) for value in order_data.values()), raw_orders_data
            )
        ], dtype=self.dtype_float64)

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
            ], dtype=self.dtype_float64)

            return arr

        try:
            pairs_orders_data_arr = np.array(pairs_orders_data_arrs, dtype=self.dtype_float64)
        except ValueError:
            len_of_smallest_arr = await get_size_of_smallest_arr(pairs_orders_data_arrs)
            pairs_orders_data_arr = await cut_off_extra_arrs_els(pairs_orders_data_arrs, len_of_smallest_arr)

        return pairs_orders_data_arr

    async def _get_precisions_arr(self, chain):
        obj = await Asset().connect(ws_node=self.wallet_uri)
        assets_arr = itertools.chain.from_iterable(
                map(lambda x: x.split(':'), chain)
            )
        precisions_arr = np.array(range(4), dtype=self.dtype_int64)

        for i, asset in enumerate(itertools.islice(assets_arr, 4)):
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

    async def _get_specific_data(self, chain):
        return (
            await self._get_fee_or_limit(self._vol_limits, chain[0]),
            await self._get_fee_or_limit(self._bts_default_fee, chain[0]),
            await self._get_fee_or_limit(self.min_profit_limits, chain[0]),
            await self._get_precisions_arr(chain)
        )

    async def _arbitrage_testing(self, chain, assets_fees):
        markets_objs = [await Market().connect() for _ in range(len(chain))]
        orders_objs = [await Order().connect(ws_node=self.wallet_uri) for _ in range(len(chain))]

        asset_vol_limit, bts_default_fee, min_profit_limit, precisions_arr = await self._get_specific_data(chain)

        time_start = dt.now()
        time_delta = 0

        async def close_connections():
            [await market.close() for market in markets_objs]
            [await order_obj.close() for order_obj in orders_objs]

        while time_delta < self.data_update_time:
            try:
                orders_arrs = await self._get_orders_data_for_chain(chain, markets_objs)
                orders_vols, profit = await ArbitrationAlgorithm(orders_arrs, asset_vol_limit, bts_default_fee,
                                                                 assets_fees, min_profit_limit, precisions_arr)()

                if self._is_orders_placing is False:
                    self._is_orders_placing = True
                    await self.volumes_checker(orders_vols, chain, orders_objs, profit)
                    self._is_orders_placing = False

            except (EmptyOrdersList, AuthorizedAsset, UnknownOrderException):
                await close_connections()
                return

            time_end = dt.now()
            time_delta = (time_end - time_start).seconds / 3600

        await close_connections()

    def start_arbitrage(self):
        cycle_counter = 0

        while True:
            chains = ChainsWithGatewayPairFees(self._ioloop).get_chains_with_fees()
            self._vol_limits = VolLimits(self._ioloop).get_volume_limits()
            self._bts_default_fee = DefaultBTSFee(self._ioloop).get_converted_default_bts_fee()
            tasks = (self._ioloop.create_task(self._arbitrage_testing(chain.chain, chain.fees)) for chain in chains)

            try:
                self._ioloop.run_until_complete(asyncio.gather(*tasks))
            except ClientConnectionError:
                self._logger.exception(self._client_conn_err_msg)
                time.sleep(self.time_to_reconnect)
            else:
                self._logger.info(f'Success arbitrage cycle #{cycle_counter}.\n')
                cycle_counter += 1
