# -*- coding: utf-8
import logging
import asyncio

# from libs.assetchainsmaker.chainscreator import ChainsCreator
from libs.assetspairsparser.bitsharesexplorerparser import BitsharesExplorerParser
from libs.assetspairsparser.btspriceparser import BTSPriceParser


logger = logging.getLogger('Rin')


class Rin:
    @staticmethod
    def start_arbitrage():
        ioloop = asyncio.get_event_loop()

        try:
            BTSPriceParser(ioloop).get_bts_price_in_usd()
            # BitsharesExplorerParser(ioloop).start_parsing()
            # file_with_chains = ChainsCreator(ioloop).start_creating_chains()
        finally:
            ioloop.close()


if __name__ == '__main__':
    try:
        Rin().start_arbitrage()
    except Exception as err:
        logger.warning(err)
