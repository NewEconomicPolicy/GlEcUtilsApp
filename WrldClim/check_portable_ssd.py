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

from shutil import copytree, rmtree
from os.path import isfile, splitext, join, isdir, split
from os import listdir, getcwd, chdir
from subprocess import Popen, PIPE, STDOUT
from time import time, sleep

ERROR_STR = '*** Error *** '
ECOSSE_LTA = 'ECOSSE_LTA'
ECOSSE_RCP = 'ECOSSE_RCP'
MAX_BAD_COORDS = 10

ARCHIVER_7Z_EXE = 'C:\\Program Files\\7-Zip\\7z.exe'

def zip_rcps(form):
    """
    extend PATH env var:     set PATH=%PATH%;C:\Program Files\7-Zip
    7z a rcp45_04.zip *
    https://documentation.help/7-Zip-18.0/start.htm
    """
    if not isfile(ARCHIVER_7Z_EXE):
        print(ERROR_STR + ARCHIVER_7Z_EXE + ' does not exist')
        return

    src_dir = form.w_lbl_srcdir.text()
    out_dir = join(split(src_dir)[0], 'zipfiles')
    for rcp_short in listdir(src_dir):
        src_rcp_dir = join(src_dir, rcp_short)
        if not isdir(src_rcp_dir):
            print('Skipping ' + src_rcp_dir)
            continue

        out_fn = join(out_dir, rcp_short)
        out_fn_zip = out_fn + '.zip'
        if isfile(out_fn_zip):
            print(out_fn_zip + ' exists, will skip')
        else:
            print('\nCreating: ' + out_fn_zip + '\tfrom:\t' + src_rcp_dir)
            t1 = time()
            curr_dir = getcwd()
            chdir(src_rcp_dir)
            try:
                cmd = ARCHIVER_7Z_EXE + ' a ' + rcp_short + '.zip ' + ' * '
                new_inst = Popen(cmd, shell=False, stdin=PIPE, stderr=STDOUT)
            except OSError as err:
                print(ERROR_STR + str(err))
            else:
                t2 = time()
                print('Created: ' + out_fn_zip + ' after: ' + str(int((t2 - t1) / 60)) + ' minutes')

                sleep(2)
                while True:
                    if new_inst.poll() is None:
                        print('job ' + str(new_inst.pid) + ' is still running')
                        sleep(5)
                    else:
                        break

            chdir(curr_dir)
    return

def check_ssd_transfer(form):
    """
    Check the integrity of and repair any incomplete RCP weather cells for the destination instance
    Copy data from the external SSD to effect repair
    Assumption: all grid cell coordinates have been transferred but some may be incomplete
                                                            i.e. have less than 60 weather files
    """
    report_only = True
    ssd_src_dir = form.settings['ssd_src_dir']
    dest_root_dir = form.settings['ssd_dest_dir']
    print('\nSanDisk source: ' + ssd_src_dir + '\tDestination directory: ' + dest_root_dir)

    # establish definitive list of coords
    # ===================================
    lta_src_dir = join(ssd_src_dir, ECOSSE_LTA)
    rcps = listdir(lta_src_dir)
    all_coords = listdir(join(lta_src_dir, rcps[0]))
    nall_coords = len(all_coords)

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
                        print(rcp_dest_dir + ' is OK')
                        continue

            # gather site directories for this RCP and realisation e.g. 100500_478500
            # =======================================================================
            ngood_coords, nbad_coords, ncopy_coords = 3*[0]
            bad_coords_dict = {}
            coord_dirs = listdir(rcp_dest_dir)

            ncoord_dirs = len(coord_dirs)
            print('\nDestination ' + short_rcp + ' has {} coords, expected: {}'.format(ncoord_dirs, nall_coords))

            for coord_dir in coord_dirs:
                dest_dir_coord = join(rcp_dest_dir, coord_dir)
                if isdir(dest_dir_coord):
                    nfiles = len(listdir(dest_dir_coord))
                    if nfiles == 60:
                        ngood_coords += 1
                    else:
                        # try copying across missing coord files
                        # ======================================
                        src_dir_coord = join(rcp_src_dir, coord_dir)
                        if isdir(src_dir_coord):
                            if report_only:
                                print('nfiles: ' + str(nfiles) + '\tWill copy ' + src_dir_coord + ' to ' ,
                                      dest_dir_coord)
                            else:
                                rmtree(dest_dir_coord)
                                copytree(src_dir_coord, dest_dir_coord)
                                print('Copied ' + src_dir_coord + ' to ', dest_dir_coord)
                            ncopy_coords += 1
                        else:
                            if nbad_coords < MAX_BAD_COORDS:
                                print('\tCould not copy met files ' + src_dir_coord + ' does not exist')
                            nbad_coords += 1
                            bad_coords_dict[coord_dir] = nfiles

            # report and repair
            # =================
            mess = 'Alignment of coordinates for: ' + short_rcp
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

            print('\n')

    return
