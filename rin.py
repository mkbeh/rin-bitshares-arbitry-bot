# -*- coding: utf-8
import logging
import asyncio

from libs.assetchainsmaker.chainscreator import ChainsCreator
from libs.algorithms.bitsharesarbitrage import BitsharesArbitrage


logger = logging.getLogger('Rin')


class Rin:
    @staticmethod
    def start_arbitrage():
        BitsharesArbitrage().foo()
        # ioloop = asyncio.get_event_loop()
        #
        # try:
        #     file_with_chains = ChainsCreator(ioloop).start_creating_chains()
        # finally:
        #     ioloop.close()


if __name__ == '__main__':
    try:
        Rin().start_arbitrage()
    except Exception as err:
        logger.warning(err)
