#-------------------------------------------------------------------------------
# Name:        common_funcs.py
# Purpose:     script to read Astley's file and create new one with just MU_GLOBALS and Lat Longs
# Author:      Mike Martin
# Created:     31/07/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'common_funcs.py'
__version__ = '0.0.0'

# Version history
# ---------------
# 
# import csv
from os.path import isdir, join, exists, split
from json import load as json_load, dump as json_dump
import glob
from unidecode import unidecode
import subprocess

def remove_non_ascii_chars(text_inp):
    '''
    # remove any non-ASCII characters
    '''
    return ''.join(i for i in text_inp if ord(i) < 128)

def process_zip_files(form):

    # read three-letter country codes and corresponding country names defined in ISO 3166-1
    fobj = open(form.codes_fname)
    lines = fobj.readlines()
    fobj.close()

    # step through each line
    country_dict = {}
    for nline, line in enumerate(lines):
        try:
            line_content = line.rstrip('\n')
            line_content_list = line_content.split(',')
            iso = remove_non_ascii_chars(line_content_list[0])   # not necessary
            country = line_content_list[1].strip('"')
        except ValueError as e:
            print('Could not extract iso and country for line {} {}'.format(nline,line_content))
            continue

        if len(iso) == 3:
            country_dict[iso] = country
        else:
            print('Bad iso {} for country {}'.format(iso,country))

    print('Identified {} countries from country codes file'.format(len(country_dict)))

    # decompression
    # =============
    # return all zip files from zip directory
    zip_files = glob.glob(form.zip_dir + '\\*.zip')
    nfound = 0
    for zip_file in zip_files:
        #
        zip_dir, zip_fname = split(zip_file)
        iso_code = zip_fname[0:3]
        if iso_code in country_dict.keys():
            nfound += 1
            country_name = unidecode(country_dict[iso_code])
        else:
            if iso_code == 'XKO':
                country_name = 'Kosovo'
            elif iso_code == 'XNC':
                country_name = 'Northern Cyprus'
            else:
                print('ISO code {} not found in countries dictionary'.format(iso_code))
                continue

        # x : eXtract files with full paths
        out_dir = join(form.cntry_shp_dir,country_name)

        if isdir(out_dir):
            print('\tdirectory ' + out_dir + ' already exists - will skip')
            continue

        output = subprocess.check_output([form.decompressor,'x','-o' + out_dir, zip_file])
        break

    print('found {} countries from countries dictionary out of total of {} zip files'.format(nfound,len(zip_files)))

    return

def _read_config_file(form):

    # read names of files used in the previous programme session from the config file if it exists
    # or create default using the current selections if config file does not exist
    config_file = form.config_file
    if exists(config_file):
        try:
            with open(config_file, 'r') as fconfig:
                config = json_load(fconfig)
        except (OSError, IOError) as e:
                print(e)
                return False
    else:
        # config file does not exists
        # data_dir = form.data_dir
        # out_res_dir =  data_dir + 'Ecosse_Spag'

        # form.ref_dir = join(out_res_dir + '\\site_spag', dfltFname) # file containing reference outputs

        # stanza if config_file needs to be created
        _default_config = {
            'FortDir': {
                 'ref_dir': form.ref_dir
            }
        }

        # if config file does not exist then create it...
        with open(config_file, 'w') as fconfig:
            json_dump(_default_config, fconfig, indent=2, sort_keys=True)
            config = _default_config

    grp = 'FortDir'
    form.ref_dir = config[grp]['ref_dir']

    return

def _write_config_file(form):

    config_file = form.config_file

    # grp = 'Files'

    config = {
        'FortDir': {
            'ref_dir': form.ref_dir
            }
        }

    with open(config_file, 'w') as fconfig:
        json_dump(config, fconfig, indent=2, sort_keys=True)

    return


