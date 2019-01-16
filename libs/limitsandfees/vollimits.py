# -*- coding: utf-8 -*-
import asyncio
import logging
import itertools
import json

from decimal import Decimal, getcontext, ROUND_HALF_UP

from libs.baserin import BaseRin
from libs import utils
from const import VOLS_LIMITS, WORK_DIR


class VolLimits(BaseRin):
    _logger = logging.getLogger('ChainsCreator')
    _lock = asyncio.Lock()
    _url = 'http://185.208.208.184:5000/get_ticker?base={}&quote=USD'
    _context = getcontext()
    _context.prec = 8
    _context.rounding = ROUND_HALF_UP
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'vollimits'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'vollimits-{_date}.lst')
    _parsed_data = None

    def __init__(self, loop):
        self._ioloop = loop

    async def _get_asset_price(self, asset):
        response = await self.get_data(self._url.format(asset), logger=self._logger, delay=1, json=True)

        try:
            return response['latest']
        except KeyError:
            self._logger.warning(response['detail'])

    async def _get_limits(self):
        assets = VOLS_LIMITS.keys()

        prices = await asyncio.gather(
            *[self._get_asset_price(asset) for asset in assets if asset != 'USD']
        )

        limits = {}

        for i, (key, val) in enumerate(VOLS_LIMITS.items()):
            if key == 'USD':
                limits[key] = val
                break

            limits[key] = float(Decimal(val) * Decimal(prices[i]))

        self._parsed_data = '{}:{} {}:{} {}:{} {}:{}'\
            .format(*itertools.chain(*limits.items()))

        await self._write_data(json.dumps(limits), self._new_file, self._lock)

    def run(self):
        tasks = [self._ioloop.create_task(self._get_limits())]

        try:
            self._ioloop.run_until_complete(asyncio.gather(*tasks))
        except Exception as err:
            self._actions_when_error(err, self._logger, self._old_file)
        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got prices and calculate limits: {self._parsed_data}')

            return self._new_file
