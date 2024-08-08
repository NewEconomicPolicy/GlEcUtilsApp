#-------------------------------------------------------------------------------
# Name:        initialise_dvrse_utils.py
# Purpose:     script to read Astley's file and create new one with just MU_GLOBALS and Lat Longs
# Author:      Mike Martin
# Created:     31/07/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'initialise_dvrse_utils.py'
__version__ = '0.0.0'

# Version history
# ---------------
# 
from os.path import join, normpath, exists, isdir
from os import getcwd
from time import sleep
import json

sleepTime = 5
APPLIC_STR = 'glbl_ecss_utils'
ERROR_STR = '*** Error *** '

def initiation(form):
    '''

    '''
    root_dir = 'E:\\'
    data_dir = 'H:\\'
    form.root_dir = root_dir
    form.data_dir = data_dir
    form.menuEntries = {}

    form.fpng = normpath(join(getcwd(), '../images', 'World_small.PNG'))
    config_dir = join(getcwd(),  '../config')
    if not isdir(config_dir):
        print(ERROR_STR + 'configuration directory ' + config_dir + ' must exist')
        sleep(sleepTime)
        exit(0)

    form.config_file = normpath(join(getcwd(),  '../config', APPLIC_STR + '.json'))
    return

def read_config_file(form):
    '''
    read names of files used in the previous programme session from the config file if it exists
    or create default using the current selections if config file does not exist
    '''
    config_file = form.config_file
    if exists(config_file):
        try:
            with open(config_file, 'r') as fconfig:
                config = json.load(fconfig)
        except (OSError, IOError) as e:
                print(e)
                return False
    else:
        # stanza if config_file needs to be created
        _default_config = {
            'FortDir': {
                 'ref_dir': getcwd()
            }
        }

        # if config file does not exist then create it...
        with open(config_file, 'w') as fconfig:
            json.dump(_default_config, fconfig, indent=2, sort_keys=True)
            config = _default_config

    grp = 'FortDir'
    ref_dir = config[grp]['ref_dir']
    form.w_lbl04.setText(normpath(ref_dir))
    if 'n_files' in config[grp]:
        n_files = config[grp]['n_files']
    else:
        n_files = 2
    form.w_ndsets.setText(str(n_files))

def write_config_file(form):

    config_file = form.config_file

    # grp = 'Files'

    config = {
        'FortDir': {
            'ref_dir': form.w_lbl04.text(),
            'n_files': form.w_ndsets.text()
            }
        }

    with open(config_file, 'w') as fconfig:
        json.dump(config, fconfig, indent=2, sort_keys=True)


