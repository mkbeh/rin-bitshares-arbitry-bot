# -*- coding: utf-8
# TODO 1. Разобраться с упаковкой проекта в файл
# TODO 2. Сделать конфиг и использовать configparser (прежде подумать , нужен ли он :D)
import logging
import asyncio

from libs.algorithms.bitsharesarbitrage import BitsharesArbitrage
from libs.limitsandfees.gatewaypairfee import GatewayPairFee

logger = logging.getLogger('Rin')


class Rin:
    @staticmethod
    def start_arbitrage():
        ioloop = asyncio.get_event_loop()

        try:
            # BitsharesArbitrage(ioloop).start_arbitrage()
            # DefaultBTSFee(ioloop).run()
            GatewayPairFee(ioloop).get_chains_fees()
        finally:
            ioloop.close()


if __name__ == '__main__':
    Rin().start_arbitrage()
    # try:
    #     Rin().start_arbitrage()
    # except Exception as err:
    #     logger.warning(err)
