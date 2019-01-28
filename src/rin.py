# -*- coding: utf-8
# TODO 1. Разобраться с упаковкой проекта в файл
# TODO 2. Сделать конфиг и использовать configparser (прежде подумать , нужен ли он :D)
import logging
import asyncio
import uvloop


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
logger = logging.getLogger('Rin')


class Rin:
    @staticmethod
    def start_arbitrage():
        from src.libs.algorithms.bitsharesarbitrage import BitsharesArbitrage

        ioloop = asyncio.get_event_loop()

        try:
            BitsharesArbitrage(ioloop).start_arbitrage()
        finally:
            ioloop.close()


if __name__ == '__main__':
    Rin().start_arbitrage()
    # try:
    #     Rin().start_arbitrage()
    # except Exception as err:
    #     logger.warning(err)
