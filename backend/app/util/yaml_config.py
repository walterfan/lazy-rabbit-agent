import os
import sys

# refer to https://pyyaml.org/wiki/PyYAMLDocumentation
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class YamlConfig:
    def __init__(self, yaml_file):
        self._config_file = yaml_file
        self._config_data = self.read_config()

    def read_config(self):
        f = open(self._config_file, 'r', encoding='UTF-8')
        config_data = load(f, Loader=Loader)
        f.close()
        return config_data

    def get_config_data(self):
        return self._config_data

    def get_config_section(self, section):
        return self._config_data.get(section, {})

    def get_config_item(self, env, category, item):
        return self._config_data.get(env, {}).get(category, {}).get(item)
    
    def __str__(self):
        return dump(self._config_data, Dumper=Dumper)



