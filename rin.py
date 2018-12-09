# -*- coding: utf-8
from libs import utils
from const import WORK_DIR

from libs.assetchainsmaker.chainscreator import ChainsCreator


class Rin:
    @staticmethod
    def start_arbitrage():
        utils.dir_exists(WORK_DIR)


if __name__ == '__main__':
    Rin().start_arbitrage()
    ChainsCreator().start_creating_chains()
