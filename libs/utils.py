# -*- coding: utf-8 -*-
import os

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


def get_dir_file(dir_):
    try:
        return os.listdir(dir_)[0]
    except IndexError:
        return
