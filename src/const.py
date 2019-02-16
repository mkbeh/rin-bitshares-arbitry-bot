from .extra import utils

WORK_DIR = utils.get_proj_dir('output')
LOG_DIR = utils.get_proj_dir('logs')
OVERALL_MIN_DAILY_VOLUME = 10
PAIR_MIN_DAILY_VOLUME = 5
VOLS_LIMITS = {'1.3.0': .5, '1.3.113': .5, '1.3.1570': .5, '1.3.121': .5}
MIN_PROFIT_LIMITS = {'1.3.0': 0.001, '1.3.113': 0.02, '1.3.1570': 0.000_000_02, '1.3.121': 0.02}
NODE_URI = 'ws://130.193.42.72:8090/ws'
WALLET_URI = 'ws://127.0.0.1:8093/ws'
DATA_UPDATE_TIME = 3                                                    # hours
ACCOUNT_NAME = 'mkbehforever007'
TIME_TO_RECONNECT = 350
