# -*- coding: utf-8 -*-
from pprint import pprint

from bitshares import BitShares

from libs.assetchainsmaker.chainscreator import ChainsCreator
from libs import utils


class BitsharesArbitrage:
    def foo(self):
        testnet = BitShares(
            "wss://bitshares.openledger.info/ws",
        )

        testnet.wallet.unlock("P5K9YsxTj3YrPPM4ZKBrxcA7sgL1DkSRXw6DmDPJNo3yx")
        testnet.transfer("makar0ff", 1, "BTS", account="mkbehforever007")

    # def __init__(self, loop):
    #     self._file_with_chains = ChainsCreator(loop).start_creating_chains()
    #     self.ioloop = loop
    #
    # def _get_chains_from_file(self):
    #     try:
    #         return utils.clear_each_str_in_seq(utils.read_file(self._file_with_chains), '\n', ' ')
    #     except Exception as err:
    #         raise Exception(err)
