# -*- coding: utf-8 -*-


"""
Order exceptions.
"""


class OrderExceptions(Exception):
    pass


class OrderNotFilled(OrderExceptions):
    pass


class AuthorizedAsset(OrderExceptions):
    pass


"""
Other exceptions.
"""


class FileDoesNotExist(TypeError):
    pass
