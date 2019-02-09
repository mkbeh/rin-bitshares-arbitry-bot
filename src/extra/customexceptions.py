# -*- coding: utf-8 -*-


class OrderExceptions(Exception):
    pass


class OrderNotFilled(OrderExceptions):
    pass


class AuthorizedAsset(OrderExceptions):
    pass


class MaxRetriesOrderFilledExceeded(OrderExceptions):
    pass
