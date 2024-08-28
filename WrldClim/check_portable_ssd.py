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

from shutil import copytree
from os.path import isfile, splitext, join, isdir, split
from os import listdir

ECOSSE_LTA = 'ECOSSE_LTA'
ECOSSE_RCP = 'ECOSSE_RCP'
MAX_BAD_COORDS = 10

def check_ssd_transfer(form):
    """
    Check and repair local RCP weather
    Copy data from the external SSD to effect repair
    """
    report_flag = False
    ssd_src_dir = form.settings['ssd_src_dir']
    dest_root_dir = form.settings['ssd_dest_dir']

    # establish definitive list of coords
    # ===================================
    lta_src_dir = join(ssd_src_dir, ECOSSE_LTA)
    rcps = listdir(lta_src_dir)
    all_coords = listdir(join(lta_src_dir, rcps[0]))

    # expecting ECOSSE_LTA and ECOSSE_RCP
    # ===================================
    print('\n')
    for short_dir in listdir(dest_root_dir):
        high_lvl_dir = join(dest_root_dir, short_dir)

        if short_dir != ECOSSE_RCP:
            if isfile(high_lvl_dir):
                ftype = 'file'
            else:
                ftype = 'directory'
            print('Ignoring high level ' + ftype + ': ' + high_lvl_dir)
            continue

        # gather RCP realisation directories e.g. ['rcp26_01', 'rcp26_04', 'rcp26_06', ....]
        # ==================================================================================
        medium_lvl_dirs = listdir(high_lvl_dir)
        ndirs = len(medium_lvl_dirs)
        print('\nChecking: ' + high_lvl_dir + '\tnumber of RCPs: ' + str(ndirs))

        for short_rcp in medium_lvl_dirs:
            rcp_dest_dir = join(high_lvl_dir, short_rcp)
            rcp_src_dir = join(ssd_src_dir, ECOSSE_RCP, short_rcp)

            # check integrity file for this RCP and realisation e.g. rcp60_06
            # ===============================================================
            skip_fn = join(rcp_dest_dir, 'skip_flag.txt')
            if isfile(skip_fn):
                with open(skip_fn, 'r') as fskip:
                    integrity = fskip.read()
                    if integrity == 'OK':
                        if report_flag:
                            print(rcp_dest_dir + ' is OK')
                        continue

            # gather site directories for this RCP and realisation e.g. 100500_478500
            # =======================================================================
            ngood_coords, nbad_coords, ncopy_coords = 3*[0]
            bad_coords_dict = {}
            coord_dirs = listdir(rcp_dest_dir)
            for coord_dir in coord_dirs:
                long_coord_dir = join(rcp_dest_dir, coord_dir)
                if isdir(long_coord_dir):
                    nfiles = len(listdir(long_coord_dir))
                    if nfiles == 60:
                        ngood_coords += 1
                    else:
                        # try copying across missing coord files
                        # ======================================
                        src_dir_coord = join(rcp_src_dir, coord_dir)
                        if isdir(src_dir_coord):
                            copytree(src_dir_coord, join(rcp_dest_dir, coord_dir))
                            ncopy_coords += 1
                        else:
                            if nbad_coords < MAX_BAD_COORDS:
                                print('\tCould not copy met files ' + src_dir_coord + ' does not exist')
                            nbad_coords += 1
                            bad_coords_dict[coord_dir] = nfiles

            # report and repair
            # =================
            mess = '\nAlignment of coordinates for: ' + short_rcp
            print( mess + '\t{} good\t{} bad\t{} copied'.format(ngood_coords, nbad_coords, ncopy_coords))
            if nbad_coords == 0:
                with open(skip_fn, 'w') as fskip:
                    fskip.write('OK')
            else:
                ncoords = min(MAX_BAD_COORDS, nbad_coords)
                bad_keys_str = str(list(bad_coords_dict.keys())[:ncoords])
                print('\tfirst of ' + str(ncoords) + ' bad coords: ' + bad_keys_str + '\n')
                with open(skip_fn, 'w') as fskip:
                    fskip.write('Bad')

    return
