#-------------------------------------------------------------------------------
# Name:        ecosse_related_utils_2.py
# Purpose:     script to read Astley's file and create new one with just MU_GLOBALS and Lat Longs
# Author:      Mike Martin
# Created:     31/07/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'ecosse_related_utils_2.py'
__version__ = '0.0.0'

# Version history
# ---------------
#
from os.path import isdir, join, isfile, split
from os import remove, walk
from glob import glob
from math import exp
from pandas import read_csv
from statistics import mean
from time import time
from sys import stdout
from subprocess import check_output

month_days = [31,28,31,30,31,30,31,31,30,31,30,31]
ngranularity = 120
sleepTime = 2

rescale_factor = {'Arable': 0.44, 'Grassland':0.44, 'Forestry':0.8, 'Semi-natural':0.44, 'Miscanthus':1.6, 'SRC':0.88}
fractions      = {'Arable': 0.53, 'Grassland':0.71, 'Forestry':0.8, 'Semi-natural':0.8,  'Miscanthus':0.3, 'SRC':0.23}
WC_PATH = 'E:\\Freeware\\UnxUtils\\usr\\local\\wbin\\wc.exe'
REGIONS = list(['North_America', 'South_America', 'Europe_and_West_Asia','Asia', 'Australia_and_NZ', 'Africa'])

def check_sv_runs(form, sims_root_dir):
    '''
    for each region collect a list of runs, each run corresponding to a smulations directory
    if a co2 file exists then check number of lines
    '''

    root_out_dir = 'F:\\GlobalEcosseOutputs\\EcosseOutputs'
    regions = list(['South_America', 'Europe_and_West_Asia'])
    out_fname = 'E:\\temp\\sv_runs.txt'
    if isfile(out_fname):
        remove(out_fname)

    fout_obj = open(out_fname, 'w')

    for region in regions:

        if region ==  'Australia_and_NZ':
            tmp_list = glob(root_out_dir + '\\' + region + '*')
        else:
            tmp_list = glob(root_out_dir + '\\' + region + '*Wheat0*')

        fout_obj.write('Region: ' + region + '\n')

        runs_list = []
        nlines = 0
        no_find = 0
        for dir_name in tmp_list:
            if isdir(dir_name):
                runs_list.append(dir_name)

        print('Found {} wheat directories for region {}'.format(len(runs_list), region))
        for out_dir in runs_list:
            cut_outdir = join(out_dir, 'cut_outdir')
            co2_fnames = glob(cut_outdir + '\\*_co2*.txt')
            if len(co2_fnames) == 0:
                print('No co2 file found in ' + cut_outdir)
                no_find += 1
            else:
                co2_fname = co2_fnames[0]
                sbytes = check_output([WC_PATH, "-l", co2_fname])
                slines = sbytes.split()[0].decode()
                fout_obj.write('\t' + slines + ' lines in co2 file in ' + cut_outdir.lstrip(root_out_dir) + '\n')
                nlines += 1

        print('*** co2 file found in {} directories\tno finds: {} ***\n'.format(nlines, no_find))

    fout_obj.close()
    

    return

def clean_sv_runs(sims_root_dir):
    '''
    remove spurious fort.123 files - liberates disk space
    '''
    fname_list = glob(sims_root_dir + '\\*Wheat*')

    n_dirs_clean = 0
    for dir_name in fname_list:
        if isdir(dir_name):
            for directory, subdirs_raw, files in walk(dir_name):
                num_sims = len(subdirs_raw)
                max_isim = num_sims - 1
                break
            del directory
            del files

            # filter weather directories to leave only simulation directories
            # ===============================================================
            last_time = time()
            for subdir in subdirs_raw:
                if subdir[:5] == 'lat00':
                    fort_list = glob(dir_name + '\\' + subdir + '\\fort.[0-9]*')
                    for fn in fort_list:
                        os.remove(fn)
                    n_dirs_clean += 1

                if time() - last_time > sleepTime:
                    stdout.write('\rCleaned: {:=8d} directories'.format(n_dirs_clean))
                    last_time = time()
    return

