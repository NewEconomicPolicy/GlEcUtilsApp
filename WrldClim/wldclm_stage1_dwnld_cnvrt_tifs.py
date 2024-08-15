#-------------------------------------------------------------------------------
# Name:        eclips_classes.py
# Purpose:     Functions to create and write to netCDF files and return latitude and longitude indices
# Author:      Mike Martin
# Created:     25/01/2017
# Description: create dimensions: "longitude", "latitude" and "time"
#              create five ECOSSE variables i.e. 'n2o','soc','co2', 'no3', and 'ch4'
# Licence:     <your licence>
#-------------------------------------------------------------------------------

__prog__ = 'wldclm_stage1_dwnld_cnvrt_tifs.py'
__version__ = '0.0.0'
__author__ = 's03mm5'

from os.path import isfile, splitext, join, isdir, split
from os import remove, chdir, getcwd, makedirs, mkdir
from time import strftime, sleep
from datetime import timedelta
from netCDF4 import Dataset
from numpy import array
from subprocess import call
from zipfile import ZipFile, BadZipFile
from glob import glob
from osgeo.gdal import Translate, UseExceptions
from time import time

from nc_low_level_fns import generate_mnthly_atimes

sleepTime = 3

WARNING_STR = '*** Warning *** '
ERROR_STR = '*** Error *** '

MISSING_VALUE = -999.0
METRICS = list(['prec', 'tmax', 'tmin'])

WGET = 'D:\\Freeware\\UnxUtils\\usr\\local\\wbin\\wget.exe'

ROOT_DIR = 'D:\\WldClim\\'

URL_ROOT = 'https://geodata.ucdavis.edu/'       # useful URL: https://geodata.ucdavis.edu/climate/worldclim/2_1/

# ================= future climate =====================================
ROOT_DIR_FUT = ROOT_DIR + 'Fut\\'

URL_FUT = URL_ROOT + 'cmip6/10m/'
SSP = 'ssp585'
PERIODS_FUT = list(['2021-2040', '2041-2060', '2061-2080', '2081-2100'])

# ================= historic weather =====================================
ROOT_DIR_HIST = ROOT_DIR + 'Hist\\'

URL_HIST = URL_ROOT + 'hist/cts4.06/10m/'
PERIODS_HIST = list(['1950-1959', '1960-1969', '1970-1979', '1980-1989', '1990-1999',
                                                '2000-2009', '2010-2019', '2020-2021'])

# ============================================================================
def download_fut_tifs(form, gcm, ssp):
    """
    C
    """
    delete_flag = form.w_del_nc.isChecked()
    initial_dir, tif_dir, nc_dir, stdout_fname = _setup_downloads(ROOT_DIR_FUT, gcm, ssp)

    print('\nDownloading future climate datasets for gcm: ' + gcm + '\tssp: ' + ssp)
    ndown_load = 0
    for metric in METRICS:
        for period in PERIODS_FUT:
            fn = 'wc2.1_10m_' + metric + '_' + gcm + '_ssp' + ssp + '_' + period + '.tif'
            out_fn = join(tif_dir, fn)
            if isfile(out_fn):
                mess = WARNING_STR + fn + ' already exists'
                if delete_flag:
                    print(mess + ' - will delete')
                    try:
                        remove(out_fn)
                    except PermissionError as err:
                        print(ERROR_STR + str(err))
                        return None
                else:
                    print(mess)
                    continue

            url = URL_FUT + gcm + '/ssp' + ssp + '/' + fn
            cmd = WGET + ' -q ' + url
            if not form.w_rprt_only.isChecked():
                tstrt = time()
                call(cmd)
                ndown_load += 1
                print('Downloaded ' + fn + ' time taken: ' + str(timedelta(seconds=int(time() - tstrt ))) )

    print('\ndownloaded: {} files to {}'.format(ndown_load, tif_dir))

    # convert tifs to NC
    # ==================
    nc_dir = join(ROOT_DIR, 'Fut', gcm, ssp, 'NCs')
    _cnvrt_tif_wthr_ncs(tif_dir, nc_dir)

    return

