# -*- coding: utf-8 -*-
# TODO написать метод для получения актуального курса шар , для того чтобы осеивать по долларовому эквиваленту.
import os
import re
import random
import logging
import aiohttp
import asyncio

import aiofiles

from libs import utils
from const import OVERALL_MIN_DAILY_VOLUME, PAIR_MIN_DAILY_VOLUME, WORK_DIR, LOG_DIR

from pprint import pprint


class BitsharesExplorerParser:
    utils.dir_exists(WORK_DIR)
    utils.dir_exists(LOG_DIR)
    logging.basicConfig(filename=os.path.join(LOG_DIR, 'rin.log'),
                        level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _logger = logging.getLogger('BitsharesExplorerParser')
    _assets_url = 'http://185.208.208.184:5000/assets'
    _assets_markets_url = 'http://185.208.208.184:5000/get_markets?asset_id={}'
    _lock = asyncio.Lock()
    _date = utils.get_today_date()
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'pairs'))
    _new_file = utils.get_file(WORK_DIR, f'pairs-{_date}.lst')
    _pairs_count = 0

    def __init__(self, loop):
        self.ioloop = loop

    async def _get_valid_assets(self, url):
        assets = await self._get_html(url)
        pprint(assets)

        valid_assets = []

        for asset in assets:
            if asset[4] > 5:
                valid_assets.append(asset)

    async def _get_html(self, url):
        await asyncio.sleep(random.randint(0, 30))
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()

            except aiohttp.client_exceptions.ClientConnectionError as err:
                self._logger.warning(err)

            except aiohttp.client_exceptions.ServerTimeoutError as err:
                self._logger.warning(err)

    def start_parsing(self):
        try:
            task = self.ioloop.create_task(self._get_valid_assets(self._assets_url))
            self.ioloop.run_until_complete(asyncio.gather(task))

            # task = self.ioloop.create_task(self._get_valid_data(*assets_page_html, OVERALL_MIN_DAILY_VOLUME, True))
            # assets = self.ioloop.run_until_complete(asyncio.gather(task))[0]
            #
            # tasks = [self.ioloop.create_task(self._get_html(self._assets_url.format(asset)))
            #          for asset in assets]
            # htmls = self.ioloop.run_until_complete(asyncio.gather(*tasks))
            #
            # tasks = [self.ioloop.create_task(self._get_valid_data(html_, PAIR_MIN_DAILY_VOLUME)) for html_ in htmls]
            # self.ioloop.run_until_complete(asyncio.wait(tasks))
            #
            # utils.remove_file(self._old_file)
            # self._logger.info(f'Parsed: {self._pairs_count} pairs.')
            #
            # return self._new_file

        except TypeError:
            self._logger.warning('HTML data retrieval error.')

            # return self._old_file
