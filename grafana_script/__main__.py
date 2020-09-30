"""
Grafana-Script main module
This is the main module of Grafana-Script
:license: MIT, see LICENSE for more details
:copyright: (c) 2020 by NETHINKS GmbH, see AUTHORS for more details
"""

from __future__ import print_function
import sys
import urllib3
from grafana_script.cmdb import CmdbDatacollection
from grafana_script.datagerry import DATAGERRY_Datacollection
from grafana_script.information_converter import cmdb_to_dict, dg_to_dict, json_to_dict, xml_to_dict
from grafana_script.grafana_dashboard import create_dashboard
from grafana_script.grafana_functions import GrafanaFunctions

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CMDB = CmdbDatacollection()
DG   = DATAGERRY_Datacollection()
GF = GrafanaFunctions()


def main():
    """
    All functions get started from here and the
    results gonne be used for the following functions
    """
    datasourceoption = sys.argv[1:2][0]

    if 'cmdb' in datasourceoption:
        objects_by_user = CMDB.get_user_objects()
        all_info = cmdb_to_dict(objects_by_user)

    elif 'datagerry' in datasourceoption:
        objects_by_user = DG.get_user_objects()
        all_info = dg_to_dict(objects_by_user)

    elif 'xml' in datasourceoption:
        all_info = xml_to_dict(datasourceoption)

    elif 'json' in datasourceoption:
        all_info = json_to_dict(datasourceoption)

    else:
        print('Wrong Datasource Number in scriptconfig.ini')

    print('')
    print('* Information collected and converted from %s' % datasourceoption)
    GF.delete_users()
    print('* Old users deleted')
    GF.create_users(all_info)
    print('* New users created')
    GF.delete_dashboards()
    print('* Old dashboards deleted')
    create_dashboard(all_info)
    print('* New dashboards created')
    users = GF.get_users()
    print('* User information collected')
    dashboards = GF.get_dashboards()
    print('* Dashboard information collected')
    GF.update_dashboard_permissions(users, dashboards)
    print('* Permissions updated')
    print('------------------------------------------------')
    print('* All Done !!!')
    print('')

if __name__ == "__main__":
    main()