def _miami_dyce(land_use ,temp, precip):
    '''
    modification of the miami model by altering coefficients (no need to reparameterise exponent terms since model
                                                                    is effectively linear in climate range of the UK)
    multiply npp values according to land cover type:
        semi-natural (4), grassland (2), arable (1): forest/2               (Ecology, 89(8), 2008, pp. 2117-2126)
        Miscanthus (5): multiply by 1.6 (from comparison of unadjusted Miami results with Miscanfor peak yield results)
        SRC (6): as forest - peak yield is just over half that of Miscanthus)

    for plant inputs to soil, multiply npp values by different fractions according to land cover; sum of net biome
                                                                                        productivities divided by npp)
    Miscanthus: 0.3 (widely reported as losing around 1/3 of peak mass before harvest; small amount returns to rhizome)
    SRC: 0.15 (assumed as forest)
    '''
    nppt = 3000/(1 + exp(1.315 - 0.119*temp))
    nppp = 3000*(1 - exp(-0.000664*precip))
    npp = 0.5*10*rescale_factor[land_use]*min(nppt, nppp)  # times 10 for unit conversion (g/m^2 to Kg/ha) and .5 for C

    soil_input = fractions[land_use]*npp     # soil input of vegetation

    return npp


def check_npp(form):

    lat_lon_fn = form.w_lbl05.text()
    sims_dir, short_fname = split(lat_lon_fn)
    sims_dir += '\\one_site'

    land_use = 'Arable'
    wthr_dirs = glob(sims_dir + '\\[0-9]*')
    for wthr_dir in wthr_dirs:
        dummy, sdir = split(wthr_dir)
        gran_lat, gran_lon = sdir.split('_')

        # open all met files
        # ==================
        npp_list = []
        met_files = glob(wthr_dir + '\\met*s.txt')
        for met_fn in met_files:
            df = read_csv(met_fn, sep='\t', names=['mnth', 'precip', 'pet', 'temp'])
            for rec in df.values:
                precip = 10*rec[1]
                temp = rec[3]
                npp = _miami_dyce(land_use, temp, precip)
                npp_list.append(npp/12)

    print('mean :', mean(npp_list))
    return

def convert_latlons(form):
    '''
    read comma separated file comprising lat/lon pairs and write tab separated granular lat lons
    '''
    lat_lon_fn = form.w_lbl05.text()
    out_dir, short_fname = split(lat_lon_fn)

    with open(lat_lon_fn, 'r') as fobj:
        lines = fobj.readlines()

    gran_latlon_fn = join(out_dir, 'gran_latlons_'+ short_fname)
    fobj_out = open(gran_latlon_fn, 'w')

    for line in lines:
        location, slat, slon = line.rstrip('\n').split(',')
        lat = float(slat)
        lon = float(slon)
        gran_lat = int(round((90.0 - lat) * ngranularity))
        gran_lon = int(round((180.0 + lon) * ngranularity))
        line_out = '{}\t{}\t{}\t{:d}\t{:d}\n'.format(location, slat, slon, gran_lat, gran_lon)
        fobj_out.write(line_out)

    fobj_out.close()
    print('Created granular lat lon file: {}'.format(gran_latlon_fn))

    return

def convert_met_files(form):
    '''
    Ecosse met file consists of timestep, rain (mm), PET, temperature (deg C)
    convert from daily to monthly
    '''
    ref_dir = form.w_lbl04.text()

    dirs = []
    met_files = glob(ref_dir + '/met*.txt')
    for fname in met_files:
        fobj = open(fname, 'r')
        fname_out = join(ref_dir, 'met_mnthly.txt')
        fobj_out = open(fname_out, 'w')
        lines = fobj.readlines()

        indx1 = 0
        for imnth, ndays in enumerate(month_days):
            indx2 = indx1 + ndays
            one_month = lines[indx1:indx2]
            # print('{:3d} {:3d} {:3d}'.format(indx1, indx2, len(one_month)))

            # step through each day, summing precipitation and temperature
            sum_tmp = 0.0
            sum_pet = 0.0
            sum_pre = 0.0
            for line in one_month:
                dummy, pre_str, pet_str, tmp_str = line.rstrip('\n').split('\t')
                sum_pre += float(pre_str)
                sum_pet += float(pet_str)
                sum_tmp += float(tmp_str)

            ave_tmp = sum_tmp/ndays
            ave_pet = sum_pet/ndays
            line_out = '{}\t{:.1f}\t{:.1f}\t{:.1f}\n'.format(imnth + 1, sum_pre, ave_pet, ave_tmp )
            fobj_out.write(line_out)
            indx1 = indx2

        fobj.close()
        fobj_out.close()
        break

    print('Processed {} met files'.format(len(met_files)))

    return