def download_hist_tifs(form):
    """
    download and unzip
    """
    initial_dir, tif_dir, nc_dir, stdout_fname = _setup_downloads(ROOT_DIR_HIST)

    print('Downloading historic datasets')
    ndown_load = 0
    for metric in METRICS:
        for period in PERIODS_HIST:
            fn = 'wc2.1_cruts4.06_10m_' + metric + '_' + period + '.zip'
            out_fn = join(tif_dir, fn)
            if isfile(out_fn):
                print(WARNING_STR + fn + ' already exists')
                continue

            url = URL_HIST + fn
            cmd = WGET + ' -q ' + url
            if not form.w_rprt_only.isChecked():
                tstrt = time()
                call(cmd)
                ndown_load += 1
                print('Downloaded ' + fn + ' time taken: ' + str(timedelta(seconds=int(time() - tstrt))))

    print('\ndownloaded: {} files to {}'.format(ndown_load, tif_dir))
    # _downloads_user_feedback(ndown_load, tif_dir, initial_dir)

    unzip_hist_tifs(tif_dir)
    cnvrt_hist_to_ncs(tif_dir, nc_dir)

    return

def _setup_downloads(root_dir, gcm=None, ssp=None):
    """
    works for both historic and gcm data
    """
    if gcm is None:     # historic
        nc_dir = join(root_dir, 'NCs')
        tif_dir = join(root_dir, 'tifs')
    else:               # gcm data
        nc_dir = join(root_dir, gcm, ssp, 'NCs')
        tif_dir = join(root_dir, gcm, ssp, 'tifs')

    if not isdir(tif_dir):
        makedirs(tif_dir, exist_ok=True)
    if not isdir(nc_dir):
        makedirs(nc_dir, exist_ok=True)

    chdir(tif_dir)
    initial_dir = getcwd()

    # string to uniquely identify log file
    # ====================================
    date_stamp = strftime('_%Y_%m_%d_%I_%M_%S')  # _%I_%M_%S hours, minutes and secs
    stdout_fname = join(tif_dir, 'stdout' + date_stamp + '.txt')
    if isfile(stdout_fname):
        try:
            remove(stdout_fname)
        except PermissionError as err:
            print(str(err))

    return initial_dir, tif_dir, nc_dir, stdout_fname

def _downloads_user_feedback(ndown_load, tif_dir, initial_dir):
    """

    """
    print(WARNING_STR + 'check ' + tif_dir + ' to make sure all files have downloaded')
    print('\t\tNB: Use Windows command line "taskkill /F /IM wget.exe" to delete unwanted ongoing wget downloads')
    chdir(initial_dir)

    return

# =============================================================================================
def create_new_nc(clone_fn, out_fn, metric, strt_yr, nmnths):
    """
    create new NC file and copy contents of clone to same
    """
    print('\ncreating new dataset: ' + out_fn)
    try:
        nc_dset = Dataset(out_fn, 'w', format='NETCDF4_CLASSIC')
    except PermissionError as err:
        print(err)
        return None

    clone_dset = Dataset(clone_fn, 'r')
    nlats = clone_dset.variables['lat'].size
    lats = array(clone_dset.variables['lat'])
    resol_lat = (lats[-1] - lats[0]) / (lats.size - 1)

    nlons = clone_dset.variables['lon'].size
    lons = array(clone_dset.variables['lon'])
    resol_lon = (lons[-1] - lons[0]) / (lons.size - 1)

    # create global attributes
    # ========================
    date_stamp = strftime('%H:%M %d-%m-%Y')
    nc_dset.attributation = 'Created at ' + date_stamp + ' from WorldClim global climate data'
    nc_dset.history = 'XXXX'

    # setup time dimension - asssume daily
    # ====================================
    atimes, atimes_strt, atimes_end = generate_mnthly_atimes(strt_yr, nmnths)  # create ndarrays

    mess = 'Number of longitudes: {}\tlatitudes: {}\tmonths: {}'.format(nlons, nlats, nmnths)
    print(mess)

    # create dimensions
    # =================
    nc_dset.createDimension('lat', nlats)
    nc_dset.createDimension('lon', nlons)
    nc_dset.createDimension('time', len(atimes))
    nc_dset.createDimension('bnds', 2)

    # create the variable (4 byte float in this case)
    # createVariable method has arguments:
    #   first: name of the , second: datatype, third: tuple with the name (s) of the dimension(s).
    # ===================================
    lats_var = nc_dset.createVariable('lat', 'f4', ('lat',))
    lats_var.description = 'degrees of latitude North to South in ' + str(resol_lat) + ' degree steps'
    lats_var.units = 'degrees_north'
    lats_var.long_name = 'latitude'
    lats_var.axis = 'Y'
    lats_var[:] = lats

    lons_var = nc_dset.createVariable('lon', 'f4', ('lon',))
    lons_var.description = 'degrees of longitude West to East in ' + str(resol_lon) + ' degree steps'
    lons_var.units = 'degrees_east'
    lons_var.long_name = 'longitude'
    lons_var.axis = 'X'
    lons_var[:] = lons

    times = nc_dset.createVariable('time', 'f4', ('time',))
    times.units = 'days since 1900-01-01'
    times.calendar = 'standard'
    times.axis = 'T'
    times.bounds = 'time_bnds'
    times[:] = atimes

    # create time_bnds variable
    # =========================
    time_bnds = nc_dset.createVariable('time_bnds', 'f4', ('time', 'bnds'), fill_value=MISSING_VALUE)
    time_bnds._ChunkSizes = 1, 2
    time_bnds[:, 0] = atimes_strt
    time_bnds[:, 1] = atimes_end

    # create the time dependent metrics and assign default data
    # =========================================================
    var_metric = nc_dset.createVariable(metric, 'f4', ('time', 'lat', 'lon'), fill_value=MISSING_VALUE)
    if metric == 'prec':
        var_metric.long_name = 'Total precipitation'
        var_metric.units = 'mm'
    else:
        if metric == 'tmax':
            var_metric.long_name = 'Average maximum temperature'
        else:
            var_metric.long_name = 'Average minimum temperature	'
        var_metric.units = 'Degrees C'

    # var_metric.alignment = clone_dset.variables['Band1'].alignment
    var_metric.missing_value = MISSING_VALUE

    # close netCDF files
    # ================
    nc_dset.sync()
    nc_dset.close()
    clone_dset.close()

    return out_fn

