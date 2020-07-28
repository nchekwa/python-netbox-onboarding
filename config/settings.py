from os import environ 
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

import os

def init():
    global yaml
    global rest
    yaml = {}
    rest = {}


