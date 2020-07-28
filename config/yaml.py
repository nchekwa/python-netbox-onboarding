from os import environ
if environ.get("DEBUG") is not None:
    print('__file__={0:<65} | __name__={1:<25} | __package__={2:<20}'.format(__file__,__name__,str(__package__)))

import yaml
import config.settings

class Yaml:

    def __init__(self, fname):
        self.fname = fname

    def set_config(self, fname):
        self.fname.append(fname)

    def import_variables_from_file(self):
        my_variables_file=open(self.fname, 'r')
        my_variables_in_string=my_variables_file.read()
        my_variables_in_yaml=yaml.safe_load(my_variables_in_string)
        my_variables_file.close()
        #print (my_variables_in_string)
        #print (my_variables_in_yaml)
        #print (my_variables_in_yaml['ip'])
        return my_variables_in_yaml