def fetch_yrs_extent_from_fn(clone_fn):
    """
    deconstruct file name
    """
    tmp_str = splitext(clone_fn)[0]
    yr_span = tmp_str.split('_')[-1]
    strt_yr, end_yr = yr_span.split('-')
    strt_yr = int(strt_yr)
    end_yr = int(end_yr)
    nmnths = (end_yr - strt_yr + 1) * 12

    return strt_yr, end_yr, nmnths

def _cnvrt_tif_wthr_ncs(tif_dir, nc_dir):
    """
    requires gdal module
    converts whtever is in the tif directory
    """
    sleepTime = 2

    if not isdir(nc_dir):
        mkdir(nc_dir)

    last_time = time()
    tif_fns = glob(tif_dir + '\\' + '*.tif')
    ic = 0
    for tif_fn in tif_fns:
        short_name = split(tif_fn)[1]
        root_name = splitext(short_name)[0]
        nc_fn = join(nc_dir, root_name + '.nc')
        if isfile(nc_fn):
            print(nc_fn + ' already exists')
        else:
            ds = Translate(nc_fn, tif_fn, format = 'NetCDF')
            ic += 1
            if time() - last_time > sleepTime:
                print('Read {}\n\twrote {}'.format(tif_fn, nc_fn))
                last_time = time()

    print('Finished conversions, generated {} files'.format(ic))
    return

def unzip_hist_tifs(tif_dir):
    """
    ceate subdirectory for each metric
    """
    curr_dir = getcwd()
    for metric in METRICS:
        tif_mtrc_dir = join(tif_dir, metric)
        if isdir(tif_mtrc_dir):
            tif_fns = glob(tif_mtrc_dir + '\\' + '*.tif')
            if len(tif_fns) > 800:
                continue
        else:
            mkdir(tif_mtrc_dir)

        chdir(tif_mtrc_dir)

        zip_fns = glob(tif_dir + '\\' + '*' + metric + '*.zip')
        for zip_fn in zip_fns:
            try:
                with ZipFile(zip_fn, mode="r") as zip_obj:
                    zip_obj.extractall()
            except BadZipFile as err:
                print(zip_fn + ' ' + str(err))
            else:
                print('unzipped ' + zip_fn)

    chdir(curr_dir)
    return

def cnvrt_hist_to_ncs(tif_dir, nc_dir):
    """
    ceate subdirectory for each metric
    """
    curr_dir = getcwd()
    for metric in METRICS:

        tif_mtrc_dir = join(tif_dir, metric)

        # create NC dirs
        # ==============
        nc_mtrc_dir = join(nc_dir, metric)
        if not isdir(nc_mtrc_dir):
            makedirs(nc_mtrc_dir, exist_ok=True)

        _cnvrt_tif_wthr_ncs(tif_mtrc_dir, nc_mtrc_dir)

    chdir(curr_dir)
    return

