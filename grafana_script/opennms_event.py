"""
Grafana-Script opennsm_event module
This is the opennsm_event module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2018 by NETHINKS GmbH, see AUTHORS for more details
"""

import os
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()


def send_event(event_data):
    """
    Generate an OpenNMS event to inform which userIDs from your Datasoruce are incorrect
    """

    event_message = 'The following Datasource Objects got wrong User IDs: %s' % event_data
    path = CONF.get_value('OpenNMS', 'path_to_send_event')
    os.system('%ssend-event.pl uei.opennms.org/default/event localhost -d "%s" -x 4' % (path, event_message))
