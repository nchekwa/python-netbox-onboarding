from os import environ
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
#print(__all__)

from requests.auth import HTTPBasicAuth
from pprint import pprint
import requests
import json
import re

import config.settings
from config.yaml import Yaml

from netbox import *
from netbox.juniper import *


def _create(urn, payload_object=None):
    
    # Define URL and YAML option
    url = config.settings.yaml['netbox_url'] + urn
    option = urn.split('/')[-2]

    items = list()
    # Go throuh all items definet in YAML
    if payload_object is None:
        try:
            items = config.settings.yaml[option]
        except KeyError:
            print ('\033[37m[------]\033[0m ' + option + ': nothing to do')
            return
    else:
        items.append(payload_object)
    
    #print (items)
    for item in items:
        #print(item)
        # Get all keys for this option
        payload_keys = list()
        payload = {}
        for keys in item:
            payload_keys.append(keys)

        for parameter in payload_keys:
            #print(parameter, '->', item.get(parameter))
            payload[parameter] = item.get(parameter)

            ### Auto maping NAME to ID
            if(type(item.get(parameter)) == str or type(item.get(parameter)) == list):
                # For 'Sites'
                if(parameter == 'tenant'):
                    payload[parameter] = _query('api/tenancy/tenants/',item.get(parameter),'id')
                # For 'Manu' and 'Device-types'
                if(parameter == 'manufacturer'):
                    payload[parameter] = _query('api/dcim/manufacturers/',item.get(parameter),'id')
                # For 'Devices'
                if(parameter == 'device_type'):
                    payload[parameter] = _query('api/dcim/device-types/',item.get(parameter),'id')
                if(parameter == 'device_role'):
                    payload[parameter] = _query('api/dcim/device-roles/',item.get(parameter),'id')
                if(parameter == 'site'):
                    payload[parameter] = _query('api/dcim/sites/',item.get(parameter),'id')
                
                if(parameter == 'device'):
                    payload[parameter] = _query('api/dcim/devices/',item.get(parameter),'id')
                
                if(parameter == 'interface'):
                    payload[parameter] = _query('api/dcim/interfaces/',item.get(parameter)+'@'+item.get('device'),'id')

                if(parameter == 'termination_a_id' or parameter == 'termination_b_id'):
                    payload[parameter] = str(_query('api/dcim/interfaces/',item.get(parameter),'id'))

                if(parameter == 'platform' ):
                    payload[parameter] = str(_query('api/dcim/platforms/',item.get(parameter),'id'))

                if(parameter == 'primary_ip4' ):
                    payload[parameter] = str(_query('api/ipam/ip-addresses/',item.get(parameter),'id'))

                if(parameter == 'role' ):
                    payload[parameter] = str(_query('api/ipam/roles/',item.get(parameter),'id'))

        #print(payload)

        # In some models - name parameter not exist.. (ie. device-types create)
        # In such situation we asume that first[main object descriptor] parameter would be the name
        if 'name' not in payload.keys():
            item['name'] = item[payload_keys[0]]

        # If slug key is not defined - create from name
        if 'slug' not in payload.keys():
            payload['slug'] = item['name'].lower().replace(" ", "_")

        #print(payload)
        rest_call = requests.post(url, headers=config.settings.headers, data=json.dumps(payload))
        if rest_call.status_code == 201:
            print ('\033[92m[ok]    \033[0m ' + option + ': \033[1m' + item['name'] + '\033[0m successfully created')
        else:
            print ('\033[91m[failed]\033[0m create ' + option + ' \033[1m' + item['name'] + '\033[0m' )
            if environ.get("DEBUG") is not None:
                pprint (rest_call.json())


def _query(urn,search_name,out_parameter=None):
    #print (search_name)
    # Getu option based on URN
    option = urn.split('/')[-2]

    # Payload which will be send in Query to Netbox - search criteria -> name
    search = 'name='+str(search_name)

    # Model needs to be search by model parameter
    if option == 'device-types':
            search = 'model='+str(search_name)

    # Workeround to search interface@devicename
    if option == 'interfaces':
        search = 'name='+search_name.split('@')[0]+'&device='+search_name.split('@')[1]

    # Define URL
    url = config.settings.yaml['netbox_url'] + urn + '?' + search
    #print (url)
    #return
    rest_call = requests.get(url, headers=config.settings.headers)
    #print(rest_call.json())
    if rest_call.status_code != 200:
        print ('\033[91m[failed]\033[0m error ' + str(rest_call.status_code) + ' not able to find \033[1m' + search_name + '\033[0m ' + option)
        return
     
    if rest_call.status_code == 200:
        reponse = rest_call.json()
        #print(reponse)
        #for data_reponse in reponse['results']:
        #    for key, value in data_reponse.items():
        #        print(key, '->', value)
        try:
            reponse['results'][0]
        except KeyError:
            print ('\033[91m[failed]\033[0m to get list - ' + option )
            return
        except  IndexError:
            return

        if out_parameter is not None:
            return reponse['results'][0][out_parameter]
        else:
            return reponse['results'][0]


        




