#-------------------------------------------------------------------------------
# Name:        ecosse_related_utils.py
# Purpose:     script to read Astley's file and create new one with just MU_GLOBALS and Lat Longs
# Author:      Mike Martin
# Created:     31/07/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'ecosse_related_utils.py'
__version__ = '0.0.0'

# Version history
# ---------------
#
from os.path import isdir, join, isfile, split, splitext
from os import walk, mkdir, rename, getcwd, remove, chdir
import sys
from pandas import read_csv
from time import time, sleep
import subprocess
from glob import glob
from distutils.dir_util import copy_tree

def rename_txt_to_json(ref_dir):
    '''
    change file extension from .txt to .json
    '''
    fname_list = glob(ref_dir + '/*.txt')
    for fname in fname_list:
        root_name = splitext(fname)[0]
        fname_json = root_name + '.json'
        rename(fname, fname_json)

    print('changed {} files in {}'.format(len(fname_list), ref_dir))

    return

def separate_projects(form):

    confirm_flag = form.w_cnfrm_del.isChecked()
    copy_flag = form.w_copy.isChecked()
    if copy_flag:
        action = 'copied'
    else:
        action = 'renamed'

    ref_dir = form.w_lbl04.text()
    root_dir, proj_name = split(ref_dir)
    new_proj_dir = join(root_dir, proj_name + '_ss')
    if not isdir(new_proj_dir) and confirm_flag:
        try:
            mkdir(new_proj_dir)
        except:
            print('Could not make new directory')
            return

    last_time = time()
    for directory, subdirs_raw, files in walk(ref_dir):
        num_sims = len(subdirs_raw)
        max_isim = num_sims - 1
        break
    del directory
    del files

    # check each simulation directory
    # ===============================
    subdirs = []
    for subdir in subdirs_raw:
        if subdir[0:5] == 'lat00':
            subdirs.append(subdir)
    num_sims = len(subdirs)
    del(subdirs_raw)

    # if there is a management file then record
    # =========================================
    every_nth = 10000
    nmanage = 0
    ss_sim_dirs = []
    for isub, subdir in enumerate(subdirs):
        subdir_full = join(ref_dir , subdir)
        management_fname = join(ref_dir , subdir, 'management.txt')

        # build new paths
        # ===============
        if isfile(management_fname):
            ss_sim_dirs.append(subdir_full)
            nmanage += 1

        if every_nth*int(isub/every_nth) == isub:
            if isub > 0:
                print('checked {} directories'.format(isub))

    print('Number of dirs with management files: {}\tfrom total of simulation dirs {}'.format(nmanage, num_sims))
    if confirm_flag:
        
        # move or copy to new directory
        # =============================
        every_nth = 50
        nsucces = 0
        mess = ''
        for subdir_full in ss_sim_dirs:
            dummy, subdir = split(subdir_full)
            subdir_new = join(new_proj_dir, subdir)
            if copy_flag:
                copy_tree(subdir_full, subdir_new)
                nsucces += 1
            else:
                if not isdir(subdir_new):
                    rename(subdir_full, subdir_new)
                    nsucces += 1
                else:
                    mess = subdir_new + ' already exists'

            if every_nth*int(nsucces/every_nth) == nsucces:
                if nsucces > 0:
                   print('{} {} directories'.format(action, nsucces))

        print('Finished {} - {} directories - {}'.format(action, nsucces, mess))

    return

def create_ecosse_inst(form):

    sim_dir = ''
    exe_path = ''

    retcode = 1
    # Set the working directory for the ECOSSE exe
    old_dir = getcwd()
    chdir(sim_dir)
    cmd = '{}\n\n{}\n2\n\n'.format(1, 'input.txt')
    try:
        stdout_path = join(sim_dir, 'stdout.txt')
        new_inst = subprocess.Popen(exe_path, shell=False,
                                    stdin=subprocess.PIPE,
                                    stdout=open(stdout_path, 'w'),
                                    stderr=subprocess.STDOUT)  # stdout=subprocess.PIPE

        # Provide the user input to ECOSSE
        if new_inst.stdin is not None:
            new_inst.stdin.write(bytes(cmd,"ascii"))
            new_inst.stdin.flush()
            new_inst.stdin.close()
        else:
            print('Instance is None')

    except OSError as e:
        print('Process with sim dir {} could not be launched - cmd: {}  {}'.format(sim_dir, cmd, e))

    else:
        print()

    chdir(old_dir)

    return retcode


def concat_met_files(form):

    ref_dir = form.w_lbl04.text()

    dirs = []
    met_files = []
    for fname in glob(ref_dir + '/met*.txt'):
        if isfile(fname):
            met_files.append(fname)

    print('Found {} met files'.format(len(met_files)))

    return

