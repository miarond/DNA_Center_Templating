[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/miarond/DNA_Center_Templating)

:star2: [Check out Cisco's Catalyst Center IaC Ansible Project!](https://github.com/cisco-en-programmability/catalyst-center-ansible-iac/tree/main/workflows/device_templates)

# DNA_Center_Templating
A repository of resources for learning how to use templates in Cisco's DNA Center product.

This repository contains a DNA Center Template "Project" in the `templates` subdirectory, which can be imported directly into DNA Center.  

To download this JSON file individually (if you are not cloning this repository), right-click on [this link](https://github.com/miarond/DNA_Center_Templating/raw/main/templates/Jinja_Template_Demos_Project.json) and choose **"Save Link As..."**.

To import this JSON-formatted project file, follow these steps:

1. Navigate in your DNA Center appliance to **Menu --> Tools --> Template Editor**.
2. Click on the blue **"+"** button above the Tree Hierachy window on the left side of the screen.
3. Click on the **Import Project(s)** option from the dropdown menu.)
    1. <img src="/assets/add_button.png" alt="Add button" width="150" />
4. In the dialog box that pops up, select the file to import and then click the **Import** button.
    1. <img src="/assets/import_window.png" alt="Import window" width="300" />

## Template Examples

#### Jinja Syntax Demo

This template is useful when run in the Template Simulator tab in DNA Center's Template Editor page.  You may choose an option from the dropdown `syntax_demo` menu and then run the simulation.  The output will show both the content of the Jinja template and the resulting output of the template processing.

#### Jinja System Bind Variable Demo & All System Bind Attributes Demo

These two templates can be run through the Template Simulator, or via the Template Preview API.  

The `Jinja_System_Bind_Variable_Demo` template will display a subset of System Bind Variable names and values for the `__device` and `__interface` objects.

The `All System Bind Attributes Demo` will display every Attribute and Value for the System Bind Variables `__device` and `__interface`.  This template can easily be extended to print the Attributes and Values for any System Bind Variable available within DNA Center.

#### Jinja CSV Import Demo

This template is intended to be used in combination with the `deploy_template.py` script and `port_config.csv` CSV file, located in the `scripts` subdirectory in this repository.  The template accepts a single input variable which is intended to be a Python List containing Dictionaries for each row of the input CSV file.  The keys in these Dictionaries are generated from the column headers in the CSV file, and the values are the cell contents for each column.  Each row of the CSV file is converted to a separate Dictionary.

#### Jinja Port Reset CSV Demo

This template is very similar to the `Jinja_CSV_Import_Demo` template however, it performs a port configuration reset (i.e. `default interface XXXX`) on a range of ports defined in the `port_reset.csv` CSV file, located in the `scripts` subdirectory.  The CSV file columns specify the port name, module number, slot number, starting port, and ending port which are used to loop through those interfaces and perform the port reset.

#### Jinja CIDR String Slicing Demo

This template demonstrates using Jinja Filters and Python functions to slice a String input.  The template expects a CIDR-formatted IP and Subnet string, which will be split into its component parts and various logic operations will be preformed on it.  It demonstrates how to build a BGP Network Statement out of the input, using the sliced string components.

This template is best utilized in the Template Simulator in DNA Center.

#### Jinja Admin Down Port Demo

This template demonstrates utilizing the System Bind Variables and Jinja conditional logic to identify ports which are "administratively disabled", and then utilize an imported Jinja Macro to apply a reusable port configuration to those ports.

#### Jinja GUI Interface Picker Demo

This template demonstrates DNA Center's Web UI capabilities for setting up advanced functionality on a template variable.  This template will only work properly when used through the Web UI or the Template Simulator.  The template includes a variable that is configured as a multi-select box, and is bound to the `__interface` System Bind Variable, using special filter rules to control the output for the pick list.  The template allows you to individually select ports from a dropdown menu and then execute the template logic on *only* those ports.

The settings for this template variable can be viewed in the Template Editor interface, on the Form Editor tab.

## Script Examples

#### Deploy Template Python Script

The `deploy_template.py` script located in the `scripts` subdirectory is a very simple example script which can be used to read data from an input CSV file, and send that data as variables to a DNA Center template using the Configuration Templates APIs.

The script is designed to collect all input from any CSV file that is passed to it, and organize the content into a Python List object containing Python Dictionaries for each row of the CSV file.  The resulting data format will look like this:

```json
[
    {
        "column_header_1": "row_1_column_1_value",
        "column_header_2": "row_1_column_2_value"
    },
    {
        "column_header_1": "row_2_column_1_value",
        "column_header_2": "row_2_column_2_value"
    },
    {
        "column_header_1": "row_3_column_1_value",
        "column_header_2": "row_3_column_2_value"
    }
]
```

When this object is passed to a Jinja Template, it can be looped through using a simple For Loop mechanism:

```jinja
{% for item in csv_data %}
column_header_1 = {{ item.column_header_1 }}
column_header_2 = {{ item.column_header_2 }}
{% endfor %}
```
And the resulting output:

```
column_header_1 = row_1_column_1_value
column_header_2 = row_1_column_2_value
column_header_1 = row_2_column_1_value
column_header_2 = row_2_column_2_value
column_header_1 = row_3_column_1_value
column_header_2 = row_3_column_2_value
```

The Python script requires several command line arguments in order to function properly.  You can view the Help output by issuing the command `python3 deploy_template.py --help`, or `py deploy_template.py --help` on Windows operating systems.  The necessary command line arguments are listed below:

| CLI Argument | Value | Description |
| :--- | :--- | :--- |
| `--username`</br>`-u` | admin | DNA Center username |
| `--password`</br>`-p` | password | DNA Center password |
| `--dnac_server` | `192.168.1.1`</br>`dnac_server.example.com` | DNA Center server IP Address or DNS Hostname |
| `--templateId` | `f89d61eb-65e9-46ae-8bdb-e81cd0ac910e` | Universally Unique Identifier (UUID) of Template, normally obtained via DNAC APIs |
| `--deviceId` | `f89d61eb-65e9-46ae-8bdb-e81cd0ac910e` | Universally Unique Identifier (UUID) of target device, normally obtained via DNAC APIs |
| `--csv_file` | `my_file.csv` | Filename and optionally full-path to input CSV file. |

## Ansible Examples

Refer to [README](/ansible/README.md) file.
