"""
#-------------------------------------------------------------------------------
# Name:
# Purpose:     consist of high level functions invoked by main GUI
# Author:      Mike Martin
# Created:     11/12/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#

"""
__prog__ = 'initialise_cntry_code.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

import os
import json
import time
import sys

sleepTime = 5
APPLIC_STR =  'country_iso_codes'

def initiation(form):
    '''
    # this function is called to initiate the programme to process non-GUI settings.
    '''
    root_dirE = 'E:\\'
    root_dirC = 'C:\\'
    wc_path = 'Freeware\\UnxUtils\\usr\\local\\wbin\\wc.exe'
    for root_dir in list([root_dirC, root_dirE]):
        wc_exe_try = root_dir + wc_path
        if os.path.isfile(wc_exe_try):
            wc_exe = wc_exe_try
            break

    form.wc_exe = wc_exe

    decompressor = 'C:\\Program Files\\7-Zip\\7z.exe'
    if not os.path.isfile(decompressor):
        print('Decompression executable ' + decompressor + ' must exist')

    form.decompressor = decompressor
    form.root_dir = root_dirE

    # retrieve settings
    # look for setup file here...
    setup_file = os.path.join(os.getcwd(), APPLIC_STR + '.json')

    if os.path.exists(setup_file):
        try:
            with open(setup_file, 'r') as fsetup:
                settings = json.load(fsetup)
        except (OSError, IOError) as e:
                print(e)
                return False
    else:
        settings = _write_default_setup_file(setup_file, root_dirE)

    grp = 'setup'
    try:
        form.codes_fname    = settings[grp]['codes_fname']
        form.cntry_shp_dir  = settings[grp]['cntry_shp_dir']
        form.zip_dir        = settings[grp]['zip_dir']
        form.overwrite_flag = settings[grp]['overwrite_flag']

    except KeyError:
        print('\tError in setup group: {}'.format(grp))
        settings = _write_default_setup_file(setup_file, form.root_dir)
        time.sleep(sleepTime)
        sys.exit(0)


    form.fname_png  = os.path.join(os.getcwd() + '\\Images', 'World_small.PNG')
    form.setup_file = setup_file
    form.any_fname = 'E:\\'
    form.hwsd_dir = 'E:\\GlobalEcosseData\\HWSD_NEW'

    return

def _write_default_setup_file(setup_file, root_dirE):
    """
    #  stanza if setup_file needs to be created
    """

    _default_setup = {
        'setup': {
            'codes_fname'    : '',
            'cntry_shp_dir'  : root_dirE,
            'zip_dir'        : root_dirE,
            'overwrite_flag' : False
        }
    }
    # if setup file does not exist then create it...
    with open(setup_file, 'w') as fsetup:
        json.dump(_default_setup, fsetup, indent=2, sort_keys=True)
        return _default_setup

def _write_setup_file(form):
    """
    # write current selections to setup file
    """
    setup_file = form.setup_file

    setup = {
        'setup': {
            'codes_fname'    : os.path.normpath(form.codes_fname),
            'zip_dir'        : form.zip_dir,
            'cntry_shp_dir'  : form.cntry_shp_dir,
            'overwrite_flag' : form.w_over_write.isChecked()
        }
    }
    with open(setup_file, 'w') as fsetup:
        json.dump(setup, fsetup, indent=2, sort_keys=True)