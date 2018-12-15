# -*- coding: utf-8
from libs.assetchainsmaker.chainscreator import ChainsCreator


class Rin:
    @staticmethod
    def start_arbitrage():
        file_with_chains = ChainsCreator().start_creating_chains()


if __name__ == '__main__':
    Rin().start_arbitrage()
