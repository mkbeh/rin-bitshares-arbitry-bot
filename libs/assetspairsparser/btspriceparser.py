# -*- coding: utf-8 -*-
import logging
import asyncio

from bs4 import BeautifulSoup

from libs.assetchainsmaker.baseassetschainsmaker import BaseAssetsChainsMaker
from libs import utils
from const import WORK_DIR


class BTSPriceParser(BaseAssetsChainsMaker):
    _logger = logging.getLogger('BTSPriceParser')
    _url = 'https://www.coingecko.com/ru/%D0%B4%D0%B8%D0%BD%D0%B0%D0%BC%D0%B8%D0%BA%D0%B0_%D1%86%D0%B5%D0%BD' \
           '/bitshares/usd'
    _lock = asyncio.Lock()
    _date = utils.get_today_date()
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'bst_price'))
    _new_file = utils.get_file(WORK_DIR, f'bst_price-{_date}.lst')

    def __init__(self, loop):
        self.ioloop = loop

    async def _parse_price(self, url):
        html = await self._get_html(url, self._logger)

        bs_obj = BeautifulSoup(html, 'lxml')
        price = bs_obj.find('span', {'data-coin-symbol': 'bts'}).get_text()\
            .replace('$', '').replace(',', '.').replace(' ', '').strip()
        await self._write_data(price, self._new_file, self._lock)

        return float(price)

    def get_bts_price_in_usd(self):
        try:
            task = self.ioloop.create_task(self._parse_price(self._url))
            price = self.ioloop.run_until_complete(asyncio.gather(task))
            utils.remove_file(self._old_file)
            self._logger.info(f'BTS price is {price[0]}.')

            return price[0]

        except TypeError:
            self._logger.warning('HTML data retrieval error.')

            return self._old_file
