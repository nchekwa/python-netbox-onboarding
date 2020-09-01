#!/usr/bin/python3
###################################################
# This script takes the variables defined in the file variables.yml 
# and make rest calls to Netbox to configure it.
#
# Created by: Artur Zdolinski
# Date: 2020-07-21
# Tested with Python3 / Netbox v2.8.7
###################################################
# > bash# export PYTHONDONTWRITEBYTECODE=1
# > bash# export DEBUG=1           / unset DEBUG

from os import environ
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

from requests.auth import HTTPBasicAuth
from pprint import pprint
import argparse
import requests
import json
import yaml
import time
import netbox


from netbox import *



import netbox.settings
from netbox.config_yaml import Config_Yaml


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='configure_netbox.py')
    parser.add_argument('-c', '--config', help='YAML File with configuration', default='config/variables.yaml')
    args = parser.parse_args()
    kwargs = vars(args)
    print('Running. Press CTRL-C to exit.')

    ##############################################################################
    # Innit global config modular share
    netbox.settings.load_yaml(kwargs['config'])

    # Create pre-defined Juniper Manufacture/Devices
    netbox.devicetypes('Juniper')
   
    ##############################################################################
    # 1) Create Tenants: CompanyA/B
    netbox.create('api/tenancy/tenants/')

    # 2) Create site: DC1/DC2
    netbox.create('api/dcim/sites/')

    # 3) Create Device Roles: leaf/spine
    netbox.create('api/dcim/device-roles/')

    # 4) Create Manufacturer ie. Juniper
    netbox.create('api/dcim/manufacturers/')

    # 5) Create Platform ie. junos
    netbox.create('api/dcim/platforms/')
    
    # 6) Create device schema ie. Nexus-9000
    netbox.create('api/dcim/device-types/')

    # 7) Ceate Role leaf_switch / spine
    netbox.create('api/ipam/roles/')
    netbox.create('api/ipam/prefixes/')

    # 8) Create Device + addtional interfaces if not included in Device-Type
    netbox.create('api/dcim/devices/')
    netbox.create('api/dcim/interfaces/')

    # 9) Create IP-Addresses
    # not standard field: 
    # interface: <if-name>@<device-name>
    # ie. interface: xe-0/0/0@Leaf-30
    netbox.create('api/ipam/ip-addresses/')
    
    # 10) Create cable interconnects between devices
    # not standard fields [termination_a_id, termination_b_id]: 
    # termination_a_id: <if-name>@<device-name>
    # ie. termination_a_id: xe-0/0/0@Leaf-30
    netbox.create('api/dcim/cables/')
