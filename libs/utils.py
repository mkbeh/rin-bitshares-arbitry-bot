# -*- coding: utf-8 -*-
import os
import sys
import re

from datetime import datetime


def get_today_date():
    return datetime.today().strftime('%d-%m-%Y-%H-%M-%S').zfill(2)


def get_abs_path(name):
    return os.path.abspath(os.path.join(name))


def dir_exists(dir_):
    if not os.path.exists(dir_):
        os.makedirs(dir_)

    return dir_


def file_exists(dir_, file):
    dir_ = get_abs_path(dir_)
    file_ = os.path.join(dir_, file)

    if os.path.exists(file):
        return file_


def get_file(dir_, file):
    dir_ = get_abs_path(dir_)

    try:
        return os.path.join(dir_, file)
    except TypeError:
        return


def get_dir_file(dir_, regex):
    files = os.listdir(dir_)
    pattern = re.compile(fr'^{regex}-')

    for file in files:
        try:
            re.search(pattern, file).group()
            return file
        except AttributeError:
            pass


def get_proj_dir(cwd=''):
    return os.path.join(os.path.dirname(sys.modules['__main__'].__file__), cwd)


def read_file(file):
    with open(file, 'r') as f:
        return [line for line in f]


def clear_each_str_in_seq(seq, *args):
    """
    :param seq:
    :param args: substr for replace like \n, whitespace, etc.
    :return:
    """
    cleared_data = None

    for arg in args:
        cleared_data = list(map(lambda x: x.replace(arg, '').strip(), seq))

    return cleared_data


def remove_duplicate_lists(seq, convert_to_lst=True):
    set_ = set(tuple(x) for x in seq)

    return [list(x) for x in set_] if convert_to_lst else set_


def write_data_from_seq(file, seq):
    if seq:
        with open(file, 'a') as f:
            for elem in seq:
                f.write(elem + '\n')


def write_data_into_file(file, seq, lock=None):
    if lock:
        with lock:
            write_data_from_seq(file, seq)

    else:
        write_data_from_seq(file, seq)


def remove_file(file):
    if file:
        os.remove(file)


def write_data(data, file):
    with open(file, 'a') as f:
        f.write(f'{data}\n')
