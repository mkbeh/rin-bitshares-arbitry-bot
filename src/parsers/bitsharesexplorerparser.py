# -*- coding: utf-8 -*-
import logging
import asyncio

from collections import namedtuple

from src.extra.baserin import BaseRin
from .btspriceparser import BTSPriceParser
from src.extra import utils


class BitsharesExplorerParser(BaseRin):
    _logger = logging.getLogger('Rin.BitsharesExplorerParser')
    _lock = asyncio.Lock()
    _date = utils.get_today_date()
    _old_file = utils.get_file(BaseRin.output_dir, utils.get_dir_file(BaseRin.output_dir, 'pairs'))
    _new_file = utils.get_file(BaseRin.output_dir, f'pairs-{_date}.lst')
    _pairs_count = 0

    def __init__(self, loop):
        self._ioloop = loop
        self._bts_price_in_usd = BTSPriceParser(loop).get_bts_price_in_usd()
        self._overall_min_daily_vol = self.overall_min_daily_volume / self._bts_price_in_usd

        self._assets_url = self.explorer_uri + '/assets'
        self._assets_markets_url = self.explorer_uri + '/get_markets?asset_id={}'
        self._market_data_url = self.explorer_uri + '/get_volume?base={}&quote={}'

    async def _check_pair_on_valid(self, pair, base_price):
        market_data = await self.get_data(self._market_data_url.format(*pair),
                                          delay=5, logger=self._logger, json=True)

        if float(market_data['base_volume']) * float(base_price) > self.pair_min_daily_volume:
            await self.write_data('{}:{}'.format(*pair), self._new_file, self._lock)
            self._pairs_count += 1

    async def _get_valid_pairs(self, asset_info):
        asset_markets_data = await self.get_data(self._assets_markets_url.format(asset_info.id),
                                                 delay=5, logger=self._logger, json=True)
        pairs = list(map(lambda x: x[1].strip().split('/'), asset_markets_data))
        [await self._check_pair_on_valid(pair, asset_info.price) for pair in pairs]

    async def _get_valid_assets(self):
        assets_data = await self.get_data(self._assets_url, delay=2, logger=self._logger, json=True)
        AssetInfo = namedtuple('AssetsInfo', ['id', 'price'])
        assets = [
            AssetInfo(asset[2], asset[3])
            for asset in assets_data
            if float(asset[4]) > self._overall_min_daily_vol
        ]
        self._logger.info(f'Parsed: {len(assets)} assets.')

        return assets

    def start_parsing(self):
        try:
            task = self._ioloop.create_task(self._get_valid_assets())
            assets_info = (self._ioloop.run_until_complete(asyncio.gather(task)))[0]

            tasks = (self._ioloop.create_task(self._get_valid_pairs(asset_info)) for asset_info in assets_info)
            self._ioloop.run_until_complete(asyncio.gather(*tasks))

            utils.remove_file(self._old_file)
            self._logger.info(f'Parsed: {self._pairs_count} pairs.')
            FileData = namedtuple('FileData', ['file', 'new_version'])

            return FileData(self._new_file, True)

        except TypeError:
            self._logger.exception('JSON data retrieval error.')
            return self.actions_when_error(self._old_file)

        except Exception as err:
            self._logger.exception('Exception occurred while parsing.', err)
            return self.actions_when_error(self._old_file)
