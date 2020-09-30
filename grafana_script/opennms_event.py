"""
Grafana-Script opennms_event module
This is the opennms_event module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2020 by NETHINKS GmbH, see AUTHORS for more details
"""

import os
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()


def send_event(user_set_wrong_errors, no_password, user_id_error, interface_errors):
    """
    Generate an OpenNMS event to inform which userIDs from your Datasoruce are incorrect
    """
    path = CONF.get_value('OpenNMS', 'path_to_send_event')
    os.system('%ssend-event.pl uei.opennms.org/cmdb/errors localhost -p "Users %s" -p "Passwords %s" -p "Objects %s" -p "Interfaces %s"'\
    	%(path, user_set_wrong_errors, no_password, user_id_error, interface_errors))
