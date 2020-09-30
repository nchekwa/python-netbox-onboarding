# About
Script which build automatically all elements in Netbox using API request and Python language<br>
Tested with:<br>
- Netbox v2.9.2
- Python 3.6.8 

# HowTo
- check diagram folder for topology example
- check 'config/variables.yaml' file to set what you need

# Run
- edit variables (you can add additional parameters from API syntax)
- run:<br>

```console
bash# cd /opt/python-netbox-onboarding
bash# python3 configure_netbox.py -h
usage: configure_netbox.py [-h] [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        YAML File with configuration (default='config/variables.yaml')
```
YAML Config example: https://github.com/azdolinski/python-netbox-onboarding/blob/master/config/variables.yaml

# Examples screenshots
![Example1](doc/img/example_2.png)
![Example2](doc/img/example_1.png)
![Example3](doc/img/Screenshot_3.png)
![Example4](doc/img/Screenshot_4.png)


# Config-Device-Types
Include predefined device types (like: ![Juniper](https://github.com/netbox-community/devicetype-library/tree/master/device-types/Juniper), ![Cisco](https://github.com/netbox-community/devicetype-library/tree/master/device-types/Cisco), ![Arista](https://github.com/netbox-community/devicetype-library/tree/master/device-types/Arista) etc.) from official repo: ![netbox-community/devicetype-library](https://github.com/netbox-community/devicetype-library)<br>
To sync this project with netbox-comunity devicetype-library:
```bash
yum install -y unzip
cd /opt/python-netbox-onboarding/config/devicetypes
wget https://github.com/netbox-community/devicetype-library/archive/master.zip -O /tmp/master.zip
unzip  /tmp/master.zip -d /tmp/
cp -R /tmp/devicetype-library-master/device-types/* /opt/python-netbox-onboarding/config/devicetypes
```
