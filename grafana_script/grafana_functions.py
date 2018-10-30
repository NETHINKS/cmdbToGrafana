"""
Grafana-Script grafana_functions module
This is the grafana_functions module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2018 by NETHINKS GmbH, see AUTHORS for more details
"""

import json
import requests
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()


class GrafanaFunctions:
    """
    Functions for Grafana to create users and dashboards
    """

    def __init__(self):
        """
        Get Grafana username, password and url for requests
        """
        self.g_user = CONF.get_value('Grafana', 'user')
        self.g_password = CONF.get_value('Grafana', 'password')
        self.g_url = CONF.get_value('Grafana', 'url')
        self.g_protocol = CONF.get_value('Grafana', 'protocol')
        if self.g_protocol == 'https':
            self.port = 443
        else:
            self.port = 80

    def create_users(self, all_info):
        """
        Creates all users found in the datasource with their configured password
        """

        for user_id in all_info:
            password = user_id['password']
            grafana_link = "%s://%s:%s@%s:%s/api/admin/users"
            grafana_access = grafana_link % (self.g_protocol, self.g_user, self.g_password, self.g_url, self.port)
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            data = {
                "name": "%s" % user_id['id'],
                "login": "%s" % user_id['id'],
                "password": "%s" % password,
                "role": "Viewer"
            }
            requests.post(grafana_access, data=json.dumps(data), headers=headers, verify=False)

    def get_users(self):
        """
        Get all created grafana users and their ids for later use.
        In updateDashboardPermissions the user id is needed in combination
        with the dashboard id from getDashboards to give the dashboard user
        specified access
        """
        # https://admin:(Fg<Se{N7K<sADBt@grafana.nethinks.com:443/api/users
        grafana_link = "%s://%s:%s@%s:%s/api/users"
        grafana_access = grafana_link % (self.g_protocol, self.g_user, self.g_password, self.g_url, self.port)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        request_data = requests.get(grafana_access, headers=headers, verify=False)
        json_data = json.loads(request_data.text)
        users = {}
        for entry in json_data:
            if entry['name'] != '':  # Admin User = ''
                users.update({entry['id']: entry['name']})
        return users

    def get_dashboards(self):
        """
        Get all created dashboards titles and their ids for later use.
        In updateDashboardPermissions the dashboard id is needed in combination
        with the user id from getUsers to give the dashboard user
        specified access.
        The title is needed cause it includes the user id which is the name from
        getUsers
        """

        grafana_link = "%s://%s:%s@%s:%s/api/search?tag=user_dashboard"
        grafana_access = grafana_link % (self.g_protocol, self.g_user, self.g_password, self.g_url, self.port)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        request_data = requests.get(grafana_access, headers=headers, verify=False)
        json_data = json.loads(request_data.text)
        dashboards = {}
        for entry in json_data:
            dashboards.update({entry['id']: entry['title']})
        return dashboards

    def update_dashboard_permissions(self, users, dashboards):
        """
        Changes the dashboarpermissons from all to user specified
        """

        for dashboard_id, dashboard_title in dashboards.items():
            for grafana_id, user_id in users.items():
                if user_id in dashboard_title:
                    grafana_link = "%s://%s:%s@%s:%s/api/dashboards/id/%s/permissions"
                    grafana_access = grafana_link % (
                    self.g_protocol, self.g_user, self.g_password, self.g_url, self.port, dashboard_id)
                    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                    data = {
                        "items": [
                            {
                                "userId": grafana_id,
                                "permission": 1
                            }
                        ]
                    }
                    requests.post(grafana_access, data=json.dumps(data), headers=headers, verify=False)

    def delete_users(self):
        """
        Deletes all Users
        In case the users changed their names or passwords in Grafana
        Get all user id's and then delete the users
        """
        grafana_link = "%s://%s:%s@%s:%s/api/users"
        grafana_access = grafana_link % (self.g_protocol, self.g_user, self.g_password, self.g_url, self.port)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        request_data = requests.get(grafana_access, headers=headers, verify=False)
        json_data = json.loads(request_data.text)
        for entry in json_data:
            if entry['name'] != '':  # Admin User = ''
                user_id = entry['id']
                grafana_link = "%s://%s:%s@%s:%s/api/admin/users/%s"
                grafana_access = grafana_link % (self.g_protocol, self.g_user, self.g_password, self.g_url, self.port, user_id)
                headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
                requests.delete(grafana_access, headers=headers, verify=False)

    def delete_dashboards(self):
        """
        Deletes all Dashboards
        Instead of updating the dashboards they get deleted
        and new ones get created
        Get all dashboard uid's and then delete the dashboards
        """

        grafana_link = "%s://%s:%s@%s:%s/api/search?tag=user_dashboard"
        grafana_access = grafana_link % (self.g_protocol, self.g_user, self.g_password, self.g_url, self.port)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        request_data = requests.get(grafana_access, headers=headers, verify=False)
        json_data = json.loads(request_data.text)
        for entry in json_data:
            uid = entry['uid']
            grafana_link = "%s://%s:%s@%s:%s/api/dashboards/uid/%s"
            grafana_access = grafana_link % (self.g_protocol, self.g_user, self.g_password, self.g_url, self.port, uid)
            headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            requests.delete(grafana_access, headers=headers, verify=False)
