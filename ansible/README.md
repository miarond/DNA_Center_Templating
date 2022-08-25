# Deploy a Template from CSV Using Ansible

This project contains an Ansible Playbook which can be used to deploy a DNA Center template to a target device by reading in the parameter data from a CSV file.  This Playbook functions the same way as the Python script in this repository:

  1. Read data from a CSV file.
  2. Parse CSV data into a List (a.k.a. Array) of Dictionary objects - one Dictionary per CSV row, with keys for each column header.
  3. Send the resulting List object as the value for a variable named `csv_data` in a Jinja template.
  4. The Jinja template iterates through the List object.
  5. The Playbook checks the status of the Deployment ID "task" and ends when the status is `SUCCESS` or `FAILURE`.

## Preparing Your Environment

To prepare for using this Ansible Playbook, you will need to install the following prerequisite modules using "Pip" (the Python package manager):

  * `ansible==6.3.0`
  * `dnacentersdk==2.5.4`

You can do this by running the command `pip3 install -r requirements.txt` (using the requirements text file located in the root of this repository), or by manually installing the packages with the command `pip3 install ansible dnacentersdk` (this will install the latest versions).

Next, you will need to update the `hosts` and `credentials.yml` files with information specific to your DNA Center appliance.  The hosts file will contain a group name of `dnac_servers` and the IP address or hostname of your DNA Center server:

```
[dnac_servers]
sandboxdnac.cisco.com
```

The `credentials.yml` file will contain log in information about your DNA Center server:

```
---
dnac_host: sandboxdnac.cisco.com
dnac_port: 443  # optional, defaults to 443
dnac_username: admin
dnac_password: <password>
dnac_version: 2.2.3.3  # optional, defaults to 2.2.3.3. See the Compatibility matrix
dnac_verify: False  # optional, defaults to True
dnac_debug: False  # optional, defaults to False
```

## Using This Playbook

There are two options for utilizing this Playbook using the `ansible-playbook` command line program.  

<u>**Option 1:**</u>

Specify the Playbook variable values as "Extra Variables" in the CLI command, using the `-e` option:

```bash
ansible-playbook -i hosts playbook_deploy_template_from_csv.yml -e "csv_file=port_config.csv forcePush=true templateId=<template_uuid> deviceId=<device_uuid>"
```

<u>**Option 2:**</u>

Edit the `myvars.yml` file and set the variable values inside the file:

```yaml
---
forcePush: true
templateId: <template_id>
deviceId: <device_id>
```

Additionally, you will need to uncomment line number 24 in the Playbook file, in order to import the `myvars.yml` file as one of the Variable Files referenced by the Playbook.

<link to code snippet>

```bash
ansible-playbook -i hosts playbook_deploy_template_from_csv.yml -e "csv_file=port_config.csv"
```

## Example CSV Format

```
int_name,description,access_vlan_id,voice_vlan_id
GigabitEthernet1/1/3,1/1/3 Access Port,10,100
GigabitEthernet1/1/4,1/1/4 Blackhole Port,999,
```

## Example Jinja Template

The deployed Jinja template should accept a single input variable with the name `csv_data`, and the value passed to this variable will be the List of Dictionaries that contains the contents of the CSV file.

The Jinja template should include a `{% for ... %}` loop which iterates through this List object.  For each iteration of the loop, the template will have access to the Dictionary stored at that index inside the List.  At this point, the template can access the keys and values inside that Dictionary, using the "." dot notation.  For example:  `item.int_name` or `item.description`.

```jinja
{% set csv_import = csv_data %}
{% for item in csv_import %}
interface {{ item.int_name }}
 description {{ item.description }}
 switchport mode access
 switchport access vlan {{ item.access_vlan_id }}
 {% if item.voice_vlan_id != '' %}
 switchport voice vlan {{ item.voice_vlan_id }}
 {% endif %}
 no shutdown
{% endfor %}
```

### Example Ansible JSON Format of CSV Data

```json
{
    "csv_data": {
        "changed": false,
        "dict": {},
        "failed": false,
        "list": [
            {
                "access_vlan_id": "10",
                "description": "1/1/3 Access Port",
                "int_name": "GigabitEthernet1/1/3",
                "voice_vlan_id": "100"
            },
            {
                "access_vlan_id": "999",
                "description": "1/1/4 Blackhole Port",
                "int_name": "GigabitEthernet1/1/4",
                "voice_vlan_id": ""
            }
        ]
    }
}
```