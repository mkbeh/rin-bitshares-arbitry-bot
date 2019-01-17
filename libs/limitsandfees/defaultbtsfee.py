# -*- coding: utf-8 -*-
import logging
import json
import asyncio
import itertools

from decimal import Decimal, ROUND_HALF_UP

from libs.limitsandfees.vollimits import VolLimits
from const import VOLS_LIMITS, WORK_DIR
from libs import utils


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

        await self._write_data(json.dumps(final_fees), self._new_file, self._lock)

    def run(self):
        tasks = [self._ioloop.create_task(self._get_converted_order_fee())]

        try:
            self._ioloop.run_until_complete(asyncio.gather(*tasks))
        except Exception as err:
            self._actions_when_error(err, self._logger, self._old_file)
        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got prices and calculate fees: {self._fees}')

            return self._new_file

