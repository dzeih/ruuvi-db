from configparser import ConfigParser

_config = ConfigParser()
_config.read('config.ini')

def get_setting(section: str, parameter: str):
    return _config[section][parameter]
