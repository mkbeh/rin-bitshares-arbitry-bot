# -*- coding: utf-8 -*-
import logging
import asyncio

from bs4 import BeautifulSoup

from src.extra.baserin import BaseRin
from src.extra import utils
from src.const import WORK_DIR


class BTSPriceParser(BaseRin):
    _logger = logging.getLogger('Rin.BTSPriceParser')
    _site_url = 'https://www.coingecko.com/ru/%D0%B4%D0%B8%D0%BD%D0%B0%D0%BC%D0%B8%D0%BA%D0%B0_%D1%86%D0%B5%D0%BD' \
                '/bitshares/usd'
    _node_url = 'http://185.208.208.184:5000/get_ticker?base=USD&quote=BTS'
    _lock = asyncio.Lock()
    _date = utils.get_today_date()
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'bst_price'))
    _new_file = utils.get_file(WORK_DIR, f'bst_price-{_date}.lst')

    def __init__(self, loop):
        self.ioloop = loop

    async def _get_price_from_node(self):
        response = await self.get_data(self._node_url, delay=2, logger=self._logger, json=True)

        try:
            return float(response['latest'])
        except KeyError:
            self._logger.warning(response['detail'])

    async def _parse_price_from_site(self):
        html = await self.get_data(self._site_url, delay=2, logger=self._logger)

        bs_obj = BeautifulSoup(html, 'lxml')
        price = bs_obj.find('span', {'data-coin-symbol': 'bts'}).get_text() \
            .replace('$', '').replace(',', '.').replace(' ', '').strip()

        return float(price)

    async def _get_price(self):
        methods = [self._get_price_from_node, self._parse_price_from_site]

        for method in methods:
            price = await method()

            if price:
                await self.write_data(str(price), self._new_file, self._lock)
                return price

        self._logger.warning('Could not get BTS price in USD.')
        return self.actions_when_error(self._old_file, value_from_file=True)

    def get_bts_price_in_usd(self):
        task = self.ioloop.create_task(self._get_price())

        try:
            price = self.ioloop.run_until_complete(asyncio.gather(task))

        except ValueError:
            self._logger.exception('Could not convert parsed price to float.')
            return self.actions_when_error(self._old_file, value_from_file=True)

        except AttributeError:
            self._logger.exception('Could not get price from html.')
            return self.actions_when_error(self._old_file, value_from_file=True)

        except TypeError:
            self._logger.exception('HTML data retrieval error.')
            return self.actions_when_error(self._old_file, value_from_file=True)

        except Exception as err:
            self._logger.exception('Exception occurred while getting BTS price.', err)
            return self.actions_when_error(self._old_file, value_from_file=True)

        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'BTS price is ${price[0]}.')

            return price[0]
