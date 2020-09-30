"""
Grafana-Script config module
This is the config module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2020 by NETHINKS GmbH, see AUTHORS for more details
"""

import os
from configparser import ConfigParser


class ScriptConfig:
    """
    Get values from your configuration.ini file
    """

    def __init__(self):
        """
        Gives you the Filepath of the configuration file
        for further usage.

        >>> /root/cmdbToGrafana/grafana_script/config/scriptconfig.ini
        """
        self.conf_path = '/grafana_script/config/scriptconfig.ini'
        self.filepath = self.load_filepath()

    def load_filepath(self):
        """
        loading config file path
        :return: str path to config
        """
        return os.path.abspath('') + self.conf_path

    def get_value(self, section, option):
        """
        Get one value from your configuration file

        a = ScriptConfig()
        a.get_value('Datasource','user')

        >>> Grafana
        """

        config = ConfigParser()
        config.read(self.filepath)
        section_option = config.get(section, option)
        return section_option
