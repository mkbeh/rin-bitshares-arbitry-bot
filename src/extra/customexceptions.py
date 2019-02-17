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


"""
Other exceptions.
"""


class WalletIsLocked(Exception):
    pass
