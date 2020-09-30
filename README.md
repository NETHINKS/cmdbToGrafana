# Automatically generated Grafana-Dashboards

This script generates dashbaords with panels for each user und object defined in one of the following datasources: DATAGERRY, yourCMDB, XML or JSON.

## Getting Started

Donwload the script-folder, install the software from requirements.txt and configure your settings in grafanaScript/config/scriptconfig.ini
```
[Datasource]
;source: cmdb
source: datagerry

[DATAGERRY]
user: 
password: 
;base_url: REST-DATASOURCE.com
base_url: 
;type_url_part: /REST/EXPORTDJOB/PULL/OBJECTS
type_url_part: 
;login_url_part: /REST/EXPORTDJOB/PULL/USERINFORMATION
login_url_part: 
;object_name: OpenNMS-REQUISITION-NAME:
object_name: 
;protocol: http or https or standard (4000)
protocol: https

[CMDB]
user: 
password: 
;base_url: REST-DATASOURCE.com
base_url: 
;object_url_part: /REST/OBJECTS
object_url_part: 
;login_url_part: /REST/USERINFORMATION
login_url_part: 
;object_name: OpenNMS-REQUISITION-NAME:
object_name: 
;protocol: http or https
protocol: https

[OpenNMS]
user: 
password: 
;base_url: OpenNMS-COMPANYNAME.com
base_url: 
;open_nms bin directory path 
path_to_send_event: /opt/opennms/bin/
;protocol: http or https
protocol: https

[Grafana]
user: 
password: 
url: 
datasource: 
;protocol: http, https or standard (3000)
protocol: https

[DashbaordTemplates]
dashboard: router_dashboard_template.json
panel: router_panel_template.json
```
The dashboard and panel templates are found in grafanaScript/dashboard_templates and can be traded for dashboards or panel settings/templates you like to use.

The following Line is needed in your dashboard template, otherwise feel free to import your own templates or copy and edit the existing ones
```
"tags": ["user_dashboard"],
```

### Prerequisites
```
You need Python 3 to execute the script otherwise you gonna get errors
and you need pip3 to install the software listed in the requirements.txt

OpenNMS
Grafana with Helm Plugin
```

### Installing
```
pip3 install -r requirements.txt
```

### Configure Datasource
There are 2 example files in grafanaScript/datasource one for xml and one for json.
If you want to use a cmdb you need to configure the rest-api paths in scriptconfig.ini

XML:
```
<dashboard-hardware>
  <user_id id="" password="">
    <object>
        <parameter key="location" value="Network-Connection: LOCATION  || IP: 127.0.0.1" />
        <parameter key="nodeid" value="REQUISITION_NAME:OPENNMS_FOREIGEN_ID" />
        <parameter key="interface" value="OPENNMS_SNMP_INTERFACE" />
    </object>
  </user_id>
</dashboard-hardware>
```
JSON:
```
[
  {
    "id": "",
    "password": "",
    "object": [
    {
      "parameter": 
      {
        "location": "Network-Connection: LOCATION || IP: 127.0.0.1",
        "nodeid": "REQUISITION_NAME:OPENNMS_FOREIGEN_ID", 
        "interface": "OPENNMS_SNMP_INTERFACE"
      }
    }
    ]
  }
]

```

## DATAGERRY configuration for use with this script
1. Create two types in DATAGERRY one for users and one type for your devices.
The user type needs at least the following fields: username/user_id and password.
The device type needs the following fields: username/user_id and interface (e.g.: Et0)
Optional fields for the device type are: street, number, postcode, city and management_ip that are used as the heading in your Grafana panels.

2. Create two Exportd pull jobs. 
The source for this job is ExternalSystemGenericPullJson.
One Exportd job is for the username and the user password and one Exportd job is for your devices.
You can add filters in the Exportd job to only export objects that are monitored and selected for a dashboard creation.


## Error reporting for DATAGERRY

There is an example OpenNMS event within the event_example folder for problems in your DATAGERRY configuration. The script executes an OpenNMS event if problems were found.
You can import the event file into your OpenNMS /events folder or just take it as a hint for your own OpenNMS event.


### Running the Script
You can run the script from the main directory with one of the following commands:


```
python3 -m grafana_script datagerry
python3 -m grafana_script cmdb
python3 -m grafana_script JSON_FILE_NAME.json
python3 -m grafana_script XML_FILE_NAME.xml
```

If you configured [Datasource] in the scriptconfig.ini you can execute the script with the following command:
```
./run_module
```

If everything went well you will see this in your terminal:
```
root@grafana:~/cmdbToGrafana# python3 grafanaScript/ cmdb

* Information collected and converted from cmdb
* Old users deleted
* New users created
* Old dashboards deleted
* New dashboards created
* User information collected
* Dashboard information collected
* Permissions updated
------------------------------------------------
* All Done !!!
```

## Authors
* **Patrick Kremser** - *Initial work*

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Possibilities
1. Template-Generater-Tool -> That way you can just create a dashboard you like to use and convert it via command for use with this script
2. A line for the max. bandwidth in the panels directy taken from one of the datasources
3. A XML/JSON-Generator to tranform one of your XML/JSON files in the format needed in this script
4. Other SNMP Objects (Switches, Server, etc ...)
5. Multi dashboards (for each category)

## Presentation
Showcase of the first version from 2018 on YouTube
https://www.youtube.com/watch?v=idrySEOhs2U

The Youtube presentation in *.pdf format can be found here
https://ouce.opennms.eu/img/ouce2018-Patrick_Kremser-Automatically_Generated_Dashboards.pdf
