# -*- coding: utf-8 -*-
import asyncio
import logging
import itertools
import json

from decimal import Decimal, ROUND_HALF_UP

from libs.baserin import BaseRin
from libs import utils
from const import VOLS_LIMITS, WORK_DIR


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
            self._actions_when_error(err, self._logger, self._old_file)
        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got prices and calculate limits: {self._vol_limits}')

            return self._new_file
