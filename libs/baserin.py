# -*- coding: utf-8 -*-
import os
import random
import logging
import asyncio
import aiohttp
import aiofiles

from libs import utils
from const import LOG_DIR, WORK_DIR


class BaseRin:
    utils.dir_exists(WORK_DIR)
    utils.dir_exists(LOG_DIR)
    logging.basicConfig(filename=os.path.join(LOG_DIR, 'rin.log'),
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    @staticmethod
    async def _write_data(data, file, lock):
        async with lock:
            async with aiofiles.open(file, 'a') as f:
                await f.write(f'{data}\n')

    @staticmethod
    async def get_data(url, logger, delay, json=False):
        await asyncio.sleep(random.randint(0, delay))
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        if json:
                            return await resp.json()

                        return await resp.text('utf-8')

            except aiohttp.client_exceptions.ClientConnectionError as err:
                logger.warning(err)

            except aiohttp.client_exceptions.ServerTimeoutError as err:
                logger.warning(err)

    @staticmethod
    def _actions_when_error(msg, logger, retrieve_file=None, value_from_file=False):
        logger.warning(msg)

        if retrieve_file:
            if value_from_file:
                return utils.read_file(retrieve_file)[0].replace('\n', '').strip()

            return retrieve_file

