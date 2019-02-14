# -*- coding: utf-8 -*-


class ReceivedDifferentOrdersAmount(ValueError):
    pass


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
