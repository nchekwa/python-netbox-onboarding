from os import environ 
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

import netbox
#####################################################################
# qfx10002-36q
def qfx10002_36q():
    device_types = {
        "model": 'qfx10002-36q',
        "u_height": 1,
        "manufacturer": 'Juniper'
    }
    netbox.create('api/dcim/device-types/', device_types)

    device_id = netbox.query('api/dcim/device-types/','qfx10002-36q','id')
    ## Power
    # https://www.juniper.net/documentation/en_US/release-independent/junos/topics/topic-map/qfx10002-power-system.html
    power_port = {
        'device_type': device_id,
        "name": 'PEM0',
        "type": 'iec-60320-c14',
        "maximum_draw": 1600,
        "allocated_draw": 1320
    }
    for port in range(0, 4):
        power_port['name'] = 'PEM' + str(port)
        netbox.create('api/dcim/power-port-templates/', power_port)

    ## Interfaces
    # https://www.juniper.net/documentation/en_US/release-independent/junos/topics/topic-map/qfx10002-port-panel.html
    # Managment
    interface={
        "device_type": device_id,
        "name": 'fxp0',
        "type": '100base-tx',
        "mgmt_only": 'True'
    }
    netbox.create('api/dcim/interface-templates/', interface)

    # Loopback 0
    interface={
        "device_type": device_id,
        "name": 'lo0',
        "type": 'virtual',
        "mgmt_only": 'False'
    }
    netbox.create('api/dcim/interface-templates/', interface)

    # Line Interfaces
    interface['type']       = '100gbase-x-qsfp28'
    interface['mgmt_only']  = False
    for port in range(0, 36):
        interface['name'] = 'xe-0/0/' + str(port)
        netbox.create('api/dcim/interface-templates/', interface)



#################################################
# virtual, lag, 100base-tx, 1000base-t, 2.5gbase-t, 5gbase-t, 10gbase-t, 10gbase-cx4, 1000base-x-gbic, 
# 1000base-x-sfp, 10gbase-x-sfpp, 10gbase-x-xfp, 10gbase-x-xenpak, 10gbase-x-x2, 25gbase-x-sfp28, 40gbase-x-qsfpp, 
# 50gbase-x-sfp28, 100gbase-x-cfp, 100gbase-x-cfp2, 200gbase-x-cfp2, 100gbase-x-cfp4, 100gbase-x-cpak, 100gbase-x-qsfp28, 
# 200gbase-x-qsfp56, 400gbase-x-qsfpdd, 400gbase-x-osfp, ieee802.11a, ieee802.11g, ieee802.11n, ieee802.11ac, 
# ieee802.11ad, ieee802.11ax, gsm, cdma, lte, sonet-oc3, sonet-oc12, sonet-oc48, sonet-oc192, sonet-oc768, sonet-oc1920, 
# sonet-oc3840, 1gfc-sfp, 2gfc-sfp, 4gfc-sfp, 8gfc-sfpp, 16gfc-sfpp, 32gfc-sfp28, 128gfc-sfp28, infiniband-sdr, infiniband-ddr, 
# infiniband-qdr, infiniband-fdr10, infiniband-fdr, infiniband-edr, infiniband-hdr, infiniband-ndr, infiniband-xdr, t1, e1, t3, e3, 
# cisco-stackwise, cisco-stackwise-plus, cisco-flexstack, cisco-flexstack-plus, juniper-vcp, extreme-summitstack, 
# extreme-summitstack-128, extreme-summitstack-256, extreme-summitstack-512, other 