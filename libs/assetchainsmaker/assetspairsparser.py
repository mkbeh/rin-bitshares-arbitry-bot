# -*- coding: utf-8 -*-
import re
import random
import aiohttp
import asyncio

import aiofiles

from bs4 import BeautifulSoup

from const import OVERALL_MIN_DAILY_VOLUME, PAIR_MIN_DAILY_VOLUME, WORK_DIR
from libs import utils


class AssetsPairsParser:
    utils.dir_exists(WORK_DIR)
    utils.remove_file(utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'pairs')))
    _main_page_url = 'https://cryptofresh.com/assets'
    _assets_url = 'https://cryptofresh.com{}'
    _lock = asyncio.Lock()
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'pairs-{_date}.lst')

    async def write_asset_pair(self, pair):
        async with self._lock:
            async with aiofiles.open(self._new_file, 'a') as f:
                await f.write(f'{pair}\n')

    @staticmethod
    async def _get_volume(str_):
        pattern = re.compile(r'(\$\d+([,.]?\d+)*)')
        res = re.findall(pattern, str_)[-1]
        new_res = float(re.sub(r'\$?,?', '', res[0]).strip())

        return new_res

    @staticmethod
    async def _get_asset(str_, find_asset=False):
        pattern = re.compile(r'/a/\w+\.?\w+') if find_asset \
            else re.compile(r'\w+\.?\w+ : \w+\.?\w+')

        return re.findall(pattern, str_)[0].replace(' ', '').strip()

    async def _get_valid_data(self, html, min_volume, find_asset=False):
        bs_obj = BeautifulSoup(html, 'lxml')
        table = bs_obj.find('tbody')
        valid_assets = []

        for elem in table.find_all('tr'):
            data = await self._get_asset(str(elem), find_asset)
            vol = await self._get_volume(str(elem))

            if vol > min_volume:
                if not find_asset:
                    await self.write_asset_pair(data)
                    continue

                valid_assets.append(data)

            else:
                break

        return valid_assets

    @staticmethod
    async def _get_html(url):
        await asyncio.sleep(random.randint(0, 30))

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.text('utf-8')

    def start_parsing(self):
        my_event_loop = asyncio.get_event_loop()

        try:
            task = my_event_loop.create_task(self._get_html(self._main_page_url))
            assets_page_html = my_event_loop.run_until_complete(asyncio.gather(task))

            task = my_event_loop.create_task(self._get_valid_data(*assets_page_html, OVERALL_MIN_DAILY_VOLUME, True))
            assets = my_event_loop.run_until_complete(asyncio.gather(task))[0]

            tasks = [my_event_loop.create_task(self._get_html(self._assets_url.format(asset)))
                     for asset in assets]
            htmls = my_event_loop.run_until_complete(asyncio.gather(*tasks))

            tasks = [my_event_loop.create_task(self._get_valid_data(html_, PAIR_MIN_DAILY_VOLUME)) for html_ in htmls]
            my_event_loop.run_until_complete(asyncio.wait(tasks))

        finally:
            my_event_loop.close()
