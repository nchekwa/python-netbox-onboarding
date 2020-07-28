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
import requests
import json
import yaml
import time
import netbox
from netbox import *


# Innit global config modular share
import config.settings
from config.yaml import Yaml
config.settings.init() 
config.settings.yaml = Yaml('variables.yaml').import_variables_from_file()
config.settings.init_http_header()




netbox.juniper.Provision()

# 1) Create Tenants: CompanyA/B
netbox._create('api/tenancy/tenants/')

# 2) Create site: DC1/DC2
netbox._create('api/dcim/sites/')

# 3) Create Device Roles: leaf/spine
netbox._create('api/dcim/device-roles/')

# 4) ie. Juniper
netbox._create('api/dcim/manufacturers/')

# 5) ie. junos
netbox._create('api/dcim/platforms/')

# 6) ie. vqfx-10000
netbox._create('api/dcim/device-types/')

# 7) Ceate Role leaf_switch / spine
netbox._create('api/ipam/roles/')
netbox._create('api/ipam/prefixes/')

# 8) 	
netbox._create('api/dcim/devices/')

# 9)
netbox._create('api/ipam/ip-addresses/')

# 10)
netbox._create('api/dcim/cables/')
