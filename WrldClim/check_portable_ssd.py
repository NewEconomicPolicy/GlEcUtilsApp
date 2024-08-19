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
    C
    """
    root_dir = form.settings['ssd_root_dir']

    nfiles = 0
    for short_dir in listdir(root_dir):
        high_lvl_dir = join(root_dir, short_dir)
        if short_dir == 'ECOSSE_RCP':
            high_lvl_dirs = listdir(high_lvl_dir)
            ndirs = len(high_lvl_dirs)
            print(high_lvl_dir + ' N RCPs: ' + str(ndirs))

            for short_rcp in high_lvl_dirs:
                rcp_dir = join(root_dir, short_dir, short_rcp)
                ngood_coords, nbad_coords = 2*[0]
                bad_coords_dict = {}
                for coord_dir in listdir(rcp_dir):
                    long_coord_dir = join(rcp_dir, coord_dir)
                    nfiles = len(listdir(long_coord_dir))
                    if nfiles == 60:
                        ngood_coords += 1
                    else:
                        nbad_coords += 1
                        bad_coords_dict[coord_dir] = nfiles

                print(rcp_dir + ' has {} good and {} bad coords'.format(ngood_coords, nbad_coords))
                if nbad_coords > 0:
                    print('bad coords: ' + str(bad_coords_dict) + '\n')
        else:
            print('Ignoring ' + high_lvl_dir)

    return
