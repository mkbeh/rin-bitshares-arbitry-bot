# -*- coding: utf-8 -*-
import random
import logging
import asyncio
import aiohttp
import aiofiles
import numpy as np

from . import utils
from .configcreator import ConfigCreator
from src.blacklistedassets import blacklisted_assets_lst


class BaseRin:
    cfg_data = ConfigCreator().get_cfg_data()

    output_dir = cfg_data.get('output dir')
    log_dir = cfg_data.get('log dir')

    overall_min_daily_volume = cfg_data.get('overall min daily volume')
    pair_min_daily_volume = cfg_data.get('pair min daily volume')

    volume_limits = cfg_data.get('volume limits')
    min_profit_limits = cfg_data.get('min profit limits')

    node_uri = cfg_data.get('node uri')
    wallet_uri = cfg_data.get('wallet uri')
    explorer_uri = cfg_data.get('explorer uri')

    account_name = cfg_data.get('account name')
    account_id = cfg_data.get('account id')
    wallet_pwd = cfg_data.get('wallet password')

    data_update_time = cfg_data.get('data update time')
    time_to_reconnect = cfg_data.get('time to reconnect')
    orders_depth = cfg_data.get('orders depth')

    dtype_float64 = np.float_
    dtype_int64 = np.int_

    work_dir = utils.get_dir('rin-bot')
    blacklist = utils.create_empty_file(
        work_dir, 'blacklist.lst'
    )
    utils.write_data_into_file(blacklist, blacklisted_assets_lst)

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
    def split_str_on_elements(seq):
        for el in seq:
            yield el.split(' ')

    @staticmethod
    def clear_each_str_in_seq(seq):
        for el in seq:
            yield el.replace('\n', '').strip()

    @staticmethod
    def _read_file(file):
        with open(file, 'r') as f:
            for line in f:
                yield line

    def get_transformed_data(self, file, generator=False):
        transformed_data = self.split_str_on_elements(
                                self.clear_each_str_in_seq(
                                    self._read_file(file)
                                )
                            )

        if generator:
            return transformed_data

        return tuple(transformed_data)

    @staticmethod
    def get_data_from_file(file):
        return utils.clear_each_str_in_seq(utils.read_file(file), '\n', ' ')

    def get_blacklisted_assets(self):
        blacklist_file = utils.get_file(self.work_dir, f'blacklist.lst')

        try:
            blacklisted_assets = self.get_data_from_file(blacklist_file)
        except FileNotFoundError:
            blacklisted_assets = []

        return blacklisted_assets
