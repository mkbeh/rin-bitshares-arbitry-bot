# -*- coding: utf-8 -*-
import math
import numpy as np

from dataclasses import dataclass


DTYPE_FLOAT64 = np.float64


@dataclass(repr=False, eq=False)
class ArbitrationAlgorithm:
    __slots__ = ['_orders_data', '_vol_limit', '_bts_default_fee', '_assets_fees', '_profit_limit', '_precisions_arr']

    _orders_data: np.ndarray
    _vol_limit: DTYPE_FLOAT64
    _bts_default_fee: DTYPE_FLOAT64
    _assets_fees: np.ndarray
    _profit_limit: DTYPE_FLOAT64
    _precisions_arr: np.ndarray

    async def __call__(self):
        return await self._run_data_through_algo()

    async def _round_vols_to_specific_prec(self, vols_arr: np.ndarray) -> np.ndarray:
        def round_half_up(n, decimals):
            multiplier = 10 ** decimals
            return math.floor(n * multiplier + 0.5) / multiplier

        flatten_vols_arr = vols_arr.flatten()
        vols_arr_with_precs = np.fromiter(
            (round_half_up(vol, prec) for vol, prec in zip(flatten_vols_arr, self._precisions_arr)),
            dtype=DTYPE_FLOAT64)

        profit = await self._get_profit(vols_arr_with_precs[0], vols_arr_with_precs[-1])

        return vols_arr_with_precs \
            if await self._is_profit_valid(profit) \
            else np.delete(vols_arr_with_precs, np.s_[:])

    async def _prepare_orders_arr(self, arr: np.ndarray, profit: DTYPE_FLOAT64) -> tuple:
        vols_arr_without_prices = np.array([
            *((el[2], el[1]) for el in arr)
        ], dtype=DTYPE_FLOAT64)

        rounded_vols_arr = await self._round_vols_to_specific_prec(vols_arr_without_prices)

        if rounded_vols_arr.size:
            return rounded_vols_arr.reshape(3, 2), profit

        return rounded_vols_arr, profit

    async def _is_profit_valid(self, profit: DTYPE_FLOAT64) -> bool:
        return profit > self._profit_limit

    async def _recalculate_vols_given_fees(self, pairs_arr: np.ndarray) -> tuple:
        new_quote0 = pairs_arr[0][1] - pairs_arr[0][1] * self._assets_fees[0] / 100
        pairs_arr[1][2] = new_quote0
        pairs_arr[1][1] = pairs_arr[1][2] / pairs_arr[1][0]
        new_quote1 = pairs_arr[1][1] - pairs_arr[1][2] / pairs_arr[1][0] * self._assets_fees[1] / 100
        pairs_arr[2][2] = new_quote1
        pairs_arr[2][1] = pairs_arr[2][2] / pairs_arr[2][0]
        new_quote2 = pairs_arr[2][1] - pairs_arr[2][2] / pairs_arr[2][0] * self._assets_fees[2] / 100

        arr_with_final_vols = np.array([pairs_arr[0][2], new_quote2], dtype=DTYPE_FLOAT64)

        return arr_with_final_vols, pairs_arr

    @staticmethod
    async def _fill_prices_with_zero(arr: np.ndarray) -> np.ndarray:
        arr[::1, 0] = 0

        return arr

    @staticmethod
    async def _compare_vols_second_step(pair0_arr: np.ndarray, pair1_arr: np.ndarray,
                                        pair2_arr: np.ndarray) -> tuple:
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
    async def _compare_vols_first_step(pair0_arr: np.ndarray, pair1_arr: np.ndarray) -> tuple:
        if pair0_arr[1] > pair1_arr[2]:
            pair0_arr[1] = pair1_arr[2]
            pair0_arr[2] = pair0_arr[1] * pair0_arr[0]

        elif pair0_arr[1] < pair1_arr[2]:
            pair1_arr[2] = pair0_arr[1]
            pair1_arr[1] = pair1_arr[2] / pair1_arr[0]

        return pair0_arr, pair1_arr

    @staticmethod
    async def _compare_base_vol_and_vol_limit(pair0_arr: np.ndarray, vol_limit: DTYPE_FLOAT64) -> np.ndarray:
        if pair0_arr[2] > vol_limit:
            pair0_arr[2] = vol_limit
            pair0_arr[1] = pair0_arr[2] / pair0_arr[0]

        return pair0_arr

    async def _recalculate_vols_within_fees(self, pair0_arr: np.ndarray, pair1_arr: np.ndarray,
                                            pair2_arr: np.ndarray, vol_limit: DTYPE_FLOAT64) -> np.ndarray:
        pair0_arr = await self._compare_base_vol_and_vol_limit(pair0_arr, vol_limit)
        pair0_arr, pair1_arr = await self._compare_vols_first_step(pair0_arr, pair1_arr)
        pair0_arr, pair1_arr, pair2_arr = await self._compare_vols_second_step(pair0_arr, pair1_arr, pair2_arr)
        arr = np.array([pair0_arr, pair1_arr, pair2_arr], dtype=DTYPE_FLOAT64)

        return arr

    async def _get_profit(self, init_vol, final_vol):
        return final_vol - init_vol - self._bts_default_fee

    async def _basic_algo(self, pair0_arr: np.ndarray, pair1_arr: np.ndarray,
                          pair2_arr: np.ndarray) -> tuple:
        pairs_arr = await self._recalculate_vols_within_fees(pair0_arr, pair1_arr, pair2_arr, self._vol_limit)
        final_vols, pairs_arrs_given_fees = await self._recalculate_vols_given_fees(pairs_arr)
        pairs_arrs_given_fees = await self._fill_prices_with_zero(pairs_arrs_given_fees)

        return final_vols, pairs_arrs_given_fees

    async def _ext_algo(self, arr: np.ndarray, pair0_arr: np.ndarray, pair1_arr: np.ndarray,
                        pair2_arr: np.ndarray) -> np.ndarray or tuple:
        if arr[0][2] >= self._vol_limit:
            return np.delete(arr, np.s_[:])

        new_vol_limit = self._vol_limit - arr[0][2]
        pairs_arr = await self._recalculate_vols_within_fees(pair0_arr, pair1_arr, pair2_arr, new_vol_limit)
        final_vols, pairs_arrs_given_fees = await self._recalculate_vols_given_fees(pairs_arr)
        vols_sum = await self._fill_prices_with_zero(arr + pairs_arrs_given_fees)

        return final_vols, vols_sum

    async def _run_data_through_algo(self) -> tuple:
        len_any_arr = len(self._orders_data[0])
        algo_data = await self._basic_algo(self._orders_data[0][0], self._orders_data[1][0], self._orders_data[2][0])
        profit = await self._get_profit(*algo_data[0])

        for i in range(1, len_any_arr):
            new_algo_data = await self._ext_algo(algo_data[1], self._orders_data[0][i],
                                                 self._orders_data[1][i], self._orders_data[2][i])
            if len(new_algo_data) == 0:
                break

            new_profit = await self._get_profit(*new_algo_data[0])

            if profit > new_profit:
                break

            algo_data = new_algo_data
            profit = new_profit

        if await self._is_profit_valid(profit):
            return await self._prepare_orders_arr(algo_data[1], profit)

        return np.delete(algo_data[1], np.s_[:]), profit
