# -*- coding: utf-8
# from libs.assetchainsmaker.chainscreator import ChainsCreator
# from libs.assetchainsmaker.assetsparser import AssetsPairsParser

from libs.assetchainsmaker.assetspairsparser import AssetsPairsParser


class Rin:
    @staticmethod
    def start_arbitrage():
        # file_with_chains = ChainsCreator().start_creating_chains()
        # AssetsPairsParser().start_parsing()
        AssetsPairsParser().start_parsing()


if __name__ == '__main__':
    Rin().start_arbitrage()
