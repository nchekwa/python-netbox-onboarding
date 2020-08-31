#!/usr/bin/env python
import json
import yaml
import os
from requests.auth import HTTPBasicAuth
from pprint import pprint
import requests
import re

nb_inventory = """
# nb_inventory.yml file in YAML format
# Example command line: ansible-inventory -v --list -i nb_inventory.yml
# https://github.com/netbox-community/ansible_modules/blob/devel/plugins/inventory/nb_inventory.py

plugin: "netbox.netbox.nb_inventory"
api_endpoint: http://192.168.254.90
token: 678bcbfccbbcb6a59069438b89b5d0f9e4a3081a
config_context: True
interfaces: True
flatten_config_context: True
flatten_local_context_data: True
flatten_custom_fields: True
group_by:
  - device_roles
#   - role
group_names_raw: True
compose:
  ansible_network_os: platform.slug
  role: custom_fields.role.label
device_query_filters:
  - name: 'Spine-20'

""" 

my_inventory_script = open('nb_inventory.yml','w')
my_inventory_script.write(nb_inventory)
my_inventory_script.close()

netbox_inventory = os.popen("/usr/bin/ansible-inventory --list -i nb_inventory.yml")
data = json.loads(netbox_inventory.read())
output_data = data
######################################################################################################################
def generate_underlay_ip_clos(device_config):
  ret = dict()
  ret['physical_interfaces'] = list()
  # Loop via all Netbox Interfaces inside this one device
  for interface in device_config['interfaces']:
    #print(interface['name'])
    if interface['mtu'] == 9192 and interface['connection_status'] and interface['enabled'] == True or re.match(r'^lo', interface['name']):
      #print(interface['name'] + "MTU 9192")
      p_if = dict()
      p_if['name'] = interface['name']
      p_if['mtu'] = interface['mtu']
      p_if['logical_interfaces'] = list()
      # Check if IP address is assign to this interface
      if len(interface['ip_addresses']) != 0:
        #print(interface['ip_addresses'][0]['address'])
        ipp = interface['ip_addresses'][0]['address'].split("/")
        ip = ipp[0]
        mask = ipp[1]
        
        ips = dict()
        ips['address'] = ip
        ips['mask'] = mask

        l_if = dict()
        l_if['name'] = interface['name']+".0"
        l_if['unit'] = "0"
        l_if['ip_addresses'] = list()
        l_if['ip_addresses'].append(ips)

        p_if['logical_interfaces'].append(l_if)
      
      ret['physical_interfaces'].append(p_if)
  return(ret)

######################################################################################################################
## Ask for ASN from Site
with open(r'nb_inventory.yml') as file:
    config_parameters = yaml.load(file, Loader=yaml.FullLoader)
netbox_api_settings = dict()
netbox_api_settings['Authorization'] = 'Token '+config_parameters['token']
netbox_api_settings['Content-Type'] = 'application/json'
url = config_parameters['api_endpoint'] + '/api/dcim/sites/?slug=warsaw_dc1'
rest_call = requests.get(url, headers=netbox_api_settings)
if rest_call.status_code == 200:
    reponse = rest_call.json()
    try:
        reponse['results'][0]['asn']
    except KeyError:
        print ('\033[91m[failed]\033[0m to get ASN for underlay - check ASN in Site' )
    except  IndexError:
        exit(1)
asn = reponse['results'][0]['asn']



for device in data['_meta']['hostvars']:
  this_device_parm = data['_meta']['hostvars'][device]

  # To each device add informaton about overlay ASN
  output_data['_meta']['hostvars'][device]['asn'] = asn
  
  # Check add CEM interfecase abstract
  output_data['_meta']['hostvars'][device]['device_abstract_config']['features'] = dict()
  output_data['_meta']['hostvars'][device]['device_abstract_config']['features']['underlay-ip-clos'] = dict()
  output_data['_meta']['hostvars'][device]['device_abstract_config']['features']['underlay-ip-clos'] = generate_underlay_ip_clos(this_device_parm)

  output_data['_meta']['hostvars'][device].pop('interfaces', None)

os.remove("nb_inventory.yml")
print(json.dumps(output_data, sort_keys=True, indent=2))




