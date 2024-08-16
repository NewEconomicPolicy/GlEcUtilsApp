# -------------------------------------------------------------------------------
# Name:        nc_low_level_fns.py
# Purpose:     Functions to create and write to netCDF files and return latitude and longitude indices
# Author:      Mike Martin
# Created:     25/01/2020
# Description: taken from netcdf_funcs.py in obsolete project PstPrcssNc
# Licence:     <your licence>
# -------------------------------------------------------------------------------

__prog__ = 'nc_low_level_fns.py'
__version__ = '0.0.0'
__author__ = 's03mm5'

from os.path import isfile, splitext, join, isdir, split
from os import listdir

def check_ssd_transfer(forms):
    """
    C
    """
    root_dir = 'G:\\PortableSSD'

    nfiles = 0
    for short_dir in listdir(root_dir):
        this_dir = join(root_dir, short_dir)
        ndirs = (len(listdir(this_dir)))
        print(this_dir + ' ' + str(ndirs))

        for subdir in listdir(join(root_dir, short_dir)):
            this_dir= join(root_dir, short_dir, subdir)
            nfiles = (len(listdir(this_dir)))
            if nfiles != 60:
                print(this_dir + ' ' + str(nfiles))

    return
