# -*- coding: utf-8 -*-
import re
import logging
import asyncio

from collections import namedtuple

from bs4 import BeautifulSoup

from libs.baserin import BaseRin
from const import OVERALL_MIN_DAILY_VOLUME, PAIR_MIN_DAILY_VOLUME, WORK_DIR
from libs import utils


class CryptofreshParser(BaseRin):
    _logger = logging.getLogger('CryptofreshParser')
    _main_page_url = 'https://cryptofresh.com/assets'
    _assets_url = 'https://cryptofresh.com{}'
    _lock = asyncio.Lock()
    _date = utils.get_today_date()
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'pairs'))
    _new_file = utils.get_file(WORK_DIR, f'pairs-{_date}.lst')
    _pairs_count = 0

    def __init__(self, loop):
        self._ioloop = loop

    @staticmethod
    async def _get_volume(str_):
        pattern = re.compile(r'(\$\d+([,.]?\d+)*)')
        res = re.findall(pattern, str_)[2]
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

        for i, elem in enumerate(table.find_all('tr')):
            data = await self._get_asset(str(elem), find_asset)

            try:
                vol = await self._get_volume(str(elem))
            except IndexError:
                break

            if vol > min_volume:
                if not find_asset:
                    await self.write_data(data, self._new_file, self._lock)
                    self._pairs_count += 1
                    continue

                valid_assets.append(data)

            else:
                break

        if find_asset:
            self._logger.info(f'Parsed: {len(valid_assets)} assets.')

        return valid_assets

    def start_parsing(self):
        try:
            task = self._ioloop.create_task(self.get_data(self._main_page_url, self._logger, delay=2))
            assets_page_html = self._ioloop.run_until_complete(asyncio.gather(task))

            task = self._ioloop.create_task(self._get_valid_data(*assets_page_html, OVERALL_MIN_DAILY_VOLUME, True))
            assets = self._ioloop.run_until_complete(asyncio.gather(task))[0]

            if assets:
                tasks = [self._ioloop.create_task(self.get_data(self._assets_url.format(asset), self._logger, delay=30))
                         for asset in assets]
                htmls = self._ioloop.run_until_complete(asyncio.gather(*tasks))

                tasks = [self._ioloop.create_task(self._get_valid_data(html_, PAIR_MIN_DAILY_VOLUME)) for html_ in htmls]
                self._ioloop.run_until_complete(asyncio.wait(tasks))

                utils.remove_file(self._old_file)
                self._logger.info(f'Parsed: {self._pairs_count} pairs.')
                FileData = namedtuple('FileData', ['file', 'new_version'])

                return FileData(self._new_file, True)

            else:
                self._logger.info('Cryptofresh assets is corrupted (low vol).')

                return self._old_file

        except TypeError:
            self._actions_when_error('HTML data retrieval error.', self._logger, self._old_file)

        except Exception as err:
            self._actions_when_error(err, self._logger, self._old_file)
