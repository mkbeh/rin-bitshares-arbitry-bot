# -*- coding: utf-8 -*-
from functools import wraps

from libs import utils


def write_data_into_file(file, lock=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            seq = func(*args, **kwargs)

            if lock:
                with lock:
                    utils.write_data_from_seq(file, seq)

            else:
                utils.write_data_from_seq(file, seq)

        return wrapper
    return decorator
