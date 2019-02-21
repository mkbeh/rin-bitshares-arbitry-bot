# -*- coding: utf-8 -*-
import logging
import json
import asyncio
import itertools
import array

import numpy as np

from decimal import Decimal, ROUND_HALF_UP
from collections import namedtuple

from aiohttp.client_exceptions import ClientConnectionError

from .chainscreator import ChainsCreator
from src.extra.baserin import BaseRin
from src.extra import utils

from src.aiopybitshares.asset import Asset
from src.aiopybitshares.blockchain import Blockchain


class VolLimits(BaseRin):
    _lock = asyncio.Lock()
    _logger = logging.getLogger('Rin.VolLimits')
    _url = 'http://185.208.208.184:5000/get_ticker?base={}&quote={}'
    _old_file = utils.get_file(BaseRin.output_dir, utils.get_dir_file(BaseRin.output_dir, 'vol_limits'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(BaseRin.output_dir, f'vol_limits-{_date}.lst')
    _vol_limits_pattern = None

    def __init__(self, loop):
        self._ioloop = loop

    async def _calculate_limits(self, prices):
        limits = {}

        for i, (key, val) in enumerate(self.volume_limits.items()):
            if key == '1.3.121':
                limits[key] = val
                break

            limits[key] = float(Decimal(val) * Decimal(prices[i]).
                                quantize(Decimal('0.00000000'), rounding=ROUND_HALF_UP))

        return limits

    async def _get_asset_price(self, base_asset, quote_asset):
        response = await self.get_data(self._url.format(base_asset, quote_asset),
                                       logger=None, delay=1, json=True)

        try:
            return response['latest']
        except KeyError:
            self._logger.warning(response['detail'])

    async def _get_limits(self):
        assets = self.volume_limits.keys()
        prices = await asyncio.gather(
            *[self._get_asset_price(asset, '1.3.121') for asset in assets if asset != '1.3.121']
        )

        vol_limits = await self._calculate_limits(prices)
        self._vol_limits_pattern = '{}:{} {}:{} {}:{} {}:{}'\
            .format(*itertools.chain(*vol_limits.items()))
        await self.write_data(json.dumps(vol_limits), self._new_file, self._lock)

        return vol_limits

    def get_volume_limits(self):
        tasks = [self._ioloop.create_task(self._get_limits())]

        try:
            vol_limits = self._ioloop.run_until_complete(asyncio.gather(*tasks))[0]
        except ClientConnectionError:
            self._logger.exception('Client connection error occurred while getting volume limits.')
            return json.loads(
                self.actions_when_errors_with_read_data(self._old_file)[0]
            )

        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got prices and calculate limits: {self._vol_limits_pattern}')

            return vol_limits


class DefaultBTSFee(VolLimits):
    _logger = logging.getLogger('Rin.DefaultBTSFee')
    _lock = asyncio.Lock()
    _old_file = utils.get_file(VolLimits.output_dir, utils.get_dir_file(VolLimits.output_dir, 'btsdefaultfee'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(VolLimits.output_dir, f'btsdefaultfee-{_date}.lst')
    _lifetime_member_percent = 0.2
    _fees = None

    def __init__(self, ioloop):
        self._ioloop = ioloop
        super().__init__(self._ioloop)

    async def _get_converted_order_fee(self):
        assets = VolLimits.volume_limits.keys()
        prices = await asyncio.gather(
            *[self._get_asset_price(asset, '1.3.0') for asset in assets if asset != '1.3.0']
        )

        blockchain_obj = await Blockchain().connect(ws_node=VolLimits.wallet_uri)
        order_create_fee = \
            await blockchain_obj.get_global_properties(create_order_fee=True) * self._lifetime_member_percent * 3
        await blockchain_obj.close()

        prices.insert(0, order_create_fee)
        final_fees = {}

        for asset, price in zip(assets, prices):
            if asset == '1.3.0':
                final_fees[asset] = price
                continue

            final_fees[asset] = float((Decimal(order_create_fee) * Decimal(price)).
                                      quantize(Decimal('0.00000000'), rounding=ROUND_HALF_UP))

        self._fees = '{}:{} {}:{} {}:{} {}:{}' \
            .format(*itertools.chain(*final_fees.items()))
        await self.write_data(json.dumps(final_fees), self._new_file, self._lock)

        return final_fees

    def get_converted_default_bts_fee(self):
        tasks = [self._ioloop.create_task(self._get_converted_order_fee())]

        try:
            converted_fees = self._ioloop.run_until_complete(asyncio.gather(*tasks))[0]
        except ClientConnectionError:
            self._logger.exception('Client connection error occurred while getting converted default bts fee')
            return json.loads(
                self.actions_when_errors_with_read_data(self._old_file)[0]
            )

        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got prices and calculate fees: {self._fees}')

            return converted_fees


class ChainsWithGatewayPairFees(BaseRin):
    _url = 'https://wallet.bitshares.org/#/market/{}_{}'
    _logger = logging.getLogger('Rin.ChainsWithGatewayPairFees')
    _lock = asyncio.Lock()
    _old_file = utils.get_file(BaseRin.output_dir, utils.get_dir_file(BaseRin.output_dir, 'chains_with_fees'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(BaseRin.output_dir, f'chains_with_fees-{_date}.lst')

    def __init__(self, loop):
        self._ioloop = loop
        # self._file_with_chains = ChainsCreator(self._ioloop).start_creating_chains()
        self._file_with_chains = '/home/cyberpunk/PycharmProjects/rin-bitshares-arbitry-bot/' \
                                 'output/chains-18-02-2019-21-46-32.lst'
        self._fees_count = 0

    async def _get_fees_for_chain(self, chain):
        assets_objs = [Asset() for _ in range(len(chain))]
        [await asset_obj.connect(self.wallet_uri) for asset_obj in assets_objs]

        raw_chain_fees = await asyncio.gather(
            *(obj.get_asset_info(pair.split(':')[1]) for obj, pair in zip(assets_objs, chain))
        )
        [await asset_obj.close() for asset_obj in assets_objs]

        arr = np.array([
            *(float(fee['options']['market_fee_percent']) / float(100)
              for fee in raw_chain_fees)
        ], dtype=self.dtype_float64)

        return arr

    async def _get_chain_fees(self, chain):
        fees = await self._get_fees_for_chain(chain)

        data = '{} {} {} {} {} {}'.format(*itertools.chain(chain, fees))
        await self.write_data(data, self._new_file, self._lock)
        self._fees_count += 3

        ChainAndFees = namedtuple('ChainAndFees', ['chain', 'fees'])

        return ChainAndFees(tuple(chain), fees)

    def _final_data_preparation(self, data):
        ChainAndFees = namedtuple('ChainAndFees', ['chain', 'fees'])

        for el in data:
            arr = np.array([*itertools.islice(el, 3, None)], dtype=self.dtype_float64)

            yield ChainAndFees(tuple(itertools.islice(el, 0, 3)), arr)

    def get_chains_with_fees(self):
        chains = self.get_transformed_data(self._file_with_chains)
        chains_num = len(chains)
        tasks = [self._ioloop.create_task(self._get_chain_fees(chain)) for chain in chains]

        try:
            chains_and_fees = self._ioloop.run_until_complete(asyncio.gather(*tasks))
        except ClientConnectionError:
            self._logger.error('Client connection error occurred while getting chain fees.')

            return self._final_data_preparation(
                        self.get_transformed_data(self._old_file, generator=True)
                    )

        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got {self._fees_count} fees for {chains_num} chains.')

            return chains_and_fees
