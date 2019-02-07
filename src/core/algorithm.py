# -*- coding: utf-8 -*-
import itertools
import numpy as np


class ArbitrationAlgorithm:
    def __init__(self, chain, orders_data, volume_limit, default_bts_fee, assets_fees, profit_limit=None):
        self.chain = chain
        self.orders_data = orders_data
        self.vol_limit = volume_limit
        self.bts_default_fee = default_bts_fee
        self.assets_fees = assets_fees
        self.profit_limit = profit_limit

    async def __call__(self):
        return await self._run_data_through_algo()

    @staticmethod
    async def _prepare_orders_arr(arr):
        orders = itertools.chain.from_iterable(
            ((arr[2], arr[1]) for arr in arr)
        )
        new_arr = np.array([*orders])

        return new_arr

    @staticmethod
    async def _is_profit_valid(profit):
        return profit > 0

    @staticmethod
    async def _recalculate_vols_given_fees(pairs_arr, fees):
        new_quote0 = pairs_arr[0][1] - pairs_arr[0][1] * fees[0] / 100
        pairs_arr[1][2] = new_quote0
        pairs_arr[1][1] = pairs_arr[1][2] / pairs_arr[1][0]
        new_quote1 = pairs_arr[1][1] - pairs_arr[1][2] / pairs_arr[1][0] * fees[1] / 100
        pairs_arr[2][2] = new_quote1
        pairs_arr[2][1] = pairs_arr[2][2] / pairs_arr[2][0]
        new_quote2 = pairs_arr[2][1] - pairs_arr[2][2] / pairs_arr[2][0] * fees[2] / 100

        arr_with_final_vols = np.array([pairs_arr[0][2], new_quote2])

        return pairs_arr, arr_with_final_vols

    async def _final_part_of_algorithm(self, pairs_arr, fees):
        pairs_arr_given_fees, arr_with_final_vols = await self._recalculate_vols_given_fees(pairs_arr, fees)

        return arr_with_final_vols, pairs_arr_given_fees

    @staticmethod
    async def _fill_prices_with_zero(arr):
        arr[::1, 0] = 0

        return arr

    @staticmethod
    async def _compare_vols_second_step(pair0_arr, pair1_arr, pair2_arr):
        if pair1_arr[1] > pair2_arr[2]:
            pair1_arr[1] = pair2_arr[2]
            pair1_arr[2] = pair1_arr[1] * pair1_arr[0]
            pair0_arr[1] = pair1_arr[2]
            pair0_arr[2] = pair0_arr[1] * pair0_arr[0]

        elif pair1_arr[1] < pair2_arr[2]:
            pair2_arr[2] = pair1_arr[1]
            pair2_arr[1] = pair2_arr[2] / pair2_arr[0]

        return pair0_arr, pair1_arr, pair2_arr

    @staticmethod
    async def _compare_vols_first_step(pair0_arr, pair1_arr):
        if pair0_arr[1] > pair1_arr[2]:
            pair0_arr[1] = pair1_arr[2]
            pair0_arr[2] = pair0_arr[1] * pair0_arr[0]

        elif pair0_arr[1] < pair1_arr[2]:
            pair1_arr[2] = pair0_arr[1]
            pair1_arr[1] = pair1_arr[2] / pair1_arr[0]

        return pair0_arr, pair1_arr

    @staticmethod
    async def _compare_base_vol_and_vol_limit(pair0_arr, vol_limit):
        if pair0_arr[2] > vol_limit:
            pair0_arr[2] = vol_limit
            pair0_arr[1] = pair0_arr[2] / pair0_arr[0]

        return pair0_arr

    async def _recalculate_vols_within_fees(self, pair0_arr, pair1_arr, pair2_arr, vol_limit):
        pair0_arr = await self._compare_base_vol_and_vol_limit(pair0_arr, vol_limit)
        pair0_arr, pair1_arr = await self._compare_vols_first_step(pair0_arr, pair1_arr)
        pair0_arr, pair1_arr, pair2_arr = await self._compare_vols_second_step(pair0_arr, pair1_arr, pair2_arr)
        arr = np.array([pair0_arr, pair1_arr, pair2_arr], dtype=float)

        return arr

    @staticmethod
    async def _get_profit(init_vol, final_vol, bts_default_fee):
        return final_vol - init_vol - bts_default_fee

    async def _basic_algo(self, pair0_arr, pair1_arr, pair2_arr, vol_limit, fees):
        pairs_arr = await self._recalculate_vols_within_fees(pair0_arr, pair1_arr, pair2_arr, vol_limit)
        final_vols, pairs_arrs_given_fees = await self._final_part_of_algorithm(pairs_arr, fees)
        pairs_arrs_given_fees = await self._fill_prices_with_zero(pairs_arrs_given_fees)

        return final_vols, pairs_arrs_given_fees

    async def _ext_algo(self, arr, pair0_arr, pair1_arr, pair2_arr, vol_limit, fees):
        if arr[0][2] >= vol_limit:
            return np.delete(arr, np.s_[:])

        new_vol_limit = vol_limit - arr[0][2]
        pairs_arr = await self._recalculate_vols_within_fees(pair0_arr, pair1_arr, pair2_arr, new_vol_limit)
        final_vols, pairs_arrs_given_fees = await self._final_part_of_algorithm(pairs_arr, fees)
        vols_sum = await self._fill_prices_with_zero(arr + pairs_arrs_given_fees)

        return final_vols, vols_sum

    async def _run_data_through_algo(self):

        len_any_arr = len(self.orders_data[0])
        algo_data = await self._basic_algo(self.orders_data[0][0], self.orders_data[1][0], self.orders_data[2][0],
                                           self.vol_limit, self.assets_fees)
        profit = await self._get_profit(*algo_data[0], self.bts_default_fee)

        for i in range(1, len_any_arr):
            new_algo_data = await self._ext_algo(algo_data[1], self.orders_data[0][i],
                                                 self.orders_data[1][i], self.orders_data[2][i],
                                                 self.vol_limit, self.assets_fees)
            if len(new_algo_data) == 0:
                break

            new_profit = await self._get_profit(*new_algo_data[0], self.bts_default_fee)

            if profit > new_profit:
                break

            algo_data = new_algo_data
            profit = new_profit

        is_profit = await self._is_profit_valid(profit)

        if is_profit:
            return await self._prepare_orders_arr(algo_data[1])

        return np.delete(algo_data[1], np.s_[:])
