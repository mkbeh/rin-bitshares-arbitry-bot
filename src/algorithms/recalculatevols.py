# -*- coding: utf-8 -*-
import numpy as np


class RecalculateVols:
    def __init__(self, orders_arrs, base_asset_vol):
        self._orders_arrs = orders_arrs
        self._base_asset_vol = base_asset_vol

    async def __call__(self, *args, **kwargs):
        return await self._run()

    @staticmethod
    async def _calc_vols(order_arr, base_asset_vol):
        arr = np.array([
            base_asset_vol, (base_asset_vol / order_arr[0])
        ], dtype=float)

        return arr

    async def _run(self):
        vols = np.array([0., 0.], dtype=float)
        vol_limit = self._base_asset_vol

        for order_arr in self._orders_arrs:
            if vol_limit < order_arr[2]:
                vols += await self._calc_vols(order_arr, vol_limit)
                break

            elif vol_limit > order_arr[2]:
                vols += await self._calc_vols(order_arr, order_arr[2])
                vol_limit -= order_arr[2]

            elif vol_limit == 0:
                break

        return vols
