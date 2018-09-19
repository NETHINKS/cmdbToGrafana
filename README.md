# Automatically generated Grafana-Dashboards

This script generates dashbaords with panels for each user und object defined in one of the following datasources: cmdb, xml or json.

## Getting Started

Donwload the script-folder, install the software from requirements.txt and configure your settings in grafanaScript/config/scriptconfig.ini
```
[Datasource]
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
protocol: 

[OpenNMS]
user:
password:
;base_url: OpenNMS-COMPANYNAME.com
base_url:
;url_with_protocol: http://OpenNMS-COMPANYNAME.com or https://OpenNMS-COMPANYNAME.com
url_with_protocol:
;open_nms bin directory path 
path_to_send_event:
;protocol: http or https
protocol:

[Grafana]
user:
password:
url:
datasource:
;protocol: http or https
protocol:

[DashbaordTemplates]
dashboard = router_dashboard_template.json
panel = router_panel_template.json
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
				<parameter key="location" value="Network-Connection: LOCATION  || IP: 127.0.0.1" />
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

### Running the Script
You can run the script from the main directory with one of the following commands:
```
python3 -m grafana_script cmdb
python3 -m grafana_script JSON_FILE_NAME.json
python3 -m grafana_script XML_FILE_NAME.xml
```
If everything went well you gonna see something like this on your shell:
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

## To-Do List
1. Better error handling
2. More generated OpenNMS-alarms for problems with the script or the datasources


## Possibilities
1. Template-Generater-Tool -> That way you can just create a dashboard you like to use and convert it via command for use with this script
2. A line for the max. bandwidth in the panels directy taken from one of the datasources
3. A XML/JSON-Generator to tranform one of your XML/JSON files in the format needed in this script
4. Other SNMP Objects (Switches, Server, etc ...)
5. Multi dashboards (for each category)
