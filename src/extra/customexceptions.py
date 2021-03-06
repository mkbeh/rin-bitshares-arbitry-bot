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


class EmptyOrdersList(OrderExceptions):
    pass


class UnknownOrderException(OrderExceptions):
    pass


"""
Other exceptions.
"""


class WalletIsLocked(Exception):
    pass


class ConfigNotFilled(Exception):
    def __init__(self):
        Exception.__init__(self, 'The configuration file is not filled. Fill out the configuration file.')
