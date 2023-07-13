import csv
import json
import sys
import time
from getpass import getpass
from argparse import ArgumentParser

import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable insecure connection warnings on destinations with untrusted certificates
urllib3.disable_warnings()

# Set global level variable for verbosity
verbose = bool()

def verbose_output(func_name, response):
    # Print verbose API response data to Console
    print(f'{func_name} Response:\n{response.status_code}\n{response.headers}\n{response.json()}\n')
    return


def auth(args):
    # Authenticate to DNA Center API and return the access token.  Tokens are valid for 60 minutes.
    if args.password:
        password = args.password
    else:
        password = getpass("Enter the DNAC Password: ", stream=None)
    credentials = HTTPBasicAuth(args.username, password)
    url = f'https://{args.dnac_server}/api/system/v1/auth/token'
    result = requests.post(url, auth=credentials, verify=False)
    if verbose:
        verbose_output('auth()', result)
    if result.status_code == 200:
        return result.json()['Token']
    else:
        print('Error during authentication.\n')
        sys.exit(1)


def parse_csv(csv_file):
    # Use Python built-in csv module to parse a CSV file, using the simplest method. 
    # Creates a Dictionary for each CSV row (headers become Keys), and appends to a List.
    csv_data = []
    with open(csv_file, 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'additional_config' in row.keys():
                row['additional_config'] = row['additional_config'].replace('\\n', '\n') # Fix up the escaped backslash problem
            csv_data.append(row)
        f.close()
    if verbose:
        print(f'CSV Data:\n{json.dumps(csv_data, indent=4)}\n')
    return csv_data


def parse_txt(txt_file):
    # Reads input text file and creates a string
    with open(txt_file, 'rt') as f:
        txt_data = f.read()
        f.close()
    if verbose:
        print(f'TXT Data:\n{txt_data}\n')
    return txt_data


def parse_yaml(yaml_file):
    # Use PyYAML package from PyPi to parse a YAML file into JSON
    # Only import PyYAML if needed
    import yaml # Packaged named "PyYAML" at pypi.org
    with open(yaml_file, 'r') as f:
        try:
            result = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f'Error parsing YAML file:\n{e}')
            sys.exit(1)
    f.close()
    if args.verbose:
        print(f'YAML Data:\n{json.dumps(result, indent=4)}\n')
    return result


def get_template_uuid(token, dnac_server, projectName, template_name):
    # Make API call to DNAC to resolve template name to UUID
    url = f'https://{dnac_server}/dna/intent/api/v2/template-programmer/template'
    headers = {
        "Content-Type": "application/json",
        "x-auth-token": token
    }
    params = {
        "name": template_name,
        "projectName": projectName,
        "unCommitted": True
    }
    result = requests.get(url, headers=headers, params=params, verify=False)
    if verbose:
        verbose_output('get_template_uuid()', result)
    if result.status_code in [200, 201, 202]:
        # Returns only the first search result - this could be a problem if multiple matches are found.
        return result.json()['response'][0]['id']
    else:
        print('Error locating template UUID.\n')
        sys.exit(1)


def get_device_uuid(token, dnac_server, device_name):
    # Make API call to DNAC to resolve hostname to UUID
    url = f'https://{dnac_server}/dna/intent/api/v1/network-device'
    headers = {
        "Content-Type": "application/json",
        "x-auth-token": token
    }
    params = {
        "hostname": device_name
    }
    result = requests.get(url, headers=headers, params=params, verify=False)
    if verbose:
        verbose_output('get_device_uuid()', result)
    if result.status_code in [200, 201, 202]:
        # Returns only the first search result - this could be a problem if multiple matches are found.
        try:
            device_id = result.json()['response'][0]['id']
        except IndexError as e:
            print(f'Function "get_device_uuid()" did not return any results.\n{e}')
            sys.exit(1)
        return device_id
    else:
        print('Error locating template UUID.\n')
        sys.exit(1)


def preview_template(token, dnac_server, template_id, device_id, input_data):
    # Send payload to Preview Template API and obtain the resulting configuration output.  DOES NOT DEPLOY.
    url = f'https://{dnac_server}/dna/intent/api/v1/template-programmer/template/preview'
    headers = {
        "Content-Type": "application/json",
        "x-auth-token": token
    }
    payload = {
        "deviceId": device_id,
        "templateId": template_id,
        "params": {
            "input_data": input_data
        }
        # "resourceParams": "any"
    }
    result = requests.put(url, headers=headers, json=payload, verify=False)
    if verbose:
        verbose_output('preview_template()', result)
    if result.status_code in [200, 201, 202]:
        return result.json()['cliPreview']
    else:
        print('Error in template preview.\n')
        sys.exit(1)


