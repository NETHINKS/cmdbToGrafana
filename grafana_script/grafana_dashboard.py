"""
Grafana-Script grafana_dashboard module
This is the grafana_dashboard module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2018 by NETHINKS GmbH, see AUTHORS for more details
"""

import os
import json
import requests
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()

def create_dashboard(all_info):
    """
    Creates Dashboards with Panels
    """

    g_protocol = CONF.get_value('Grafana', 'protocol')
    g_user = CONF.get_value('Grafana', 'user')
    g_password = CONF.get_value('Grafana', 'password')
    g_url = CONF.get_value('Grafana', 'url')
    g_datasource = CONF.get_value('Grafana', 'datasource')

    filename_dashboard = CONF.get_value('DashbaordTemplates', 'dashboard')
    filepath = os.path.abspath('')
    filepath += '/grafana_script/dashboard_templates/%s' % filename_dashboard
    with open(filepath) as json_data:
        dashboard = json.load(json_data)

    filename_panel = CONF.get_value('DashbaordTemplates', 'panel')
    filepath = os.path.abspath('')
    filepath += '/grafana_script/dashboard_templates/%s' % filename_panel

    for users in all_info:
        paneldata = []
        panel_id = 1
        grid_pos_y = 0
        user_id = users['id']
        for objects in users['object']:
            with open(filepath) as json_data:
                panel = json.load(json_data)
            location = objects['parameter']['location']
            nodeid = objects['parameter']['nodeid']
            interface = objects['parameter']['interface']
            panel['datasource'] = g_datasource
            panel['gridPos']['y'] = grid_pos_y
            panel['id'] = panel_id
            panel['targets'][0]['nodeId'] = nodeid
            panel['targets'][0]['resourceId'] = interface
            panel['targets'][1]['nodeId'] = nodeid
            panel['targets'][1]['resourceId'] = interface

            hc_octets = objects['parameter']['hc_octets']
            if hc_octets == 'true':
                panel['targets'][0]['attribute'] = 'ifHCInOctets'
                panel['targets'][0]['label'] = 'ifHCInOctets'
                panel['targets'][1]['attribute'] = 'ifHCOutOctets'
                panel['targets'][1]['label'] = 'ifHCOutOctets'
                panel['targets'][2]['expression'] = 'ifHCInOctets*8/(1024*1024)'
                panel['targets'][3]['expression'] = 'ifHCOutOctets*8/(1024*1024)'
            else:
                panel['targets'][0]['attribute'] = 'ifInOctets'
                panel['targets'][0]['label'] = 'ifInOctets'
                panel['targets'][1]['attribute'] = 'ifOutOctets'
                panel['targets'][1]['label'] = 'ifOutOctets'
                panel['targets'][2]['expression'] = 'ifInOctets*8/(1024*1024)'
                panel['targets'][3]['expression'] = 'ifOutOctets*8/(1024*1024)'

            panel['title'] = location
            paneldata.append(panel)
            panel_id += 1
            grid_pos_y += 9

        if g_protocol == 'https':
            port = 443
        elif g_protocol == 'http':
            port = 80
        else:
            port = 3000

        grafana_access = "%s://%s:%s@%s:%s/api/dashboards/db" % (g_protocol, g_user, g_password, g_url, port)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        dashboard['dashboard']['panels'] = paneldata
        dashboard['dashboard']['title'] = "Network Workload - %s" % user_id
        requests.post(grafana_access, data=json.dumps(dashboard), headers=headers, verify=False)
