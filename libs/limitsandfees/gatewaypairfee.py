# -*- coding: utf-8 -*-
import logging
import asyncio
import itertools

from decimal import Decimal

from libs.baserin import BaseRin
from libs.aiopybitshares.asset import Asset
from libs.assetschainsmaker.chainscreator import ChainsCreator
from libs import utils

from const import WALLET_URI, WORK_DIR


class GatewayPairFee(BaseRin):
    _url = 'https://wallet.bitshares.org/#/market/{}_{}'
    _logger = logging.getLogger('GatewayPairFee')
    _lock = asyncio.Lock()
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'chains_with_fees'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'chains_with_fees-{_date}.lst')

    def __init__(self, loop):
        self._ioloop = loop
        self._file_with_chains = ChainsCreator(self._ioloop)
        self._fees_count = 0
        self._chains_num = None

    async def foo(self, chain):
        assets_objs = [Asset() for _ in range(len(chain))]
        [await asset_obj.alternative_connect(WALLET_URI) for asset_obj in assets_objs]

        raw_chain_fees = await asyncio.gather(
            *[obj.get_asset_info(pair.split(':')[1]) for obj, pair in zip(assets_objs, chain)]
        )

        fees = [str(Decimal(fee['options']['market_fee_percent']) / Decimal(100))
                for fee in raw_chain_fees]

        data = '{} {} {} {} {} {}'.format(*itertools.chain(chain, fees))
        await self.write_data(data, self._new_file, self._lock)
        self._fees_count += 3

        [await asset_obj.close() for asset_obj in assets_objs]

    @staticmethod
    def _split_chain_on_pairs(seq):
        for el in seq:
            yield el.split(' ')

    @staticmethod
    def _clear_each_str_in_seq(seq):
        for el in seq:
            yield el.replace('\n', '').strip()

    @staticmethod
    def _read_file(file):
        with open(file, 'r') as f:
            for line in f:
                yield line

    def _get_chains(self):
        return list(
            self._split_chain_on_pairs(
                self._clear_each_str_in_seq(
                    self._read_file(self._file_with_chains)
                )
            )
        )

    def get_chains_fees(self):
        chains = self._get_chains()
        self._chains_num = len(chains)
        tasks = [self._ioloop.create_task(self.foo(chain)) for chain in chains]

        try:
            self._ioloop.run_until_complete(asyncio.gather(*tasks))
        except Exception as err:
            self._actions_when_error(err, self._logger, self._old_file)
        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Successfully got {self._fees_count} fees for {self._chains_num} chains.')

            return self._new_file
