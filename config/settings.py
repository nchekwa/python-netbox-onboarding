from os import environ 
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

import os

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