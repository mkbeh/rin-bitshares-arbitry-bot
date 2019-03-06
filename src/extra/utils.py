# -*- coding: utf-8 -*-
import os
import re
import logging

from datetime import datetime


def get_today_date():
    return datetime.today().strftime('%d-%m-%Y-%H-%M-%S').zfill(2)


def get_abs_path(name):
    return os.path.abspath(os.path.join(name))


def dir_exists(dir_):
    if not os.path.exists(dir_):
        os.makedirs(dir_)

    return dir_


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


def remove_file(file):
    if file:
        os.remove(file)


def get_dir(work_dir):
    return dir_exists(
        os.path.join(
            os.path.expanduser('~'), work_dir
        )
    )
