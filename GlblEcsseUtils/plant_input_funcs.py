#-------------------------------------------------------------------------------
# Name:        plant_input_funcs.py
# Purpose:     script to read Astley's file and create new one with just MU_GLOBALS and Lat Longs
# Author:      Mike Martin
# Created:     31/07/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'plant_input_funcs.py'
__version__ = '0.0.0'

# Version history
# ---------------
#
from os.path import isdir, join, normpath, isfile, splitext, split
from os import remove
import sys
import numpy as nd
from pandas import read_csv
from random import random
from csv import reader

REQUIRED_FIELDS = list(['mu_global', 'gran_lat', 'gran_lon'])
WARNING_STR = '*** Warning *** '

def _fetch_annual_plant_inputs(strt_year, nyears, gran_lat, gran_lon, pi_df):
    '''
    sum each year
    '''
    pi_ann = {}
    locat = pi_df.loc[(pi_df['gran_lat'] == gran_lat) & (pi_df['gran_lon'] == gran_lon)]
    if len(locat.values) == 0:
        return None

    len_locat = len(locat.values[0])
    yr = strt_year
    for indx in range(5, len_locat, 12):
        pi_ann[str(yr)] = locat.values[0][indx:indx+12].sum()
        yr += 1

    return pi_ann

def convert_joe_plant_inputs_to_nc(fname):
    '''
    plant inputs are for 21 years - 252 values
    start year is 2020
    monthly values - convert to annual, write NC file
    '''

    # get header fields and start year
    # ================================
    with open(fname) as csv_fobj:
        csv_reader = reader(csv_fobj, delimiter = ' ')
        for header in csv_reader:

            # check the header list for compliance
            # ====================================
            for fld in REQUIRED_FIELDS:
                if fld not in header:
                    print('Field: ' + fld +  ' must be in header: ' + ', '.join(header[:6]))
                    return False

            # start year and number of years
            # ==============================
            strt_year = int(header[5].split('.')[0].lstrip('X'))
            nfields = len(header)
            nyears = int(nfields/12)

            nflds_lctn = nfields % 12
            if nflds_lctn != 5:
                print(WARNING_STR + 'should be 5 location fields, got ' + str(nflds_lctn))
            print(f'Location fields: {", ".join(header[:5])}')


            break

    # convert to int
    # ==============
    data_frame = read_csv(fname, sep = ' ', names = header, skiprows=1, usecols = range(1,nfields + 1))
    for metric in list(['mu_global', 'gran_lat', 'gran_lon']):
        data_frame[metric] = data_frame[metric].astype(str).astype(int)

    # generate 20 randon coordinates
    # ==============================
    gran_vals = {}
    max_vals = 20
    for metric in list(['gran_lat', 'gran_lon']):
        gran_vals[metric] = []
        val_max = data_frame[metric].max()
        val_min = data_frame[metric].min()
        span = val_max - val_min
        for ic in range(max_vals):
            gran_vals[metric].append(int(val_min + random()*span))

    for gran_lat, gran_lon in zip(gran_vals['gran_lat'], gran_vals['gran_lon']):
        pi_ann = _fetch_annual_plant_inputs(strt_year, nyears, gran_lat, gran_lon, data_frame)
        if pi_ann is None:
            print('No data at cordinates: gran_lat: {}\tgran_lon: {}'.format(gran_lat, gran_lon))
        else:
            print(str(pi_ann))

    print('Processed ' + fname)

    return True

def _open_file_sets(fert_fname, df_columns, remove_flag = True):
    '''
    for each field create and open a new file
    return file objects
    '''
    prefix = 'FERT_APPL_'
    path_name, fert_short = split(fert_fname)
    key_list = []
    fert_fobjs = {}
    for field in df_columns[2:]:
        fname = join(path_name, prefix + field + '.txt')
        if isfile(fname):
            if remove_flag:
                remove(fname)
                print('Deleted ' + fname)
            else:
                print('Fertiliser file ' + fname + ' already exists')
                return -1

        fert_fobjs[field] = open(fname, 'w')

    return fert_fobjs

