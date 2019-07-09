"""
Grafana-Script information_converter module
This is the information_converter module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2018 by NETHINKS GmbH, see AUTHORS for more details
"""

import os
import json
import xml.etree.ElementTree as ET
from grafana_script.cmdb import CmdbDatacollection
from grafana_script.opennms_functions import OpennmsFunctions
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()
CMDB = CmdbDatacollection()
ONMS = OpennmsFunctions()


def cmdb_to_dict(objects_by_user):
    """
    Summs up all necessary information in one dictionary
    """

    object_name = CONF.get_value('CMDB', 'object_name')
    foreign_to_id = ONMS.associate_to_id()
    asset_to_user = CMDB.asset_id_to_user_id()

    all_info = []
    for user_id in asset_to_user:
        
        password = CMDB.get_password(asset_to_user[user_id])
        object_lst = []
        
        if password:
            # Create a new dictionary-template for further use
            main_data = {
                "id": "%s" % user_id,
                "password": "%s" % password,
                "object": ""
            }

            for object_id in objects_by_user[user_id]:
               
                # Add Description of Object Location to dictionary
                location = CMDB.get_location(object_id)

                # Add WAN-Interface to disctionary
                interface = CMDB.get_interfaces(object_id)

                nodeid = "%s%s" % (object_name, object_id)
                interface = ONMS.corrected_interface(foreign_to_id, object_id, interface)
                
                hc_check = ONMS.hc_octets_check(foreign_to_id, object_id, interface)

                object_data = {
                    "parameter": {
                        "location": "%s" % location,
                        "nodeid": "%s" % nodeid,
                        "interface": "%s" % interface,
                        "hc_octets": "%s" % hc_check
                    }
                }

                # Only add object with Interfaces
                if interface is not None:
                    object_lst.append(object_data)

                """
                Creates the final Dicionary in the format of 
                {'UserID','Password', Objects:{{'Object location information'}}, 
                'UserID','Password', Objects:{{'Object location information'}}}
                """
                main_data.update({'object': object_lst})
                all_info.append(main_data) 
    return all_info


def json_to_dict(filename):
    """
    Converts the json datasource information into the formation
    needed for further use and removes \xa0 unicode
    JSON:
    [{
        "id": "15972",
        "password": "test1",
        "object": [{
            "id": "869",
            "parameter":
                {
                "location": "Network-Connection: STREET 3, 12345 CITY  || IP: 127.0.0.1",
                "nodeid": "yourcmdb-kdrouter:869",
                "interface": "Et0"
                }
            }
        ]
    }]

    Converted:
    [{'id': '15972', 'password': 'test1', 'object': [{'parameter':
    {'location': 'Network-Connection: STREET 3, 12345 CITY  || IP: 127.0.0.1',
     'nodeid': 'yourcmdb-kdrouter:869', 'interface': 'interfaceSnmp[Et0-7cad7461ea3e]'}}]}]
    """

    foreign_to_id = ONMS.associate_to_id()
    filepath = os.path.abspath('')
    filepath += '/grafana_script/datasource/%s' % filename
    with open(filepath) as json_data:
        all_info = json.load(json_data)
    for ids in all_info:
        objects = ids['object']
        for object_data in objects:
            location = object_data['parameter']['location']
            object_data['parameter']['location'] = location.replace('\xa0', ' ')
            object_id = object_data['parameter']['nodeid'].split(":",1)[1]
            interface = object_data['parameter']['interface']
            interface = ONMS.corrected_interface(foreign_to_id, object_id, interface)
            object_data['parameter']['interface'] = interface
    return all_info


def xml_to_dict(filename):
    """
    Converts the xml datasource information into the formation
    needed for further use and removes \xa0 unicode
    XML:
    <dashboard-hardware>
        <user_id id="15972" password="test1">
            <object id="869">
                    <parameter key="location" value="Network-Connection: STREET 3, 12345 CITY  
                    || IP: 127.0.0.1" />
                    <parameter key="nodeid" value="yourcmdb-kdrouter:869" />
                    <parameter key="interface" value="Et0" />
            </object>
        </user_id>
    </dashboard-hardware>

    Converted:
    [{'id': '15972', 'password': 'test1', 'object': [{'parameter':
    {'location': 'Network-Connection: STREET 3, 12345 CITY  || IP: 127.0.0.1',
     'nodeid': 'yourcmdb-kdrouter:869', 'interface': 'interfaceSnmp[Et0-7cad7461ea3e]'}}]}]
    """

    filepath = os.path.abspath('')
    filepath += '/grafana_script/datasource/%s' % filename
    parsed_xml = ET.parse(filepath)
    all_info = []
    foreign_to_id = ONMS.associate_to_id()
    for user_ids in parsed_xml.findall('user_id'):
        object_lst = []
        user_id = user_ids.get('id')
        password = user_ids.get('password')
        main_data = {
            "id": "%s" % user_id,
            "password": "%s" % password,
            "object": ""
        }
        for objects in user_ids.findall('object'):
            location = {}
            for parameter in objects.findall('parameter'):
                if parameter.get('key') == 'location':
                    location = parameter.get('value').replace('\xa0', ' ')
                elif parameter.get('key') == 'nodeid':
                    nodeid = parameter.get('value')
                elif parameter.get('key') == 'interface':
                    interface = parameter.get('value')
                    object_id = nodeid.split(":",1)[1]
                    interface = ONMS.corrected_interface(foreign_to_id, object_id, interface)
            object_data = {
                "parameter": {
                    "location": "%s" % location,
                    "nodeid": "%s" % nodeid,
                    "interface": "%s" % interface
                }
            }
            object_lst.append(object_data)
        main_data.update({'object': object_lst})
        all_info.append(main_data)
    return all_info
