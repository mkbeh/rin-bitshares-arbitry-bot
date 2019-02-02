# -*- coding: utf-8 -*-
import numpy as np


class ArbitrationAlgorithm:

    def __init__(self, orders_data, volume_limit, default_bts_fee, assets_fees, profit_limit=None):
        self.orders_data = orders_data
        self.vol_limit = volume_limit
        self.bts_default_fee = default_bts_fee
        self.assets_fees = assets_fees
        self.profit_limit = profit_limit

    async def __call__(self):
        return await self._run_data_through_algo()

    @staticmethod
    async def _decide_order_placed(arr):
        if len(arr) == 3:
            print('Set orders HERE!!!')
            return True

        return False

    @staticmethod
    async def _is_profit(init_vol, final_vol, bts_default_fee):
        return init_vol < (final_vol - bts_default_fee)

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

    async def _final_part_of_algorithm(self, pairs_arr, arr_copy, fees, bts_default_fee):
        pairs_arr_given_fees, arr_with_final_vols = await self._recalculate_vols_given_fees(pairs_arr, fees)
        have_profit = await self._is_profit(*arr_with_final_vols, bts_default_fee)
        orders_arr = np.array([
            pairs_arr_given_fees[0][2], pairs_arr_given_fees[0][1],
            pairs_arr_given_fees[1][2], pairs_arr_given_fees[1][1],
            pairs_arr_given_fees[2][2], pairs_arr_given_fees[2][1],
        ], dtype=float)

        if have_profit:
            return orders_arr

        return orders_arr, arr_copy

    @staticmethod
    async def _fill_prices_with_zero(arr):
        arr[::1, 0] = 0

        return arr

    async def _get_arr_copy(self, arr):
        arr_copy = arr.copy()

        return await self._fill_prices_with_zero(arr_copy)

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

    async def _basic_algo(self, pair0_arr, pair1_arr, pair2_arr, vol_limit, bts_default_fee, fees):
        pairs_arr = await self._recalculate_vols_within_fees(pair0_arr, pair1_arr, pair2_arr, vol_limit)
        pairs_arr_copy = await self._get_arr_copy(pairs_arr)

        return await self._final_part_of_algorithm(pairs_arr, pairs_arr_copy, fees, bts_default_fee)

    async def _ext_algo(self, arr, pair0_arr, pair1_arr, pair2_arr, vol_limit, bts_default_fee, fees):
        if arr[0][2] >= vol_limit:
            return np.delete(arr, np.s_[:])

        new_vol_limit = vol_limit - arr[0][2]
        pairs_arr = await self._recalculate_vols_within_fees(pair0_arr, pair1_arr, pair2_arr, new_vol_limit)
        vols_sum = arr + pairs_arr
        vols_sum_copy = await self._get_arr_copy(vols_sum)

        return await self._final_part_of_algorithm(pairs_arr, vols_sum_copy, fees, bts_default_fee)

    @staticmethod
    async def _get_max_len_of_arrs(np_arr):
        return max(map(lambda x: len(x), np_arr))

    async def _run_data_through_algo(self):
        len_of_largest_arr = await self._get_max_len_of_arrs(self.orders_data)
        algo_data = await self._basic_algo(self.orders_data[0][0], self.orders_data[1][0], self.orders_data[2][0],
                                           self.vol_limit, self.bts_default_fee, self.assets_fees)

        orders_placed = await self._decide_order_placed(algo_data)

        if orders_placed:
            return

        orders = algo_data[0]

        for i in range(1, len_of_largest_arr):
            algo_data = await self._ext_algo(algo_data[1], self.orders_data[0][i],
                                             self.orders_data[1][i], self.orders_data[2][i],
                                             self.vol_limit, self.bts_default_fee, self.assets_fees)

            if len(algo_data) == 0:
                break

            orders_placed = await self._decide_order_placed(algo_data)

            if orders_placed:
                return

            orders += algo_data[0]