def deploy_template(token, dnac_server, template_id, device_id, input_data):
    # Construct the API payload and deploy it to the target device.
    # Using V1 of this API endpoint; V2 adds an extra step of returning a Task ID - no real benefit
    url = f'https://{dnac_server}/dna/intent/api/v1/template-programmer/template/deploy'
    headers = {
        "Content-Type": "application/json",
        "x-auth-token": token
    }
    payload = {
        "forcePushTemplate": True,
        "templateId": template_id,
        "targetInfo": [
            {
                "id": device_id,
                "type": "MANAGED_DEVICE_UUID",
                "params": {
                    "input_data": input_data
                }
            }
        ]
    }
    result = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
    if verbose:
        verbose_output('deploy_template()', result)
    if result.status_code in [201, 202]:
        # DNA Center returns a poorly formatted response - we have to slice a string to obtain Deployment ID.
        deploy_data = [x.strip() for x in result.json()['deploymentId'].split(':')]
        deploy_id = deploy_data[len(deploy_data)-1]
        print(f'Deployment ID: {deploy_id}\n')
        return deploy_id
    else:
        print('Error in template deployment.\n')
        sys.exit(1)


def check_deployment(dnac_server, token, deploy_id):
    # Check the status of the template deployment every 10 seconds until a proper response is received.
    url = f'https://{dnac_server}/dna/intent/api/v1/template-programmer/template/deploy/status/{deploy_id}'
    headers = {
        "Content-Type": "application/json",
        "x-auth-token": token
    }
    while True:
        result = requests.get(url, headers=headers, verify=False)
        if verbose:
            verbose_output('check_deployment()', result)
        if result.status_code in [201, 202, 204]:
            try:
                status = result.json()['status']
            except KeyError:
                print('Waiting 10 seconds...')
                time.sleep(10)
                continue
            if status in ['SUCCESS', 'FAILURE']:
                # print('Deployment status:\n')
                # print(json.dumps(result.json(), indent=4))
                break
            else:
                print('Waiting 10 seconds...')
                time.sleep(10)
                continue
        else:
            print('Waiting 10 seconds...')
            time.sleep(10)
            continue
    return result.json()


def main(args):
    global verbose
    verbose = args.verbose
    token = auth(args)
    # Get input_file extension and evaluate it
    if args.input_file.split('.')[1].lower() == 'csv':
        input_data = parse_csv(args.input_file)
    elif args.input_file.split('.')[1].lower() == 'txt':
        input_data = parse_txt(args.input_file)
    elif args.input_file.split('.')[1].lower() in ['yaml', 'yml']:
        input_data = parse_yaml(args.input_file)
    else:
        print('Input file type not supported.\n')
        sys.exit(1)
    template_id = get_template_uuid(token, args.dnac_server, args.template_project, args.template_name)
    device_id = get_device_uuid(token, args.dnac_server, args.device_name)
    if args.preview:
        result = preview_template(token, args.dnac_server, template_id, device_id, input_data)
    else:
        deploy_id = deploy_template(token, args.dnac_server, template_id, device_id, input_data)
        result = check_deployment(args.dnac_server, token, deploy_id)
    print(f'"{args.template_name}" Template Result:\n\n{result}')


if __name__ == '__main__':
    parser = ArgumentParser(description='Select your options:')
    parser.add_argument('--username', '-u', type=str, required=True, help="DNAC Username")
    parser.add_argument('--password', '-p', type=str, help="DNAC Password")
    parser.add_argument('--dnac_server', type=str, required=True, help="DNAC Server IP")
    parser.add_argument('--template_project', type=str, required=True, help="Template Project Name")
    parser.add_argument('--template_name', type=str, required=True, help="Template Name")
    parser.add_argument('--device_name', type=str, required=True, help="Target Device Name")
    parser.add_argument('--input_file', type=str, required=True, help="CSV, TXT or YAML Input File")
    parser.add_argument('--preview', action='store_true', help="Only Preview the template output - do not deploy.")
    parser.add_argument('--verbose', '-v', action='store_true', help="Print verbose output")
    args = parser.parse_args()
    
    main(args)