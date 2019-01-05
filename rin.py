# -*- coding: utf-8
# TODO 1. Разобраться с упаковкой проекта в файл
# TODO 2. Сделать конфиг и использовать configparser
import logging
import asyncio

from libs.assetschainsmaker.chainscreator import ChainsCreator
# from libs.algorithms.bitsharesarbitrage import BitsharesArbitrage

logger = logging.getLogger('Rin')


class Rin:
    @staticmethod
    def start_arbitrage():
        ioloop = asyncio.get_event_loop()

        try:
            file_with_chains = ChainsCreator(ioloop).start_creating_chains()
            # BitsharesArbitrage(ioloop).start_arbitrage()
        finally:
            ioloop.close()


if __name__ == '__main__':
    Rin().start_arbitrage()
    # try:
    #     Rin().start_arbitrage()
    # except Exception as err:
    #     logger.warning(err)
