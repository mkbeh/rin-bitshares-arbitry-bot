# -*- coding: utf-8 -*-
from functools import wraps


def write_data_from_seq(file, seq):
    if seq:
        with open(file, 'a') as f:
            for elem in seq:
                f.write(elem + '\n')


def write_data_into_file(file, lock=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            seq = func(*args, **kwargs)

            if lock:
                with lock:
                    write_data_from_seq(file, seq)

            else:
                write_data_from_seq(file, seq)

        return wrapper
    return decorator