def split_filter_fertiliser(form):
    '''
    check and filter an existing fertiliser file then write result to a new fertiliser file
    '''
    '''
    # read the CSV of fertilisers
    # ===========================
    '''
    fert_fname = form.w_lbl07.text()
    data_frame = read_csv(fert_fname, sep = '\t')
    nlines = len(data_frame)
    print('Read {} lines from fertiliser_file'.format(nlines))
    if 'lon' not in data_frame.columns or 'lat' not in data_frame.columns:
        print('Fertiliser file ' + fert_fname + ' must have fields lon and lat')
        return

    # output file objects
    # ===================
    columns = data_frame.columns
    fert_fobjs = _open_file_sets(fert_fname, columns)

    for rec in data_frame.values:
        for field, val in zip(columns[2:], rec[2:]):

            if not nd.isnan(val):
                out_rec = '{}\t{}\t{}\n'.format(rec[0], rec[1], rec[5])
                fert_fobjs[field].write(out_rec)

    for field in fert_fobjs:
        fert_fobjs[field].close()

    print('Finished writing {} files'.format(len(fert_fobjs)))

    return

def split_check_sowing_dates(form):
    '''
    check, filter and split existing sowing dates file then write result to a new sowing dates file
    '''
    remove_flag = True

    # read the CSV of fertilisers
    # ===========================
    headers = ['lon', 'lat', 'year', 'sow_day', 'harv_day']
    sowing_fname = form.w_lbl09.text()

    # comma is used as default delimiter or separator while parsing file
    # ==================================================================
    data_frame = read_csv(sowing_fname, sep = ' ', names = headers)

    nlines = len(data_frame)
    print('Read {} lines from sowing and harvest dates file'.format(nlines))
    if 'lon' not in data_frame.columns or 'lat' not in data_frame.columns:
        print('Sowing and harvest datesfile ' + sowing_fname + ' must have fields lon and lat')
        return

    # make sure input file is not overwritten
    # =======================================
    prefix = 'SOWING_HARVEST_DATES'
    path_name, sowing_short = split(sowing_fname)
    root_name, extn = splitext(sowing_short)
    filter_name = root_name.rstrip('_VB') + '_FILTERED.txt'

    fname = join(path_name, filter_name)
    if isfile(fname):
        if remove_flag:
            remove(fname)
            print('Deleted ' + fname)
        else:
            print('Sowing dates file ' + fname + ' already exists')
            return -1

    fobj = open(fname, 'w')
    nfilter = 0
    for nline, rec in enumerate(data_frame.values):
        lon = rec[0]
        year = rec[2]
        sow_day = rec[3]
        harv_day = rec[4]

        if nd.isnan(lon) or nd.isnan(year) or nd.isnan(sow_day) or nd.isnan(harv_day):
            nfilter += 1
        else:
            out_rec = '{}\t{}\t{}\t{}\t{}\n'.format(rec[0], rec[1], year, sow_day, harv_day)
            fobj.write(out_rec)

    fobj.close()
    print('Finished writing ' + fname + ' after filtering {} lines'.format(nfilter))

    return

def add_vigour(form):

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

def regrid_yields(form):
    '''
    # create regridded yields file suitable for global Ecosse
    '''
    separator = ','
    ngranularity = 120

    # read Hwsd AOI and plant input file
    # ==================================
    hwsd_file = form.hwsd_file
    df = read_csv(hwsd_file, sep = separator)
    lines_hwsd = df.values
    del (df)
    ngrid_cells = len(lines_hwsd)

    yields_file = form.yields_file
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
                                                                find_nearest_grid_cell(yield_data, gran_lat, gran_lon)
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

def find_nearest_grid_cell(yield_data, gran_lat, gran_lon):
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

