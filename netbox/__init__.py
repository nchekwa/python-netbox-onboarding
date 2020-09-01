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
import glob
import os
import yaml
import copy

import netbox.settings
from netbox.config_yaml import Config_Yaml

from netbox import *

def create(urn, payload_object=None):
    
    # Define URL and YAML option
    url = netbox.settings.yaml['netbox_url'] + urn
    option = urn.split('/')[-2]

    items = list()
    # Go throuh all items definet in YAML
    if payload_object is None:
        try:
            items = netbox.settings.yaml[option]
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
        payload_orig = {}
        for keys in item:
            payload_keys.append(keys)

        for parameter in payload_keys:
            #print(parameter, '->', item.get(parameter))
            payload[parameter] = item.get(parameter)
            payload_orig[parameter] = item.get(parameter)

            ### Auto maping NAME to ID
            if(type(item.get(parameter)) == str or type(item.get(parameter)) == list):
                # For 'Sites'
                if(parameter == 'tenant'):
                    payload[parameter] = query('api/tenancy/tenants/',item.get(parameter),'id')
                
                # For 'Manu' and 'Device-types'
                if(parameter == 'manufacturer'):
                    payload[parameter] = query('api/dcim/manufacturers/',item.get(parameter),'id')
                
                # For 'Devices'
                if(parameter == 'device_type'):
                    payload[parameter] = query('api/dcim/device-types/',item.get(parameter),'id')

                if(parameter == 'device_role'):
                    payload[parameter] = query('api/dcim/device-roles/',item.get(parameter),'id')

                if(parameter == 'site'):
                    payload[parameter] = query('api/dcim/sites/',item.get(parameter),'id')
                
                if(parameter == 'device'):
                    payload[parameter] = query('api/dcim/devices/',item.get(parameter),'id')
 
                #if(parameter == 'interface'):
                #    pprint(item)
                #    payload[parameter] = query('api/dcim/interfaces/',item.get(parameter)+'@'+item.get('device'),'id')

                if(parameter == 'termination_a_id' or parameter == 'termination_b_id'):
                    payload[parameter] = str(query('api/dcim/interfaces/',item.get(parameter),'id'))

                if(parameter == 'platform' ):
                    payload[parameter] = str(query('api/dcim/platforms/',item.get(parameter),'id'))

                if(parameter == 'primary_ip4' ):
                    payload[parameter] = str(query('api/ipam/ip-addresses/',item.get(parameter),'id'))

                if(parameter == 'role' and option == "prefixes"):
                    payload[parameter] = str(query('api/ipam/roles/',item.get(parameter),'id'))

                if(parameter == 'local_context_data' ):
                    payload[parameter] = json.dumps(item.get(parameter))
        #print(payload)

        # In some models - name parameter not exist.. (ie. device-types create)
        # In such situation we asume that first[main object descriptor] parameter would be the name
        if 'name' not in payload.keys():
            item['name'] = item[payload_keys[0]]

        # If slug key is not defined - create from name
        if 'slug' not in payload.keys():
            payload['slug'] = item['name'].lower().replace(" ", "_")

        # Prevent duplicated create objects 
        if option == "ip-addresses":
            # Check if IP exist? If exist - conntinue /-> skip this interaction
            ip = query('api/ipam/ip-addresses/',item.get('address'))
            if ip.get('id') and ip.get('vrf') == payload.get('vrf') and ip.get('tenant') == payload.get('tenant'):
                print ('\033[93m[skip]  \033[0m ' + option + ': \033[1m' + ip['address'] + '\033[0m allready exist')
                continue
            # Check if interface exist 
            if item.get('interface'):
                id_interface = query('api/dcim/interfaces/',item.get('interface'),'id')
                # if loopback type - if not exist - auto create interface 
                if type(id_interface) != int and re.match(r'^lo|^em', item.get('interface') ):
                    new_interface = dict()
                    new_interface['type']   = "virtual"
                    new_interface['name']   = item['interface'].split('@')[0]
                    new_interface['device'] = query('api/dcim/devices/',item['interface'].split('@')[1],'id') 
                    netbox.create('api/dcim/interfaces/', new_interface)
                    id_interface = query('api/dcim/interfaces/',item.get('interface'),'id')
                payload['assigned_object_type'] = "dcim.interface"
                payload['assigned_object_id'] = id_interface
                # Remove parameter interface from payload [we need only assigned_object]
                payload.pop('interface')

        if option == "prefixes":
            prefix = query('api/ipam/prefixes/',item.get('prefix'))
            #print(prefix)
            if prefix.get('id') and prefix.get('vrf') == payload.get('vrf') and prefix.get('tenant') == payload.get('tenant') and prefix.get('vlan') == payload.get('vlan'):
                print ('\033[93m[skip]  \033[0m ' + option + ': \033[1m' + payload['prefix'] + '\033[0m allready exist')
                continue

        if option == "cables":
            # if we not define in config "termination_X_type"
            # we assume that we will use type=dcim.interface
            if item.get('termination_a_type') is None:
                payload['termination_a_type'] = "dcim.interface"

            if item.get('termination_b_type') is None:
                payload['termination_b_type'] = "dcim.interface"

        #print(payload)
        rest_call = requests.post(url, headers=netbox.settings.headers, data=json.dumps(payload))
        #print(payload)
        if rest_call.status_code == 201:
            print ('\033[92m[ok]    \033[0m ' + option + ': \033[1m' + item['name'] + '\033[0m successfully created')
            
            ##########################################################################################################
            #
            # Additional jobs after create some elements
            #
            ##########################################################################################################
            # If IP was created for device / and if it is managment -> add this IP as primary_ipv4 in device
            if option == "ip-addresses" and payload.get("status") == "active" and payload.get("mgmt_only") == True :
                #pprint(item)
                ip = query('api/ipam/ip-addresses/', item.get('address'))
                #pprint(ip)
                if ip.get('id'):
                    print('[update] devices: '+ip['assigned_object']['device']['name']+ ': primary_ip4=>'+str(ip['address']))
                    device_payload = dict()
                    device_payload['id'] = ip['assigned_object']['device']['id']
                    device_payload['primary_ip4'] = ip['id']
                    patch('api/dcim/devices/', device_payload)
                    pass
            
            # If we create cable connection for interconnect - we need to update interfaces descriptions on each device and set MTU9192
            if option == "cables" and payload.get("label") == "interconnect":
                termination_a_id = query('api/dcim/interfaces/',item.get('termination_a_id'),'id')
                termination_b_id = query('api/dcim/interfaces/',item.get('termination_b_id'),'id')

                print('[update] interface: '+payload_orig['termination_a_id']+ " - set interconnect inerface description and mtu" )
                if_a_payload = dict()
                if_a_payload['id'] = termination_a_id
                if_a_payload['mtu'] = 9192
                if_a_payload['tag'] = 'interconnect'
                if_a_payload['description'] = str('*** '+payload_orig['termination_a_id']+'<--|-->'+ payload_orig['termination_b_id'] +' ***')
                patch('api/dcim/interfaces/',if_a_payload)

                print('[update] interface: '+payload_orig['termination_b_id']+ " - set interconnect inerface description and mtu" )
                if_b_payload = dict()
                if_b_payload['id'] = termination_b_id
                if_b_payload['mtu'] = 9192
                if_b_payload['tag'] = 'interconnect'
                if_b_payload['description'] = str('*** '+payload_orig['termination_b_id']+'<--|-->'+ payload_orig['termination_a_id'] +' ***')
                patch('api/dcim/interfaces/',if_b_payload)

            ##########################################################################################################

        else:
            print ('\033[91m[failed]\033[0m create ' + option + ' \033[1m' + item['name'] + '\033[0m' )
            if environ.get("DEBUG") is not None:
                pprint (rest_call.json())
            


