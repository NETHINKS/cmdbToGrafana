#!/usr/bin/python3
"""
Run script 
:license: MIT, see LICENSE for more details
:copyright: (c) 2020 by NETHINKS GmbH, see AUTHORS for more details
"""

import os
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()

source = CONF.get_value('Datasource', 'source')
path = os.path.abspath('')
os.chdir(path)
os.system("python3 -m grafana_script %s"%source)