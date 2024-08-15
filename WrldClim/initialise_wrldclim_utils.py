"""
#-------------------------------------------------------------------------------
# Name:        initialise_wrldclim_utils.py
# Purpose:     script to read read and write the setup and configuration files
# Author:      Mike Martin
# Created:     16/05/2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
"""

__prog__ = 'initialise_wrldclim_utils.py'
__version__ = '0.0.0'

# Version history
# ---------------
# 
from os.path import isdir, exists, join, lexists, normpath
from os import getcwd, makedirs
import json
from time import sleep
from set_up_logging import set_up_logging

# foe setup and config files
# ==========================
APPLIC_STR = 'netcdf_wrldclim_utils'
SETTINGS_LIST = ['config_dir', 'log_dir', 'fname_png', 'wthr_dir']
USER_SETTINGS_LIST = ['overwrite', 'ssp_indx', 'gcm_indx', 'pop_hist_flag', 'pop_fut_flag']
sleepTime = 5

ERROR_STR = '*** Error *** '

def initiation(form):
    '''
    initiate the programme
    '''
    # retrieve settings
    # =================

    form.settings = _read_setup_file()
    form.settings['config_file'] = normpath(form.settings['config_dir'] + '/' + APPLIC_STR + '_config.json')
    set_up_logging(form, APPLIC_STR)

    return

def _read_setup_file():
    """
    read settings used for programme from the setup file, if it exists,
    or create setup file using default values if file does not
    """
    func_name =  __prog__ +  ' _read_setup_file'

    # validate setup file
    # ===================

    fname_setup = APPLIC_STR + '_setup.json'

    setup_file = join(getcwd(), fname_setup)
    if exists(setup_file):
        try:
            with open(setup_file, 'r') as fsetup:
                setup = json.load(fsetup)

        except (OSError, IOError) as e:
                sleep(sleepTime)
                exit(0)
    else:
        setup = _write_default_setup_file(setup_file)

    # initialise vars
    # ===============
    settings = setup['setup']
    for key in SETTINGS_LIST:
        if key not in settings:
            print('*** Error *** setting {} is required in setup file {} '.format(key, setup_file))
            sleep(sleepTime)
            exit(0)

    settings['APPLIC_STR'] = APPLIC_STR

    # make sure directories exist
    # ===========================
    config_dir = settings['config_dir']
    if not lexists(config_dir):
        makedirs(config_dir)

    log_dir = settings['log_dir']
    if not lexists(log_dir):
        makedirs(log_dir)

    wthr_dir = settings['wthr_dir']
    wthr_mess = 'weather and climate data location'
    if not lexists(wthr_dir):
        print(ERROR_STR + wthr_mess + ': ' + wthr_dir + ' must exist')

    # report settings
    # ===============
    print('Resource location:')
    print('\tconfiguration file: ' + config_dir)
    print('\t' + wthr_mess + ': ' + wthr_dir)
    print('')

    return settings

def read_config_file(form):
    """
    read widget settings used in the previous programme session from the config file, if it exists,
    or create config file using default settings if config file does not exist
    """
    func_name =  __prog__ +  ' read_config_file'

    config_file = form.settings['config_file']
    if exists(config_file):
        try:
            with open(config_file, 'r') as fconfig:
                config = json.load(fconfig)
                print('Read config file ' + config_file)
        except (OSError, IOError) as e:
                print(e)
                return False
    else:
        config = _write_default_config_file(config_file)

    grp = 'user_settings'
    for key in USER_SETTINGS_LIST:
        if key not in config[grp]:
            print(ERROR_STR + 'attribute {} required for group {}\n\tin config file {}'.format(key, grp, config_file))
            sleep(sleepTime)
            exit(0)

    # displays detail
    # ===============
    form.w_combo10.setCurrentIndex(config[grp]['ssp_indx'])
    form.w_combo11.setCurrentIndex(config[grp]['gcm_indx'])

    # set check boxes
    # ===============
    if config[grp]['overwrite']:
        form.w_del_nc.setCheckState(2)
    else:
        form.w_del_nc.setCheckState(0)

    if config[grp]['pop_hist_flag']:
        form.w_pop_hist.setCheckState(2)
    else:
        form.w_pop_hist.setCheckState(0)

    if config[grp]['pop_fut_flag']:
        form.w_pop_fut.setCheckState(2)
    else:
        form.w_pop_fut.setCheckState(0)

    return True

def write_config_file(form, message_flag = True):
    """
    # write current selections to config file
    """
    config_file = form.settings['config_file']

    config = {
        'user_settings': {
            'overwrite':  form.w_del_nc.isChecked(),
            'pop_fut_flag': form.w_pop_fut.isChecked(),
            'pop_hist_flag': form.w_pop_hist.isChecked(),
            'ssp_indx': form.w_combo10.currentIndex(),
            'gcm_indx': form.w_combo11.currentIndex()
        }
    }

    with open(config_file, 'w') as fconfig:
        json.dump(config, fconfig, indent=2, sort_keys=True)
        print('Wrote configuration file: ' + config_file)

    return

def _write_default_config_file(config_file):
    """
    stanza if config_file needs to be created
    """
    default_config = {
        'user_settings': {
            'gcm_indx':0,
            'overwrite': True,
            'pop_fut_flag': True,
            'pop_hist_flag': True,
            'ssp_indx':0,
            'sims_dir': ''
        }
    }
    # create configuration file
    # =========================
    with open(config_file, 'w') as fconfig:
        json.dump(default_config, fconfig, indent=2, sort_keys=True)
        print('Wrote default configuration file: ' + config_file)

    return default_config

def _write_default_setup_file(setup_file):
    """
    stanza if setup_file needs to be created - TODO: improve
    """
    root_dir = None

    for drive in list(['D:\\','C:\\']):
        if isdir(drive):
            root_dir = join(drive, 'AbUniv\\GlobalEcosseSuite')
            break

    default_setup = {
        'setup': {
            'config_dir': join(root_dir, 'config'),
            'log_dir'   : join(root_dir, 'logs'),
            'fname_png' : join(root_dir, 'Images', 'World_small.PNG')
        }
    }
    # create setup file
    # =================
    with open(setup_file, 'w') as fsetup:
        json.dump(default_setup, fsetup, indent=2, sort_keys=True)
        print('Wrote default setup file: ' + setup_file)

    return default_setup
