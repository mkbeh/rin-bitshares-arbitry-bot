# -*- coding: utf-8 -*-
import random
import logging
import asyncio
import aiohttp
import aiofiles

from . import utils
from src.const import LOG_DIR, WORK_DIR


class BaseRin:
    utils.dir_exists(WORK_DIR)
    utils.dir_exists(LOG_DIR)

    @staticmethod
    def setup_logger(logger_name, log_file, level=logging.INFO):
        logger = logging.getLogger(logger_name)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        logger.setLevel(level)
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    async def write_data(data, file, lock=None):
        if lock:
            await lock.acquire()

        try:
            async with aiofiles.open(file, 'a') as f:
                await f.write(f'{data}\n')
        finally:
            if lock:
                lock.release()

    @staticmethod
    async def get_data(url, delay, logger, json=False):
        await asyncio.sleep(random.randint(0, delay))
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        if json:
                            return await resp.json()

                        return await resp.text('utf-8')

            except aiohttp.ClientConnectionError:
                logger.exception('Error while getting data.')

            except aiohttp.ServerTimeoutError:
                logger.exception('Error while getting data.')

    @staticmethod
    def actions_when_error(retrieve_file=None, value_from_file=False):
        if retrieve_file:
            if value_from_file:
                return utils.read_file(retrieve_file)[0].replace('\n', '').strip()

            return retrieve_file

    @staticmethod
    def actions_when_errors_with_read_data(file):
        return utils.read_file(file)

    @staticmethod
    def _split_chain_on_pairs(seq):
        for el in seq:
            yield el.split(' ')

    @staticmethod
    def _clear_each_str_in_seq(seq):
        for el in seq:
            yield el.replace('\n', '').strip()

    @staticmethod
    def _read_file(file):
        with open(file, 'r') as f:
            for line in f:
                yield line

    def get_chains(self, file):
        return list(
            self._split_chain_on_pairs(
                self._clear_each_str_in_seq(
                    self._read_file(file)
                )
            )
        )

