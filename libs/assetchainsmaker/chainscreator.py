# # -*- coding: utf-8 -*-
# # TODO optimize the algorithm 'create chains for asset'
# # TODO проверить вот что: попробовать вместо if main[1]==pair[0] в секондари искать по 2м элементам списка
# # TODO некорректно работает алго (см. п.2) , неправильно собираются пары.
from libs.assetchainsmaker.assetspairsparser import AssetsPairsParser
from const import WORK_DIR, LOG_DIR
from libs import utils


class ChainsCreator:
    _main_assets = ['BTS', 'BRIDGE.BTC', 'CNY', 'USD']
    _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'chains'))
    _date = utils.get_today_date()
    _new_file = utils.get_file(WORK_DIR, f'chains-{_date}.lst')

    def __init__(self):
        self._file_with_pairs = AssetsPairsParser().start_parsing()

    def _get_pairs_from_file(self):
        try:
            return utils.clear_each_str_in_seq(utils.read_file(self._file_with_pairs), '\n', ' ')
        except Exception as err:
            raise Exception(err)

    def _create_chains_for_asset(self, asset):
        pass

    def start_creating_chains(self):
        # pairs_lst = self._get_pairs_from_file()
        pass







# from multiprocessing import RLock
#
# from libs.assetchainsmaker.assetspairsparser import AssetsPairsParser
# from const import WORK_DIR
# from libs import utils
# from libs import decorators
#
#
# class ChainsCreator():
#     _main_assets = ['BTS', 'BRIDGE.BTC', 'CNY', 'USD']
#     _lock = RLock()
#     _old_file = utils.get_file(WORK_DIR, utils.get_dir_file(WORK_DIR, 'chains'))
#     _date = utils.get_today_date()
#     _new_file = utils.get_file(WORK_DIR, f'chains-{_date}.lst')
#
#     def __init__(self):
#         self._file_with_pairs = AssetsPairsParser().start_parsing()
#
#     def _get_pairs_from_file(self):
#         try:
#             return utils.clear_each_str_in_seq(utils.read_file(self._file_with_pairs), '\n', ' ')
#         except Exception as err:
#             raise Exception(err)
#
#     @decorators.write_data_into_file(_new_file, _lock)
#     def _create_chains_for_asset(self, asset):
#         pairs = self._get_pairs_from_file()
#         split_pairs = [pair.split(':') for pair in pairs]
#         pairs_with_main_asset = [pair for pair in split_pairs
#                                  if pair[0] == asset]
#
#         pairs_with_secondary_assets = [pair for main_pair in pairs_with_main_asset
#                                        for pair in split_pairs
#                                        if main_pair[1] == pair[0]]
#
#         pairs_with_tertiary_assets = [pair for secondary_pair in pairs_with_secondary_assets
#                                       for pair in split_pairs
#                                       if secondary_pair[1] == pair[0] and pair[1] == asset]
#
#         pairs_with_tertiary_assets = utils.remove_duplicate_lists(pairs_with_tertiary_assets)
#         chains = []
#
#         for main_pair in pairs_with_main_asset:
#             for secondary_pair in pairs_with_secondary_assets:
#                 if main_pair[1] == secondary_pair[0]:
#                     for end_pair in pairs_with_tertiary_assets:
#                         if secondary_pair[1] == end_pair[0]:
#                             chains.append('{}:{},{}:{},{}:{}'.format(*main_pair, *secondary_pair, *end_pair))
#
#         return chains
#
#     def start_creating_chains(self):
#         self._run_in_multiprocessing(self._create_chains_for_asset, self._main_assets)
#         self._compare_files_with_pairs(self._old_file, self._new_file, self._lock)
#
#         return self._new_file
