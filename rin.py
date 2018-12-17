# -*- coding: utf-8
import logging
import asyncio

from libs.assetchainsmaker.chainscreator import ChainsCreator


logger = logging.getLogger('Rin')


class Rin:
    @staticmethod
    def start_arbitrage():
        ioloop = asyncio.get_event_loop()

        try:
            file_with_chains = ChainsCreator(ioloop).start_creating_chains()
        finally:
            ioloop.close()


if __name__ == '__main__':
    try:
        Rin().start_arbitrage()
    except Exception as err:
        logger.warning(err)