def add_vigour (form):

    fname = join('C:\\AbUniv\\ECOSSE_test\\ss_marta','management.txt')

    fname_vig = join('C:\\AbUniv\\ECOSSE_test\\ss_marta','management_vig.txt')
    if isfile(fname_vig):
        remove(fname_vig)
        print('Removed ' + fname_vig)

    fobj = open(fname, 'r')
    lines = fobj.readlines()

    fobj_vig = open(fname_vig, 'w')

    # read lines and then add vigoure to every third line
    # ===================================================
    nlines = 0
    last_line = len(lines) - 1
    for linenum, line in enumerate(lines):
        fobj_vig.write(line)
        nlines += 1
        if linenum > 1378:
            if int(line) == 3:
                if linenum >= last_line:
                    fobj_vig.write('\n0.1')
                else:
                    fobj_vig.write('0.1\n')
                nlines += 1

    fobj.close()
    fobj_vig.close()
    print('Wrote ' + fname_vig + ' having written {} lines'.format(nlines))

    return

def _find_nearest_grid_cell(yield_data, gran_lat, gran_lon):
    '''
    gran_lat = granular latitude of grid cell
    gran_lon = granular longitude of grid cell
    return nearest yield value for given lat, lon pair
    '''
    shortest_dist = sys.float_info.max
    for key in yield_data:

        latitude, longitude, pi_2020, pi_2030, gran_lat_pi, gran_lon_pi = yield_data[key]
        distance = pow(gran_lat_pi - gran_lat, 2) + pow(gran_lon_pi - gran_lon, 2)
        if distance < shortest_dist:
            shortest_dist = distance
            closest_yield_rec = yield_data[key]

#    print('{} {} '.format(shortest_dist, closest_yield_rec))

    return closest_yield_rec + list([shortest_dist])

def _regrid_yields(form):
    '''
    # create regridded yields file suitable for global Ecosse
    '''
    separator = ','
    ngranularity = 120

    # read Hwsd AOI and plant input file
    # ==================================
    hwsd_file = form.lbl02.text()
    df = read_csv(hwsd_file, sep = separator)
    lines_hwsd = df.values
    del (df)
    ngrid_cells = len(lines_hwsd)

    yields_file = form.lbl01.text()
    df = read_csv(yields_file, sep = separator)
    lines_yields = df.values
    del (df)
    nyields = len(lines_yields)

    # ------------------------------------------------------------------------
    print('Read plant input and HWSD AOI files - now creating list of keys...')
    yield_data = {}
    for line in lines_yields:

        latitude, longitude, pi_2020, pi_2030 = line
        gran_lat = round((90.0 - latitude)*ngranularity)
        gran_lon = round((180.0 + longitude)*ngranularity)
        key_pi = '{:0=5d}_{:0=5d}'.format(int(gran_lat), int(gran_lon))
        yield_data[key_pi] = list(line) + list([gran_lat, gran_lon])

    # ------------------------------------------------------------------------
    print('For each AOI grid cell, retrieve the nearest yield...')
    ncommon = 0
    nearby = 0
    max_dist = -999.0
    max_lines_read = 60
    for nlines_read, line in enumerate(lines_hwsd):
        gran_lat, gran_lon, mu_global, lat, lon = line
        key_hwsd = '{:0=5d}_{:0=5d}'.format(int(gran_lat), int(gran_lon))
        if key_hwsd in yield_data:
            # NB. latitude, longitude, gran_lat_pi, gran_lon_pi should respectively be same as gran_lat, gran_lon, lat, lon
            latitude, longitude, pi_2020, pi_2030, gran_lat_pi, gran_lon_pi = yield_data[key_hwsd]
            ncommon += 1
        else:
            latitude, longitude, pi_2020, pi_2030, gran_lat_pi, gran_lon_pi, distance  = \
                                                            _find_nearest_grid_cell(yield_data, gran_lat, gran_lon)
            if distance > max_dist:
                max_dist = distance
            nearby += 1

        if 100*int(nlines_read/100.0) == nlines_read:
            print('Processed: {} lines of AOI data\tcommon lines: {}\tnearby: {}'.format(nlines_read + 1, ncommon, nearby))

        if nlines_read > max_lines_read:
            break

    print('Read {} HWSD grid cells, found {} corresponding PIs and {} nearby from {} values\tapprox max dist: {} arc seconds'
                                        .format(ngrid_cells, ncommon, nearby, nyields, int(30.0*pow(max_dist, 0.5))))

    return True
