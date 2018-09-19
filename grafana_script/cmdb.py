"""
Grafana-Script cmdb module
This is the cmdb module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2018 by NETHINKS GmbH, see AUTHORS for more details
"""

import json
import requests
from grafana_script.opennms_event import send_event
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()


class CmdbDatacollection:
    """
    Functions for cmdb datasource to get all necessary information
    """

    def __init__(self):
        """
        Get CMDB username, password and url for requests
        """

        self.c_user = CONF.get_value('CMDB', 'user')
        self.c_password = CONF.get_value('CMDB', 'password')
        self.c_address = CONF.get_value('CMDB', 'base_url')
        self.c_protocol = CONF.get_value('CMDB', 'protocol')

    def asset_id_to_user_id(self):
        """
        Creates a dictionary in the format {user_id:asset_id}
        that is needed in cmdbToDict
        """

        objects_url = self.c_address + CONF.get_value('CMDB', 'login_url_part')
        access_object = '%s://%s:%s@%s' % (self.c_protocol, self.c_user, self.c_password, objects_url)
        cmdb_data = requests.get(access_object)
        json_cmdb_data = json.loads(cmdb_data.text)
        asset_to_user = {}
        for asset_id in json_cmdb_data:
            objects_url = '%s/rest.php/objects/%s' % (self.c_address, asset_id)
            access = '%s://%s:%s@%s' % (self.c_protocol, self.c_user, self.c_password, objects_url)
            object_data = requests.get(access)
            json_object_data = json.loads(object_data.text)
            user_id = json_object_data['objectFields']['Grafana-Zugangsdaten'][0]['value']
            asset_to_user.update({user_id: asset_id})
        return asset_to_user

    def get_user_objects(self):
        """
        Creates an Dictionary in the following format:
        {'UserID':['ObjectID','ObjectID'], 'UserID':['ObjectID','ObjectID']}
        """

        objects_by_user = {}
        entrylist = {}

        """
        Get all CMDB ObjectIDs an place them in a list
        ['ObjectID','ObjectID', ...]
        """
        objects_url = self.c_address + CONF.get_value('CMDB', 'object_url_part')
        access_object = '%s://%s:%s@%s' % (self.c_protocol, self.c_user, self.c_password, objects_url)
        cmdb_objects = requests.get(access_object).text.strip('[').strip(']\n]').split(',')

        """
        1. Filter if the Object is monitored and active
        2. Add the UserID to the ObjectID
        {'ObjectID':'UserID', 'ObjectID':'UserID', ...}
        """
        for entry in cmdb_objects:
            objects_url = '%s/rest.php/objects/%s' % (self.c_address, entry)
            access = '%s://%s:%s@%s' % (self.c_protocol, self.c_user, self.c_password, objects_url)
            object_data = requests.get(access)
            json_object_data = json.loads(object_data.text)
            # Check if object is active at all
            if json_object_data['status'] == 'N':
                pass
            # Check if object is active in monitoring
            elif json_object_data['objectFields']['Management'][2]['value'] == 'false':
                pass
            # Check if object is active in portal
            elif json_object_data['objectFields']['Kundenportal'][0]['value'] == 'false':
                pass
            else:
                user_id = json_object_data['objectFields']['Kunde'][0]['value']
                entrylist.update({entry: user_id})

        """
        Rearange the Dictionary in the following format: 
        {'UserID':['ObjectID','ObjectID'], 'UserID':['ObjectID','ObjectID']}
        Check if there is a wrong UserID and if the case is true => 
        add the object_id to a list
        """
        event_data = []
        for object_id in entrylist:
            if len(entrylist[object_id]) != 5 and entrylist[object_id].isdigit() is False:
                event_data.append(object_id)
            else:
                if entrylist[object_id] in objects_by_user:
                    objects_by_user[entrylist[object_id]].append(object_id)
                else:
                    objects_by_user.update({entrylist[object_id]: [object_id]})

        """
        If there are IDs in the evenData list send an OpenNMS Event to inform
        """
        if event_data:
            send_event(event_data)
        return objects_by_user

    def get_interfaces(self, object_id):
        """
        Get the WAN-Interface from your cmdb
        """

        cmdb_url = '%s/rest.php/objects/%s' % (self.c_address, object_id)
        cmdb_access = '%s://%s:%s@%s' % (self.c_protocol, self.c_user, self.c_password, cmdb_url)
        cmdb_data = requests.get(cmdb_access)
        json_cmdb_data = json.loads(cmdb_data.text)
        interface = json_cmdb_data['objectFields']['Kundenportal'][1]['value']
        return interface

    def get_password(self, asset_id):
        """
        Get the User Password from the cmdb
        """

        objects_url = '%s/rest.php/objects/%s' % (self.c_address, asset_id)
        access = '%s://%s:%s@%s' % (self.c_protocol, self.c_user, self.c_password, objects_url)
        object_data = requests.get(access)
        json_object_data = json.loads(object_data.text)
        password = json_object_data['objectFields']['Grafana-Zugangsdaten'][1]['value']
        return password

    def get_location(self, object_id):
        """
        Creates a Location String für Dashboard Panel Description:
        {'location': 'Network-Connection: street number postcode city
        || IP:127.0.0.1', 'nodeid': 'Requisition:ForeignID'}
        """

        cmdb_url = '%s/rest.php/objects/%s' % (self.c_address, object_id)
        cmdb_access = '%s://%s:%s@%s' % (self.c_protocol, self.c_user, self.c_password, cmdb_url)
        cmdb_data = requests.get(cmdb_access)
        json_cmdb_data = json.loads(cmdb_data.text)

        street = json_cmdb_data['objectFields']['Standort'][1]['value']
        number = json_cmdb_data['objectFields']['Standort'][2]['value']
        postcode = json_cmdb_data['objectFields']['Standort'][3]['value']
        city = json_cmdb_data['objectFields']['Standort'][4]['value']

        location = 'Network-Connection:'

        if street:
            location = location + ' ' + '%s' % street
        if number:
            location = location + ' ' + '%s' % number + ','
        if postcode:
            location = location + ' ' + '%s' % postcode
        if city:
            location = location + ' ' + '%s' % city

        management_ip = json_cmdb_data['objectFields']['Management'][0]['value']
        location_and_ip = location + ' || IP: ' + management_ip
        return location_and_ip
