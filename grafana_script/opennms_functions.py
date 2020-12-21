"""
Grafana-Script functions module
This is the functions module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2020 by NETHINKS GmbH, see AUTHORS for more details
"""

import xml.etree.ElementTree as ET
import requests
from grafana_script.config import ScriptConfig

CONF = ScriptConfig()


class OpennmsFunctions:
    """
    Functions for OpenNMS to get all necessary information
    """
    def __init__(self):
        """
        Get OpenNMS username, password and url for requests
        """
        self.o_user = CONF.get_value('OpenNMS', 'user')
        self.o_password = CONF.get_value('OpenNMS', 'password')
        self.o_url = CONF.get_value('OpenNMS', 'base_url')
        self.o_protocol = CONF.get_value('OpenNMS', 'protocol')

    def associate_to_id(self):
        """
        Creates a dictionary in the format {foreignID:nodeID}
        This is needed for the interface correction since we dont got
        the node id but its needed in the rest call in OpenNMS
        """
        opennms_address = self.o_url + '/opennms/rest/nodes?limit=0'
        opennms_access = '%s://%s:%s@%s' % (self.o_protocol, self.o_user, self.o_password, opennms_address)
        requestdata = requests.get(opennms_access, verify=False).text
        nodes_xml = ET.fromstring(requestdata.encode('utf-8'))
        nodes = nodes_xml.findall('node')

        foreign_to_id = {}
        for entry in nodes:
            foreign_to_id.update({entry.get('foreignId'): entry.get('id')})
        return foreign_to_id

    def corrected_interface(self, foreign_to_id, object_id, interface):
        """
        In the datasource you only write something like Fa0, Gi0, etc...
        for your Interface. This functions takes it and checks for the right
        interface needed in Grafana :
        Gi0/0/0 => interfaceSnmp[Gi0_0_0-70f35a7135d1]
        """
        opennms_node_id = foreign_to_id[str(object_id)]

        resourceid = ''

        opennms_address = self.o_url + '/opennms/rest/nodes/%s/snmpinterfaces?limit=0' % opennms_node_id
        access = '%s://%s:%s@%s' % (self.o_protocol, self.o_user, self.o_password, opennms_address)
        nodes = requests.get(access, verify=False).text
        nodes_xml = ET.fromstring(nodes.encode('utf-8'))
        all_interfaces = nodes_xml.findall('snmpInterface')
        if nodes_xml.get('totalCount') != '0':
            for data_entry in all_interfaces:
                interfaces = data_entry.find('ifName').text
                if interfaces == interface:
                    try:
                        phys_addr = data_entry.find('physAddr').text
                        interface = interface.replace('/', '_').replace('.', '_')
                        resourceid = 'interfaceSnmp' + '[' + '%s' % interface + '-' + phys_addr + ']'
                    except AttributeError:
                        resourceid = 'interfaceSnmp' + '[' + '%s' % interface + ']'
        return resourceid

    def corrected_interface_from_resources(self, foreign_to_id, object_id, interface):
        """
        In the datasource you only write something like Fa0, Gi0, etc...
        for your Interface. This functions takes it and checks for the right
        interface needed in Grafana :
        Gi0/0/0 => interfaceSnmp[Gi0_0_0-70f35a7135d1]
        """
        opennms_node_id = foreign_to_id[str(object_id)]

        resourceid = ''

        opennms_address = self.o_url + '/opennms/rest/resources/fornode/%s' % opennms_node_id
        access = '%s://%s:%s@%s' % (self.o_protocol, self.o_user, self.o_password, opennms_address)
        resources = requests.get(access, verify=False).text
        resources_xml = ET.fromstring(resources.encode('utf-8'))

        for children in resources_xml: 
            if children.attrib: 
                for resource in children:
                    if 'SNMP Interface Data' in resource.attrib.values():
                        interface_corr = interface.replace('/', '_').replace('.', '_') + '-'
                        if resource.attrib['name'].startswith(interface_corr) or resource.attrib['name'] == interface:
                            resourceid = 'interfaceSnmp' + '[' + '%s' % resource.attrib['name'] + ']'
        return resourceid

    def hc_octets_check(self, foreign_to_id, object_id, interface):
        """
        Check if the resouce has ifHcInOctets or only provides ifInOctets
        """
        opennms_node_id = foreign_to_id[str(object_id)]
        opennms_address = self.o_url + '/opennms/rest/measurements/node[%s].%s/ifHCInOctets?&aggregation=AVERAGE'%(opennms_node_id, interface)
        access = '%s://%s:%s@%s' % (self.o_protocol, self.o_user, self.o_password, opennms_address)
        response = requests.get(access)
        hc_octets_available = ''
        if response.status_code == 200:
            hc_octets_available = 'true'
        else:
            hc_octets_available = 'false'
        return hc_octets_available
