# -*- coding: utf-8
import os
import configparser
import ujson

from . import utils
from .customexceptions import ConfigNotFilled


class ConfigCreator:
    _work_dir = utils.get_dir('rin-bot')
    _cfg_file = os.path.join(_work_dir, 'config.ini')

    _data = (
        {'DIRS': {
            'output dir': utils.dir_exists(
                            os.path.join(_work_dir, 'output')
                          ),
            'log dir': utils.dir_exists(
                            os.path.join(_work_dir, 'logs')
                          )
        }},
        {'MIN_DAILY_VOLUME': {
            'overall min daily volume': '10',  # $ / required non
            'pair min daily volume': '5'       # $ / required int
        }},
        {'LIMITS': {
            'volume limits': ujson.dumps({'1.3.0': .5, '1.3.113': .5, '1.3.1570': .5, '1.3.121': .5}),   # required dict
            'min profit limits': ujson.dumps({'1.3.0': 0.001, '1.3.113': 0.02,                           # required dict
                                             '1.3.1570': 0.000_000_02, '1.3.121': 0.02})
        }},
        {'URI': {
            'node uri': '',
            'wallet uri': '',
            'explorer uri': '',
        }},
        {'ACCOUNT': {
            'account name': '',
            'account id': '',
            'wallet password': '',
        }},
        {'OTHER': {
            'data update time': '1',        # hours / required int
            'time to reconnect': '350',     # secs / required int
            'orders depth': '5'             # required int
        }}
    )

    def _is_empty_fields(self, config):
        config.read(self._cfg_file)

        for el in self._data:
            section, options = tuple(*el.items())

            for option in options.keys():
                if config.get(section, option) == '':
                    return True

    def _create_config(self, config):
        if not os.path.exists(self._cfg_file):
            for el in self._data:
                section, options = tuple(*el.items())
                config.add_section(section)

                for option, value in options.items():
                    config.set(section, option, value)

            with open(self._cfg_file, 'w') as cfg:
                config.write(cfg)

        if self._is_empty_fields(config):
            raise ConfigNotFilled

    def get_cfg_data(self):
        config = configparser.ConfigParser()
        self._create_config(config)
        config.read(self._cfg_file)
        data = {}

        for el in self._data:
            section, options = tuple(*el.items())

            for option in options.keys():
                if section == 'MIN_DAILY_VOLUME' or section == 'OTHER':
                    val = int(config.get(section, option))

                elif section == 'LIMITS':
                    val = ujson.loads(config.get(section, option))

                else:
                    val = config.get(section, option)

                data.update(
                    {option: val}
                )

        return data