def query(urn,search_name,out_parameter=None):
    #print (search_name)
    # Getu option based on URN
    option = urn.split('/')[-2]

    # Payload which will be send in Query to Netbox - search criteria -> name
    search = 'name='+str(search_name)

    # Model needs to be search by model parameter
    if option == 'device-types':
            search = 'model='+str(search_name)

    # Model needs to be search by ip-addresses parameter
    if option == 'ip-addresses':
            search = 'address='+str(search_name)

    # Model needs to be search by prefixes parameter
    if option == 'prefixes':
            search = 'prefix='+str(search_name)

    # Workeround to search interface@devicename
    if option == 'interfaces':
        search = 'name='+search_name.split('@')[0]+'&device='+search_name.split('@')[1]

    # Define URL
    url = netbox.settings.yaml['netbox_url'] + urn + '?' + search
    #print(url)

    rest_call = requests.get(url, headers=netbox.settings.headers)
    #print(rest_call.json())
    #print(rest_call.status_code)
    if rest_call.status_code != 200:
        print ('\033[91m[failed]\033[0m error ' + str(rest_call.status_code) + ' not able to find \033[1m' + search_name + '\033[0m ' + option)
        return dict()
     
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
            return dict()
        except  IndexError:
            return dict()

        if out_parameter is not None:
            return reponse['results'][0][out_parameter]
        else:
            return reponse['results'][0]

