"""
Copyright (c) 2022 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Aron Donaldson <ardonald@cisco.com>"
__contributors__ = ""
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import csv
import json
import time
import sys
from argparse import ArgumentParser
# External packages from Pip
import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable insecure connection warnings on destinations with untrusted certificates
urllib3.disable_warnings()

def auth(dnac_server, username, password):
    # Authenticate to DNA Center API and return the access token.  Tokens are valid for 60 minutes.
    credentials = HTTPBasicAuth(username, password)
    url = f'https://{dnac_server}/api/system/v1/auth/token'
    result = requests.post(url, auth=credentials, verify=False)
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
            csv_data.append(row)
        f.close()
    print(f'CSV Data:\n{json.dumps(csv_data, indent=4)}\n')
    return csv_data


def deploy_template(token, dnac_server, template_id, device_id, csv_data):
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
                    "csv_data": csv_data
                }
            }
        ]
    }
    result = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
    # print(f'{result.status_code}\n{result.headers}\n{result.json()}\n\n')  # Uncomment this line for debugging
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
        if result.status_code in [201, 202, 204]:
            try:
                status = result.json()['status']
            except KeyError:
                print('Waiting 10 seconds...')
                time.sleep(10)
                continue
            if status in ['SUCCESS', 'FAILURE']:
                print('Deployment status:\n')
                print(json.dumps(result.json(), indent=4))
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


if __name__ == '__main__':
    parser = ArgumentParser(description='Select your options:')
    parser.add_argument('--username', '-u', type=str, required=True, help="DNAC Username")
    parser.add_argument('--password', '-p', type=str, required=True, help="DNAC Password")
    parser.add_argument('--dnac_server', type=str, required=True, help="DNAC Server IP")
    parser.add_argument('--templateId', type=str, required=True, help="Template UUID")
    parser.add_argument('--deviceId', type=str, required=True, help="Target Device UUID")
    parser.add_argument('--csv_file', type=str, required=True, help="CSV Input File")
    args = parser.parse_args()
    
    token = auth(args.dnac_server, args.username, args.password)
    csv_data = parse_csv(args.csv_file)
    deploy_id = deploy_template(token, args.dnac_server, args.templateId, args.deviceId, csv_data)
    result = check_deployment(args.dnac_server, token, deploy_id)
