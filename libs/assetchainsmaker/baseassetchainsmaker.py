# -*- coding: utf-8 -*-
import os

from multiprocessing import Process
from libs import utils


class BaseAssetChainsMaker:

    @staticmethod
    def _run_in_multiprocessing(func, seq1, seq2=None):
        if seq2:
            processes = [Process(target=func, args=(elem1, elem2)) for elem1, elem2 in zip(seq1, seq2)]
        else:
            processes = [Process(target=func, args=(elem,)) for elem in seq1]

        [process.start() for process in processes]
        [process.join() for process in processes]

    @staticmethod
    def _compare_files_with_pairs(old, new, lock=None):
        if old:
            old_data_set = set()
            new_data_set = set()
            set_lst = [old_data_set, new_data_set]
            files = [old, new]

            for i, data_set in enumerate(set_lst):
                with open(files[i], 'r') as f:
                    [data_set.add(line.replace('\n', '').strip()) for line in f]

            diff = old_data_set.difference(new_data_set)
            os.remove(old)
            utils.write_data_into_file(new, diff, lock)
