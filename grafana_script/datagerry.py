"""
Grafana-Script DATAGERRY module
This is the DATAGERRY module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2020 by NETHINKS GmbH, see AUTHORS for more details
"""

import os
import json
import requests
from grafana_script.opennms_event import send_event
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()


class DATAGERRY_Datacollection:
    """
    Functions for DATAGERRY datasource to get all necessary information
    """
    def __init__(self):
        """
        Get DATAGERRY username, password and url for requests
        """
        self.dg_user = CONF.get_value('DATAGERRY', 'user')
        self.dg_password = CONF.get_value('DATAGERRY', 'password')
        self.dg_address = CONF.get_value('DATAGERRY', 'base_url')
        self.dg_protocol = CONF.get_value('DATAGERRY', 'protocol')

    def get_user_data(self):
        """
        Get all user data from DATAGERRY export
        """
        users_url = self.dg_address + CONF.get_value('DATAGERRY', 'login_url_part')
        access_users = '%s://%s:%s@%s' % (self.dg_protocol, self.dg_user, self.dg_password, users_url)
        datagerry_users = requests.get(access_users, verify=False).json()
        return datagerry_users

    def get_object_data(self):
        """
        Get all object data from DATAGERRY export
        """
        objects_url = self.dg_address + CONF.get_value('DATAGERRY', 'type_url_part')
        access_type_id = '%s://%s:%s@%s' % (self.dg_protocol, self.dg_user, self.dg_password, objects_url)
        datagerry_objects = requests.get(access_type_id, verify=False).json()
        return datagerry_objects

    def get_user_objects(self):
        """
        Creates an Dictionary in the following format:
        {'UserID':['ObjectID','ObjectID'], 'UserID':['ObjectID','ObjectID']}
        """
        objects_by_user = {}
        entrylist = {}

        """
        Get all DATAGERRY ObjectIDs an place them in a list
        ['ObjectID','ObjectID', ...]
        """
        datagerry_objects = DATAGERRY_Datacollection.get_object_data(self)

        for entry in datagerry_objects:
            user_id = entry['variables']['User_ID']
            entrylist.update({entry['object_id']: user_id})

        """
        Rearange the Dictionary in the following format: 
        {'UserID':['ObjectID','ObjectID'], 'UserID':['ObjectID','ObjectID']}
        """
        for object_id in entrylist:
            if len(entrylist[object_id]) == 5 and entrylist[object_id].isdigit() is True:
                if entrylist[object_id] in objects_by_user:
                    objects_by_user[entrylist[object_id]].append(object_id)
                else:
                    objects_by_user.update({entrylist[object_id]:[object_id]})
        return objects_by_user

    def get_interfaces(self, object_id, dg_objects):
        """
        Get the WAN-Interface from your DATAGERRY
        """
        interface = [item['variables']['Interface'] for item in dg_objects if item['object_id'] == object_id][0].lstrip()
        return interface

    def get_password(self, user_id, dg_users):
        """
        Get the User Password from the DATAGERRY
        """
        all_passwords = dg_users
        password = [item['variables']['Password'] for item in all_passwords if item['variables']['User_ID'] == user_id]
        if password:
            return password[0]

    def get_location(self, object_id, dg_objects):
        """
        Creates a Location String für Dashboard Panel Description:
        {'location': 'Network-Connection: street number postcode city
        || IP:127.0.0.1', 'nodeid': 'Requisition:ForeignID'}
        """
        location = 'Network-Connection:'
        street = [item['variables']['Street'] for item in dg_objects if item['object_id'] == object_id][0]
        number = [item['variables']['Number'] for item in dg_objects if item['object_id'] == object_id][0]
        postcode = [item['variables']['Postcode'] for item in dg_objects if item['object_id'] == object_id][0]
        city = [item['variables']['City'] for item in dg_objects if item['object_id'] == object_id][0]
        
        if street:
            location = location + ' ' + '%s' % street
        if number:
            location = location + ' ' + '%s' % number + ','
        if postcode:
            location = location + ' ' + '%s' % postcode
        if city:
            location = location + ' ' + '%s' % city
        management_ip = [item['variables']['IP'] for item in dg_objects if item['object_id'] == object_id][0]
        location_and_ip = location + ' || IP: ' + management_ip
        return location_and_ip
