# DNA Center Template Deployment Script

The Python scripts contained in this directory can be used to deploy template configurations to a target device, through DNA Center's Template Programmer APIs.  They will read in configuration details from an input file, parse that configuration into JSON structured data, and then send that JSON data to a DNA Center template, using a single variable.  Once received by the target template, it can loop through the input data and use it to apply configurations to a target device.

## Table of Contents
1. [The Files](#the-files)
2. [Using the "deploy_template.py" Script](#using-the-deploy_templatepy-script)
3. [Using the "template_runner.py" Script](#using-the-template_runnerpy-script)

## The Files

There are two iterations of the Python script located in this directory.  The `deploy_template.py` script is the earliest version and it is designed to read configuration input from a CSV formatted file.  The intended use case was to specify individual switch port configurations in the CSV file, as separate rows, and then send that data to a template which could loop through each row's columns and apply the necessary configuration to each switch port.  This system allows you to configure a large number of switch port interfaces with custom values, such as the `description` field, the `access vlan` or `trunk native vlan`, etc.  

The latest version of this script is named `template_runner.py`, and it has several added features.  

1. Input data can be stored in CSV, TXT or YAML formats (file extensions can be `.csv`, `.txt`, `.yaml`, or `.yml`)
2. Devices and Templates can be referenced by their friendly names, rather than their Universally Unique Identifiers (UUIDs)
3. The script can perform a resulting configuration "preview", which will send the data to DNA Center, simulate the template deployment, and return back the raw text of what the resulting deployed configuration would be.
4. A "verbose" option was added which will print out the raw contents of all API responses from DNA Center, as the script runs.

## Using the "deploy_template.py" Script

This script requires only one external Python package, which needs to be installed using the "Pip" Package Manager - this is the [`requests` package](https://pypi.org/project/requests/), which is used to build HTTP messages to make API calls.  All other functionality is provided using Python v3's built-in packages.

### Command Line Options

You can view the script's Help documentation by executing the following command:

* Mac or Linux: `python3 deploy_template.py --help`
* Windows: `py.exe deploy_template.py --help`

<u>Available Options</u>:

* `--username` or `-u`: The username that will be used to authenticate to your DNA Center server.
* `--password` or `-p`: The password that will be used to authenticate to your DNA Center server 
    * **Note:** You may need to "escape" any special characters by placing a backslash `\` before each character.
* `--dnac_server`: The hostname or IP address of your DNA Center server.
* `--templateId`: The Universally Unique Identifier (UUID) of the target template in DNA Center.  You can make a separate API call to DNA Center to obtain this ID and that ID will never change throughout the life of the template.
* `--deviceId`: The UUID of the target device in DNA Center.  This can be obtained through a separate API call, or from the webpage URL (website address) of the device's "Details" page.
* `--csv_file`: The filename of the input CSV file and, if located in a separate directory, the path to that file.

### Target DNA Center Template

This script can accomodate both Velocity and Jinja formatted templates, and the actual structure of the template is not important.  The only necessary component in a target template is a variable named `csv_data`, which will capture the JSON structured data derived from the input file.  Once that data is stored in the `csv_data` variable, you can loop through it inside the template and gain access to all of the cell values contained in each row of the CSV file.

Here is an example of what the resulting JSON data will look like, based on the following CSV data:

```csv
interface_name,interface_number,description,port_mode,access_vlan,native_vlan
GigabitEthernet,1/0/1,Port 1/0/1 Description,access,10,
GigabitEthernet,1/0/2,Port 1/0/2 Description,trunk,,20
```

```json
[
    {
        "interface_name": "GigabitEthernet",
        "interface_number": "1/0/1",
        "description": "Port 1/0/1 Description",
        "port_mode": "access",
        "access_vlan": "10",
        "native_vlan": "" 
    },
    {
        "interface_name": "GigabitEthernet",
        "interface_number": "1/0/2",
        "description": "Port 1/0/2 Description",
        "port_mode": "trunk",
        "access_vlan": "",
        "native_vlan": "20"
    }
]
```

Here is an example of what the target template might look like, using the Jinja Templating language:

```jinja
{% set csv_import = csv_data %}
{% for item in csv_import %}
interface {{ item.interface_name }} {{ item.interface_number }}
 description {{ item.description }}
 {% if item.port_mode|lower == 'access' %}
 switchport mode access
 switchport access vlan {{ item.access_vlan }}
 {% elif item.port_mode|lower == 'trunk' %}
 switchport mode trunk
 switchport trunk native vlan {{ item.native_vlan }}
 {% else %}
 description {{ item.description }}
 {% endif %}
 no shutdown

{% endfor %}
```

## Using the "template_runner.py" Script

This script requires up to two external Python packages, which need to be installed using the "Pip" Package Manager - the necessary packages depend on which CLI options you choose.  These external packages are

* [`requests` package](https://pypi.org/project/requests/): Used to build HTTP messages to make API calls.
* [`yaml` (PyYAML) package](): Used to read input data from a YAML formatted file, then convert it to JSON.

### Command Line Options

You can view the script's Help documentation by executing the following command:

* Mac or Linux: `python3 template_runner.py --help`
* Windows: `py.exe template_runner.py --help`

<u>Available Options</u>:

* `--username` or `-u`: The username that will be used to authenticate to your DNA Center server.
* `--password` or `-p`: The password that will be used to authenticate to your DNA Center server 
    * **Note:** You may need to "escape" any special characters by placing a backslash `\` before each character.
    * If this option is omitted, the script will prompt the user interactively for their password.  This is also a workaround for passwords with special characters.
* `--dnac_server`: The hostname or IP address of your DNA Center server.
* `--template_project`: The name of the Template Editor Project where the target template exists.
* `--template_name`: The name of the target Template that will be used.
* `--device_name`: The name of the target Device that will be configured with the template.
* `--input_file`: The filename of the input CSV file and, if located in a separate directory, the path to that file.
    * Accepts CSV, TXT and YAML formatted text files.
* `--preview`: Used to simulate the deployment of a template without actually configuring the target device.  The raw configuration output generated by the template will be returned and printed to the CLI.
* `--verbose` or `-v`: Used to print the raw contents of all HTTP responses from DNA Center.  Helpful for troubleshooting or inspecting return data.

### Target DNA Center Template

This script can accomodate both Velocity and Jinja formatted templates, and the actual structure of the template is not important.  The only necessary component in a target template is a variable named `input_data`, which will capture the JSON structured data derived from the input file.  Once that data is stored in the `input_data` variable, you can loop through it inside the template and gain access to all of the attributes stored in each CSV row or YAML element

Here is an example of what the resulting JSON data will look like, based on the following CSV or YAML input data:

<u>CSV:</u>
```csv
interface_name,interface_number,description,port_mode,access_vlan,native_vlan
GigabitEthernet,1/0/1,Port 1/0/1 Description,access,10,
GigabitEthernet,1/0/2,Port 1/0/2 Description,trunk,,20
```

<u>YAML</u>
```yaml
- interface_name: GigabitEthernet
  interface_number: "1/0/1"
  description: "Port 1/0/1 Description"
  port_mode: access
  access_vlan: "10"
  native_vlan: 
- interface_name: GigabitEthernet
  interface_number: "1/0/2"
  description: "Port 1/0/2 Description"
  port_mode: trunk
  access_vlan: 
  native_vlan: "20"
```

<u>JSON Result</u>
```json
[
    {
        "interface_name": "GigabitEthernet",
        "interface_number": "1/0/1",
        "description": "Port 1/0/1 Description",
        "port_mode": "access",
        "access_vlan": "10",
        "native_vlan": "" 
    },
    {
        "interface_name": "GigabitEthernet",
        "interface_number": "1/0/2",
        "description": "Port 1/0/2 Description",
        "port_mode": "trunk",
        "access_vlan": "",
        "native_vlan": "20"
    }
]
```

Here is an example of what the target template might look like, using the Jinja Templating language:

```jinja
{% set data_import = input_data %}
{% for item in data_import %}
interface {{ item.interface_name }} {{ item.interface_number }}
 description {{ item.description }}
 {% if item.port_mode|lower == 'access' %}
 switchport mode access
 switchport access vlan {{ item.access_vlan }}
 {% elif item.port_mode|lower == 'trunk' %}
 switchport mode trunk
 switchport trunk native vlan {{ item.native_vlan }}
 {% else %}
 description {{ item.description }}
 {% endif %}
 no shutdown

{% endfor %}
```

### Using TXT Input Files

When the input file specified is a simple text file, the intended use case is different from a CSV or YAML input file.  Text input files should contain raw snippets of CLI configuration commands (or entire configuration files!).  This is useful for situations where arbitrary custom configuration needs to be applied to a device, and there's no simple way to handle that inside a DNA Center template.

Here is an example of what a TXT input file should contain:

```
vlan 10
 name Data-VLAN-End-User
vlan 600
 name Guest-VLAN

interface Vlan10
 description Data-VLAN-End-User
 ip address 10.10.10.1 255.255.255.0
 ip-helper address 172.16.20.5
 no shutdown

interface GigabitEthernet 1/0/1
  description Port 1/0/1 Description
  switchport mode access
  switchport access vlan 10
  no shutdown
```

In this case, the target template should contain only a single line of code, with a single variable named `input_data`.  Such a template will accept the raw text contents from the file as a "String" variable, and will generate an output that contains these exact lines of configuration commands.  Here is an example of what that template would look like in the Jinja Templating Language:

```jinja
{{ input_data }}
```

The output from the template will look identical to the contents of the TXT input file.