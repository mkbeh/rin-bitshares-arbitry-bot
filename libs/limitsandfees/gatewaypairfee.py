# -*- coding: utf-8 -*-
"""
Цель: создать отдельный файл с цепочками , где напротив каждой цепочки будут указаны %.
Пример: <chain> <[1st %] [2nd %] [3rd %]>
"""
import logging
import asyncio

from libs.baserin import BaseRin
from libs.assetschainsmaker.chainscreator import ChainsCreator
from pprint import pprint


class GatewayPairFee:
    _url = 'https://wallet.bitshares.org/#/market/{}_{}'
    _logger = logging.getLogger('ChainsCreator')
    _lock = asyncio.Lock()

    def __init__(self):
        # self._file_with_chains = ChainsCreator(self._ioloop)
        self._file_with_chains = '/home/cyberpunk/PycharmProjects/rin-bitshares-arbitry-bot/' \
                                 'output/chains-05-01-2019-15-35-09.lst'

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

        for chain in chains[:1]:
            self._get_html(chain)
