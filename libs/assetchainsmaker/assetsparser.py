# -*- coding: utf-8 -*-
import time
import re

import requests

from multiprocessing import Process, RLock

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from libs.assetchainsmaker.baseassetchainsmaker import BaseAssetChainsMaker
from const import WORK_DIR, MIN_DAILY_VOLUME
from libs import utils
from libs import decorators


class AssetsPairsParser(BaseAssetChainsMaker):
    _urls = {
        'bridge.btc': 'https://cryptofresh.com/a/BRIDGE.BTC',
        'bts': 'https://cryptofresh.com/a/BTS',
        'cny': 'https://cryptofresh.com/a/CNY',
        'usd': 'https://cryptofresh.com/a/USD',
        'open.btc': 'https://cryptofresh.com/a/OPEN.BTC',
        'gdex.btc': 'https://cryptofresh.com/a/GDEX.BTC',
    }
    _lock = RLock()
    _min_daily_volume = MIN_DAILY_VOLUME
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'pairs'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'pairs-{_date}.lst')

    @staticmethod
    def _requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
        session = session or requests.Session()
        retry = Retry(total=retries, read=retries, connect=retries,
                      backoff_factor=backoff_factor, status_forcelist=status_forcelist)

        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def _get_html(self, url):
        time.sleep(2)

        try:
            return self._requests_retry_session().get(url, timeout=(3.05, 27), stream=True).content
        except Exception as e:
            raise Exception(e)

    @decorators.write_data_into_file(_new_file, _lock)
    def _filter_pairs(self, parsed_data):
        new_tds = [[parsed_data[i], parsed_data[i + 4]] for i in range(0, len(parsed_data), 5)]
        filtered_pairs = []

        for pair, vol in new_tds:
            vol = int(re.sub(r'\$?,?', '', vol.get_text()))

            if vol > self._min_daily_volume:
                try:
                    pair = pair.strong.get_text().replace(' ', '').strip()
                except AttributeError:
                    pair = pair.find('a').get_text().replace(' ', '').strip()

                filtered_pairs.append(pair)

        return filtered_pairs

    def _parse_pairs(self, html):
        bs_obj = BeautifulSoup(html, 'lxml')
        pairs_table = bs_obj.find('div', {'class': 'col-md-8'})
        tds = pairs_table.findAll('td')
        self._filter_pairs(tds)

    def start_parsing(self):
        htmls = [self._get_html(value) for _, value in self._urls.items()]
        self._run_in_multiprocessing(self._parse_pairs, htmls)
        self._compare_files_with_pairs(self._old_file, self._new_file, self._lock)

        return self._new_file
