# -*- coding: utf-8 -*-
import json

from .grambitshares import GramBitshares


class Account(GramBitshares):
    def __init__(self, gram_instance):
        super().__init__()
        self.gram = gram_instance

    def create_account(self):
        pass
