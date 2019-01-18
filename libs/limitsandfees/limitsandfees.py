# -*- coding: utf-8 -*-
import logging
import json
import asyncio
import itertools

from decimal import Decimal, ROUND_HALF_UP

from libs.baserin import BaseRin
from libs.assetschainsmaker.chainscreator import ChainsCreator
from libs.aiopybitshares.asset import Asset
from const import VOLS_LIMITS, WORK_DIR, WALLET_URI
from libs import utils


class VolLimits(BaseRin):
    _logger = logging.getLogger('VolLimits')
    _lock = asyncio.Lock()
    _url = 'http://185.208.208.184:5000/get_ticker?base={}&quote={}'
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'vol_limits'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'vol_limits-{_date}.lst')
    _vol_limits = None

    def __init__(self, loop):
        self._ioloop = loop

    async def _get_asset_price(self, base_asset, quote_asset, logger):
        response = await self.get_data(self._url.format(base_asset, quote_asset),
                                       logger=logger, delay=1, json=True)

        try:
            return response['latest']
        except KeyError:
            logger.warning(response['detail'])

    async def _get_limits(self):
        assets = VOLS_LIMITS.keys()

        prices = await asyncio.gather(
            *[self._get_asset_price(asset, 'USD', self._logger) for asset in assets if asset != 'USD']
        )

        limits = {}

        for i, (key, val) in enumerate(VOLS_LIMITS.items()):
            if key == 'USD':
                limits[key] = val
                break

            limits[key] = float(Decimal(val) * Decimal(prices[i]).
                                quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))

        self._vol_limits = '{}:{} {}:{} {}:{} {}:{}'\
            .format(*itertools.chain(*limits.items()))

        await self.write_data(json.dumps(limits), self._new_file, self._lock)

    def run(self):
        tasks = [self._ioloop.create_task(self._get_limits())]

        try:
            self._ioloop.run_until_complete(asyncio.gather(*tasks))
        except Exception as err:
            self.actions_when_error(err, self._logger, self._old_file)
        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got prices and calculate limits: {self._vol_limits}')

            return self._new_file


class DefaultBTSFee(VolLimits):
    _logger = logging.getLogger('DefaultBTSFee')
    _lock = asyncio.Lock()
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'btsdefaultfee'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'btsdefaultfee-{_date}.lst')
    _order_create_fee = 0.00116 * 3
    _fees = None

    def __init__(self, ioloop):
        self._ioloop = ioloop
        super().__init__(self._ioloop)

    async def _get_converted_order_fee(self):
        assets = VOLS_LIMITS.keys()

        prices = await asyncio.gather(
            *[self._get_asset_price(asset, 'BTS', self._logger) for asset in assets if asset != 'BTS']
        )

        prices.insert(0, self._order_create_fee)
        final_fees = {}

        for asset, price in zip(assets, prices):
            if asset == 'BTS':
                final_fees[asset] = price
                continue

            final_fees[asset] = float((Decimal(self._order_create_fee) * Decimal(price)).
                                      quantize(Decimal('0.00000000'), rounding=ROUND_HALF_UP))

        self._fees = '{}:{} {}:{} {}:{} {}:{}' \
            .format(*itertools.chain(*final_fees.items()))

        await self.write_data(json.dumps(final_fees), self._new_file, self._lock)

    def run(self):
        tasks = [self._ioloop.create_task(self._get_converted_order_fee())]

        try:
            self._ioloop.run_until_complete(asyncio.gather(*tasks))
        except Exception as err:
            self.actions_when_error(err, self._logger, self._old_file)
        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got prices and calculate fees: {self._fees}')

            return self._new_file


class GatewayPairFee(BaseRin):
    _url = 'https://wallet.bitshares.org/#/market/{}_{}'
    _logger = logging.getLogger('GatewayPairFee')
    _lock = asyncio.Lock()
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'chains_with_fees'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'chains_with_fees-{_date}.lst')

    def __init__(self, loop):
        self._ioloop = loop
        self._file_with_chains = ChainsCreator(self._ioloop)
        self._fees_count = 0
        self._chains_num = None

    async def foo(self, chain):
        assets_objs = [Asset() for _ in range(len(chain))]
        [await asset_obj.alternative_connect(WALLET_URI) for asset_obj in assets_objs]

        raw_chain_fees = await asyncio.gather(
            *[obj.get_asset_info(pair.split(':')[1]) for obj, pair in zip(assets_objs, chain)]
        )

        fees = [str(Decimal(fee['options']['market_fee_percent']) / Decimal(100))
                for fee in raw_chain_fees]

        data = '{} {} {} {} {} {}'.format(*itertools.chain(chain, fees))
        await self.write_data(data, self._new_file, self._lock)
        self._fees_count += 3

        [await asset_obj.close() for asset_obj in assets_objs]

    def get_chains_fees(self):
        chains = self._get_chains(self._file_with_chains)
        self._chains_num = len(chains)
        tasks = [self._ioloop.create_task(self.foo(chain)) for chain in chains]

        try:
            self._ioloop.run_until_complete(asyncio.gather(*tasks))
        except Exception as err:
            self.actions_when_error(err, self._logger, self._old_file)
        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got {self._fees_count} fees for {self._chains_num} chains.')

            return self._new_file
