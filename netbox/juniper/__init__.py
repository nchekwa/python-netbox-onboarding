from os import environ
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))


from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
for module in __all__:
    try:
        exec("from netbox.juniper.{x} import {x}".format(x=module))
        #print ("Successfully imported "+ module)
    except ImportError:
        print ("Error importing "+ module)


import netbox
class Provision():

    def __init__(self):
        
        # Ceck If Junier Manufacture exist / if not - create
        juniper_manufacturer = netbox._query('api/dcim/manufacturers/','Juniper','id')
        if juniper_manufacturer is None:
            manufacturer = {
                "name": 'Juniper',
                "description": 'Juniper Networks'
            }
            netbox._create('api/dcim/manufacturers/', manufacturer)
            juniper_manufacturer = netbox._query('api/dcim/manufacturers/','Juniper','id')

            platform = {
                "name": 'junos',
                "napalm_driver": 'junos',
                "manufacturer": juniper_manufacturer
            }
            netbox._create('api/dcim/platforms/', platform)


        ## Device Provisioning
        for type in __all__:
            dev_model = type.replace("_","-")
            device_id = netbox._query('api/dcim/device-types/', dev_model, 'id')
            if device_id is None:
                #ie. qfx10002_36q()
                eval(type)()


        #    qfx5100_48s_6q()
