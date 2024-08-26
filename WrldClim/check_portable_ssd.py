# -------------------------------------------------------------------------------
# Name:        nc_low_level_fns.py
# Purpose:     Functions to create and write to netCDF files and return latitude and longitude indices
# Author:      Mike Martin
# Created:     25/01/2020
# Description: taken from netcdf_funcs.py in obsolete project PstPrcssNc
# Licence:     <your licence>
# -------------------------------------------------------------------------------

__prog__ = 'check_portable_ssd.py'
__version__ = '0.0.0'
__author__ = 's03mm5'

from os.path import isfile, splitext, join, isdir, split
from os import listdir

def check_ssd_transfer(form):
    """
    Check and repair local RCP weather
    Copy data from the external SSD to effect repair
    """
    report_flag = False
    ssd_root_dir = form.settings['ssd_root_dir']
    local_root_dir = form.settings['ssd_root_dir']  #  TODO:

    # expecting ECOSSE_LTA and ECOSSE_RCP
    # ===================================
    for short_dir in listdir(local_root_dir):
        high_lvl_dir = join(local_root_dir, short_dir)

        if short_dir != 'ECOSSE_RCP':
            print('\nIgnoring high level directory: ' + high_lvl_dir)
            continue

        # gather RCP and realisation directories e.g. ['rcp26_01', 'rcp26_04', 'rcp26_06', ....]
        # ======================================================================================
        medium_lvl_dirs = listdir(high_lvl_dir)
        ndirs = len(medium_lvl_dirs)
        print('\nChecking: ' + high_lvl_dir + '\tnumber of RCPs: ' + str(ndirs) + '\n')

        for short_rcp in medium_lvl_dirs:
            rcp_dir = join(local_root_dir, short_dir, short_rcp)

            # check integrity file for this RCP and realisation e.g. rcp60_06
            # ===============================================================
            skip_fn = join(rcp_dir, 'skip_flag.txt')
            if isfile(skip_fn):
                with open(skip_fn, 'r') as fskip:
                    integrity = fskip.read()
                    if integrity == 'OK':
                        if report_flag:
                            print(rcp_dir + ' is OK')
                        continue

            # gather site directories for this RCP and realisation e.g. 100500_478500
            # =======================================================================
            ngood_coords, nbad_coords = 2*[0]
            bad_coords_dict = {}
            for coord_dir in listdir(rcp_dir):
                long_coord_dir = join(rcp_dir, coord_dir)
                if isdir(long_coord_dir):
                    nfiles = len(listdir(long_coord_dir))
                    if nfiles == 60:
                        ngood_coords += 1
                    else:
                        nbad_coords += 1
                        bad_coords_dict[coord_dir] = nfiles

            # report and repair
            # =================
            print('\t' + short_rcp + ' has {} good and {} bad coords'.format(ngood_coords, nbad_coords))
            if nbad_coords == 0:
                with open(skip_fn, 'w') as fskip:
                    fskip.write('OK')
            else:
                print('bad coords: ' + str(bad_coords_dict) + '\n')
                with open(skip_fn, 'w') as fskip:
                    fskip.write('Bad')

    return
