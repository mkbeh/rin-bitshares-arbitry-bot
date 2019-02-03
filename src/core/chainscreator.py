# -*- coding: utf-8 -*-
import logging
import asyncio
import aiofiles

from src.extra.baserin import BaseRin
from src.parsers.cryptofreshparser import CryptofreshParser
from src.parsers.bitsharesexplorerparser import BitsharesExplorerParser
from src.aiopybitshares.asset import Asset
from src.const import WORK_DIR
from src.extra import utils


class ChainsCreator(BaseRin):
    _logger = logging.getLogger('ChainsCreator')
    _lock = asyncio.Lock()
    _main_assets = ['BTS', 'BRIDGE.BTC', 'CNY', 'USD']
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'chains'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'chains-{_date}.lst')
    _chains_count = 0

    def __init__(self, loop):
        self._ioloop = loop
        self._file_with_pairs = self._get_file_with_pairs()

    def _get_file_with_pairs(self):
        parsers = [BitsharesExplorerParser, CryptofreshParser]
        file_with_pairs = []

        for parser in parsers:
            file_data = parser(self._ioloop).start_parsing()

            try:
                if file_data.new_version:
                    return file_data.file
            except AttributeError:
                file_with_pairs.append(file_data)

        return file_with_pairs[0]

    async def _write_chain(self, chain):
        async with self._lock:
            async with aiofiles.open(self._new_file, 'a') as f:
                await f.write(f'{chain}\n')

    @staticmethod
    async def _get_chain_with_ids(pygram_obj, *args):
        chains_with_ids = list(args)

        for i in range(0, len(args), 2):
            chains_with_ids[i] = chains_with_ids[i-1] = await pygram_obj.convert_name_to_id(args[i])

        return '{}:{} {}:{} {}:{}'.format(*chains_with_ids)

    @staticmethod
    async def _adjust_asset_location_in_seq(asset, seq):
        if seq[0] != asset:
            seq.reverse()

        return seq

    async def _create_chains_for_asset(self, main_asset, pairs):
        chains = []
        pygram_asset = Asset()
        await pygram_asset.connect()

        for pair in pairs:
            if main_asset in pair:
                main = (await self._adjust_asset_location_in_seq(main_asset, pair)).copy()

                for pair2 in pairs:
                    if main[1] in pair2 and main_asset not in pair2:
                        secondary = (await self._adjust_asset_location_in_seq(main[1], pair2)).copy()

                        for pair3 in pairs:
                            if secondary[1] in pair3 and main_asset in pair3:
                                tertiary = (await self._adjust_asset_location_in_seq(secondary[1], pair3)).copy()
                                chain = await self._get_chain_with_ids(pygram_asset, *main, *secondary, *tertiary)

                                if chain not in chains:
                                    chains.append(chain)
                                    self._chains_count += 1
                                    await self._write_chain(chain)

        await pygram_asset.close()

    @staticmethod
    def _remove_pairs_duplicates_from_seq(seq):
        new_seq = list(map(lambda x: x.split(':'), seq))

        for el in new_seq:
            el.reverse()

            if el in new_seq:
                index = new_seq.index(el)
                del new_seq[index]

        return new_seq

    def _get_pairs_from_file(self):
        return utils.clear_each_str_in_seq(utils.read_file(self._file_with_pairs), '\n', ' ')

    def start_creating_chains(self):
        try:
            pairs_lst = self._remove_pairs_duplicates_from_seq(self._get_pairs_from_file())
            tasks = [self._ioloop.create_task(self._create_chains_for_asset(asset, pairs_lst))
                     for asset in self._main_assets]
            self._ioloop.run_until_complete(asyncio.wait(tasks))

        except Exception as err:
            return self.actions_when_error(err, self._logger, self._old_file)

        else:
            utils.remove_file(self._old_file)
            self._logger.info(f'Created: {self._chains_count} chains.\n')

            return self._new_file
