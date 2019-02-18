# -*- coding: utf-8
# TODO 2. Сделать конфиг и использовать configparser (прежде подумать , нужен ли он :D)
import os
import asyncio
import uvloop

from src.const import LOG_DIR
from src.extra.baserin import BaseRin

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
logger = BaseRin.setup_logger('Rin', os.path.join(LOG_DIR, 'rin.log'))


class Rin:
    @staticmethod
    def start_arbitrage():
        from src.core.bitsharesarbitrage import BitsharesArbitrage
        ioloop = asyncio.get_event_loop()

        from src.parsers.bitsharesexplorerparser import BitsharesExplorerParser
        BitsharesExplorerParser(ioloop).start_parsing()

        # try:
        #     BitsharesArbitrage(ioloop).start_arbitrage()
        # finally:
        #     ioloop.close()


def main():
    Rin().start_arbitrage()
    # try:
    #     Rin().start_arbitrage()
    # except Exception as err:
    #     logger.exception('Got unhandled exception.', err)


if __name__ == '__main__':
    main()
