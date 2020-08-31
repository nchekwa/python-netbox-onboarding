from os import environ 
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

import os
import netbox.settings
<<<<<<< HEAD
from netbox.config_yaml import Config_Yaml
=======
from netbox.yaml import Yaml
>>>>>>> 7d7437bb482d12001aaa4aa5fe8e19c1023ae6d5

def init():
    global yaml
    global rest
    yaml = {}
    rest = {}


def init_http_header():
    global headers
    headers={
        'Authorization': 'Token ' + yaml['netbox_token'],
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


def load_yaml(config_path):
    netbox.settings.init() 
<<<<<<< HEAD
    netbox.settings.yaml = Config_Yaml(config_path).import_variables_from_file()
=======
    netbox.settings.yaml = Yaml(config_path).import_variables_from_file()
>>>>>>> 7d7437bb482d12001aaa4aa5fe8e19c1023ae6d5
    netbox.settings.init_http_header()
