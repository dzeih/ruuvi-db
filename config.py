from configparser import ConfigParser
import pathlib

path_prefix = pathlib.Path(__file__).parent.absolute()
_config = ConfigParser()
_config.read(f'{path_prefix}/config.ini')


def get_setting(section: str, parameter: str):
    return _config[section][parameter]
