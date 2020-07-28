from os import environ 
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

import netbox
#####################################################################
# vqfx-10000
def vqfx_10000():
    device_types = {
        "model": 'vqfx-10000',
        "u_height": 1,
        "manufacturer": 'Juniper'
    }
    netbox._create('api/dcim/device-types/', device_types)

    device_id = netbox._query('api/dcim/device-types/','vqfx-10000','id')
    ## Interfaces
    # Managment EM0
    interface={
        "device_type": device_id,
        "name": 'em0',
        "type": '1000base-t',
        "mgmt_only": 'True'
    }
    netbox._create('api/dcim/interface-templates/', interface)

    # Managment EM1
    interface={
        "device_type": device_id,
        "name": 'em1',
        "type": '1000base-t',
        "mgmt_only": 'False'
    }
    netbox._create('api/dcim/interface-templates/', interface)

    # Loopback 0
    interface={
        "device_type": device_id,
        "name": 'lo0',
        "type": 'virtual',
        "mgmt_only": 'False'
    }
    netbox._create('api/dcim/interface-templates/', interface)

    # Line Interfaces
    interface['type']       = '10gbase-t'
    interface['mgmt_only']  = False
    for port in range(0, 11):
        interface['name'] = 'xe-0/0/' + str(port)
        netbox._create('api/dcim/interface-templates/', interface)