def patch(urn,payload=None):
    url = netbox.settings.yaml['netbox_url'] + urn
    option = urn.split('/')[-2]
    #print(payload)

    if payload.get('id'):
        #print("Found ID")
        id = payload['id']
        payload.pop('id', None)

    # Define URL
    url = netbox.settings.yaml['netbox_url'] + urn + str(id) + '/'

    rest_call = requests.patch(url, headers=netbox.settings.headers, data=json.dumps(payload))
    #print(rest_call.status_code)
    if rest_call.status_code == 200:
        print ('\033[92m[ok]    \033[0m ' + option + ': successfully updated')
    else:
        print ('\033[91m[failed]\033[0m failed to patch ' + option + ' \033[1m' + str(id) + '\033[0m' )
        if environ.get("DEBUG") is not None:
            pprint (rest_call.json())

def devicetypes(vendor):
    print ('\033[92m[ok]    \033[0m Device Types - folder: config/devicetypes/' + vendor + ' - checking')
    file_number = 0
    device_arr = dict()
    arr = [f for f in glob.glob("config/devicetypes/"+vendor+"/*.yaml")]
    for dev_file in arr:
        head, tail = os.path.split(dev_file)
        file_device_name = tail.replace('.yaml','')
        file_number += 1
        with open(dev_file) as file:
            yml_file_content = yaml.safe_load(file)
            device_arr[yml_file_content['model']] = yml_file_content
    print ('\033[92m[ok]    \033[0m Device Types - number of '+vendor+' devices YAML files: ' + str(file_number) )
    # Ok - so we have all file content in one dict.
    # Check if vendor manfuacture exist?
    id_manufacturer = netbox.query('api/dcim/manufacturers/',vendor,'id')
    if type(id_manufacturer) == int :
        print ('\033[93m[skip]  \033[0m Device Types - manufactur \033[1m' + vendor + '\033[0m allready exist')
    else:
        manufacturer = {
            "name": vendor
        }
        netbox.create('api/dcim/manufacturers/', manufacturer)
        id_manufacturer = netbox.query('api/dcim/manufacturers/',vendor,'id')
        #print ('\033[92m[ok]    \033[0m Device Types - manufacture: '+vendor+' created - id: '+str(id_manufacturer) )

    for unit in device_arr:
        # Check if device allready exist?
        id_device_type = netbox.query('api/dcim/device-types/',unit,'id')
        #print("id_device_type" + str(id_device_type) + " - "+ unit)
        if type(id_device_type) == int :
            print ('\033[93m[skip]  \033[0m Device Types - model \033[1m' + unit + '\033[0m allready exist')
        else:
            # Device not exist - so we create
            new_dev = dict()
            new_dev['device-types'] = dict()
            for key,value in device_arr[unit].items():
                if type(value) != list:
                    new_dev['device-types'][key] = value
                else:
                    new_dev[key] = value
            
            netbox.create('api/dcim/device-types/', new_dev['device-types'])
            device_id = netbox.query('api/dcim/device-types/',new_dev['device-types']['model'],'id')

            device_components = ['interfaces','console-ports','device-bays','power-ports']

            for component in device_components:
                # ie. component = interfaces
                if new_dev.get(component):
                    for inter_key in new_dev[component]:
                        inter_key['device_type'] = device_id
                        netbox.create('api/dcim/'+component[:-1]+'-templates/', inter_key)
            

