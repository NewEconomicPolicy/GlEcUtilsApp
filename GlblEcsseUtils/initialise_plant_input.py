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
__prog__ = 'initialise_plant_input.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from os.path import join, isfile, exists
from os import getcwd
import sys
from json import load as json_load, dump as json_dump
from time import sleep

sleepTime = 5

def initiation(form):
    """
    this function is called to initiate the program to process non-GUI settings.
    """

    # retrieve settings
    _read_setup_file(form)
    form.config_file = join(form.config_dir, 'plant_input_hwsd_regrid_config.json' )     # configuration file
    return

def _read_setup_file(form):
    """
    read settings used for programme from the setup file, if it exists,
    or create setup file using default values if file does not exist
    """
    func_name =  __prog__ +  ' _read_setup_file'

    # retrieve settings - look for setup file here...
    setup_file = join(getcwd(), 'plant_input_regrid.json')
    if exists(setup_file):
        try:
            with open(setup_file, 'r') as fsetup:
                settings = json_load(fsetup)
        except (OSError, IOError) as err:
                print(err)
                return False
    else:
        settings = _write_default_setup_file(setup_file)

    form.setup_file = setup_file

    grp = 'setup'
    try:
        root_dir        = settings[grp]['root_dir']
        form.config_dir = settings[grp]['config_dir']
        fpng = settings[grp]['fname_png']
    except KeyError:
        print('{0}\tError in group: {1}'.format(func_name,grp))
        settings = _write_default_setup_file(setup_file)

    if not isfile(fpng):
        print('File {} does not exist'.format(fpng))
    form.fname_png = fpng

    return True

def read_config_file(form):
    """
    # read widget settings used in the previous programme session from the config file, if it exists,
    # or create config file using default settings if config file does not exist
    """
    func_name =  __prog__ +  ' read_config_file'

    config_file = form.config_file
    if exists(config_file):
        try:
            with open(config_file, 'r') as fconfig:
                config = json_load(fconfig)
        except (OSError, IOError) as err:
                print(err)
                return False
    else:
        config = _write_default_config_file(config_file)

    # read group - only one
    # =====================
    FNAMES_LIST = list(['hwsd_file', 'yields_file', 'latlon_file', 'max_recs', 'fert_file', 'out_dir','sowing_file'])
    grp = 'fnames'
    for attrib in FNAMES_LIST:
        if attrib not in config[grp]:
            config[grp][attrib] = ''

    hwsd_file   = config[grp]['hwsd_file']
    yields_file = config[grp]['yields_file']
    latlon_file = config[grp]['latlon_file']
    max_recs   = config[grp]['max_recs']
    fert_file = config[grp]['fert_file']
    out_dir = config[grp]['out_dir']
    sowing_file = config[grp]['sowing_file']

    form.w_lbl01.setText(yields_file)
    form.w_lbl02.setText(hwsd_file)
    form.w_lbl05.setText(latlon_file)
    form.w_lbl07.setText(fert_file)
    form.w_lbl09.setText(sowing_file)
    form.w_lbl_outdir.setText(out_dir)
    form.w_max_recs.setText(str(max_recs))

    return True

def write_config_file(form):
    '''

    '''
    config_file = form.config_file

    config = {
        'fnames': {
            'yields_file': form.w_lbl01.text(),
            'hwsd_file': form.w_lbl02.text(),
            'latlon_file': form.w_lbl05.text(),
            'fert_file': form.w_lbl07.text(),
            'max_recs': form.w_max_recs.text(),
            'out_dir': form.w_lbl_outdir.text(),
            'sowing_file': form.w_lbl09.text()
            }
        }
    with open(config_file, 'w') as fconfig:
        json_dump(config, fconfig, indent=2, sort_keys=True)

def _write_default_config_file(config_file):
    """
    # only required if the config_file needs to be created
    """
    _default_config = {
        'fnames': {
            'hwsd_file': "",
            'yields_file': "",
            'latlon_file': "",
            'fert_file': "",
            'sowing_file': ""
            }
        }

    # if config file does not exist then create it
    # ============================================
    try:
        with open(config_file, 'w') as fconfig:
            json_dump(_default_config, fconfig, indent=2, sort_keys=True)
    except FileNotFoundError as err:
        print('Could not create configuration file ' + config_file)
        sleep(sleepTime)
        sys.exit(0)

    return _default_config

def _write_default_setup_file(setup_file):
    """
    #  stanza if setup_file needs to be created
    """

    # TODO: check directory exists
    root_dir = 'E:\\'

    _default_setup = {
        'setup': {
            'root_dir'   : root_dir,
            'config_dir' : root_dir + 'mark2mike\\config'
        }
    }
    # if setup file does not exist then create it...
    with open(setup_file, 'w') as fsetup:
        json_dump(_default_setup, fsetup, indent=2, sort_keys=True)
        return _default_setup


