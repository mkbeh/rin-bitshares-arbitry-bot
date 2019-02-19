# import json
#
# from .extra import utils, configcreator
#
#
# cfg_creator = configcreator.ConfigCreator()
# cfg = cfg_creator.create_config()
# cfg_data = cfg_creator.get_cfg_data()


# WORK_DIR = cfg.get('DIRS', 'output dir')
# LOG_DIR = cfg.get('DIRS', 'log dir')
# OVERALL_MIN_DAILY_VOLUME = int(cfg.get('MIN_DAILY_VOLUME', 'overall min daily volume'))
# PAIR_MIN_DAILY_VOLUME = int(cfg.get('MIN_DAILY_VOLUME', 'pair min daily volume'))
# VOLS_LIMITS = json.loads(cfg.get('LIMITS', 'volume limits'))
# MIN_PROFIT_LIMITS = json.loads(cfg.get('LIMITS', 'min profit limits'))
# NODE_URI = cfg.get('URI', 'node uri')
# WALLET_URI = cfg.get('URI')
# DATA_UPDATE_TIME = 3                                                    # hours
# ACCOUNT_NAME = 'mkbehforever007'
# TIME_TO_RECONNECT = 350
# WALLET_PWD = '<set_here_u_pwd>'
# ORDERS_DEPTH = 5

# WORK_DIR = utils.get_proj_dir('output')
# LOG_DIR = utils.get_proj_dir('logs')
# OVERALL_MIN_DAILY_VOLUME = 10
# PAIR_MIN_DAILY_VOLUME = 5
# VOLS_LIMITS = {'1.3.0': .5, '1.3.113': .5, '1.3.1570': .5, '1.3.121': .5}
# MIN_PROFIT_LIMITS = {'1.3.0': 0.001, '1.3.113': 0.02, '1.3.1570': 0.000_000_02, '1.3.121': 0.02}
# NODE_URI = 'ws://130.193.42.72:8090/ws'
# WALLET_URI = 'ws://127.0.0.1:8093/ws'
# DATA_UPDATE_TIME = 3                                                    # hours
# ACCOUNT_NAME = 'mkbehforever007'
# TIME_TO_RECONNECT = 350
# WALLET_PWD = '<set_here_u_pwd>'
# ORDERS_DEPTH = 5
