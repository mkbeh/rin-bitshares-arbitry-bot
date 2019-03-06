# -*- coding: utf-8
import os
import asyncio
import uvloop

from src.extra.baserin import BaseRin


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
logger = BaseRin.setup_logger('Rin', os.path.join(BaseRin.log_dir, 'rin.log'))


class Rin:
    @staticmethod
    def start_arbitrage():
        from src.core.bitsharesarbitrage import BitsharesArbitrage
        ioloop = asyncio.get_event_loop()

        try:
            BitsharesArbitrage(ioloop).start_arbitrage()
        finally:
            ioloop.close()


def main():
    try:
        Rin().start_arbitrage()
    except Exception as err:
        logger.exception('Got unhandled exception.', err)


if __name__ == '__main__':
    main()
