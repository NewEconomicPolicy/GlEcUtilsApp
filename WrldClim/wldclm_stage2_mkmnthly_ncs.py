#-------------------------------------------------------------------------------
# Name:
# Purpose:     main function to process Spec results
# Author:      Mike Martin
# Created:     11/12/2015
# Licence:     <your licence>
# Comments:    Global warming potential(GWP)
#-------------------------------------------------------------------------------

__prog__ = 'eclips_reorg.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from os.path import join, isfile, isdir, split, splitext
from os import remove, makedirs
from netCDF4 import Dataset
from glob import glob
from time import time
from locale import setlocale, LC_ALL

from wldclm_stage1_dwnld_cnvrt_tifs import create_new_nc, fetch_yrs_extent_from_fn
from nc_low_level_fns import update_progress

setlocale(LC_ALL, '')
sleepTime = 5

ERROR_STR = '*** Error *** '
WARNING_STR = '*** Warning *** '

DSET_PREFIX = 'wc2.1_10m'

FUT_STRT_YR = 2021
FUT_YR_SPANS = list(['2021-2040', '2041-2060','2061-2080', '2081-2100'])

METRICS = ['prec', 'tmax', 'tmin']
MISSING_VALUE = -999.0

def make_wrldclim_dsets(form):
    """

    """
    delete_flag = form.w_del_nc.isChecked()

    ssp = form.w_combo10.currentText()
    gcm = form.w_combo11.currentText()

    out_dir = join(form.settings['wthr_dir'], 'outputs', 'Monthly')
    if not isdir(out_dir):
        makedirs(out_dir)

    # future
    # ======
    out_fut_fn = None
    out_nc_dset = None
    if form.w_pop_fut.isChecked():
        fut_inp_dir = join(form.settings['wthr_dir'], 'Fut', gcm, 'NCs')
        for metric in METRICS:
            frst_flag = True
            for yr_span in FUT_YR_SPANS:
                short_fn = '_'.join([DSET_PREFIX, metric, gcm, 'ssp' + ssp, yr_span + '.nc'])
                fut_nc = join(fut_inp_dir, short_fn)
                if frst_flag:
                    out_fut_fn = _create_new_fut_nc(fut_nc, out_dir, metric, yr_span, delete_flag)
                    if out_fut_fn is None:
                        out_nc_dset = None
                        break

                    out_nc_dset = Dataset(out_fut_fn, 'a')  # leave dataset open
                    frst_flag = False

                _append_to_new_fut_nc(fut_nc, out_nc_dset, metric, yr_span)

            if out_nc_dset is not None:
                out_nc_dset.close()
                print('NC aggregation for ' + out_fut_fn + ' complete')

    # historic
    # ========
    if form.w_pop_hist.isChecked():
        for metric in METRICS:
            frst_flag = True
            hist_inp_dir = join(form.settings['wthr_dir'], 'Hist', 'NCs', metric)

            hist_ncs = glob(hist_inp_dir + '\\*' + metric + '*.nc')
            for time_indx, hist_nc in enumerate(hist_ncs):
                if frst_flag:
                    out_hist_fn = _create_new_hist_nc(hist_nc, out_dir, metric, len(hist_ncs), delete_flag)
                    if out_hist_fn is None:
                        out_nc_dset = None
                        break

                    out_nc_dset = Dataset(out_hist_fn, 'a')       # leave dataset open
                    frst_flag = False

                _append_to_new_hist_nc(hist_nc, out_nc_dset, metric, time_indx)
                if time_indx % 50 == 0:
                    print('\tappending ' + hist_nc)

            if out_nc_dset is not None:
                out_nc_dset.close()
                print('\nWrote {} monthly NCs to {}'.format(len(hist_ncs), out_hist_fn))

    return

#======================================== future ================================

def _append_to_new_fut_nc(this_nc, out_nc_dset, metric, yr_span):
    """
    add slice to output dataset
    """
    print('\tappending ' + this_nc)
    strt_yr, end_yr = yr_span.split('-')
    strt_yr = int(strt_yr)
    end_yr = int(end_yr)

    nyears = end_yr - strt_yr + 1

    time_indx = (strt_yr - FUT_STRT_YR) * 12

    nc_dset = Dataset(this_nc, 'r')

    for iyr in range(nyears):
        for mnth_indx in range(12):
            band = 'Band' + str(mnth_indx + 1)
            this_slice = nc_dset.variables[band][:, :]
            out_nc_dset.variables[metric][time_indx, :, :] = this_slice
            time_indx += 1

    nc_dset.close()

    return

def _create_new_fut_nc(clone_fn, out_dir, metric, yr_span, delete_flag):
    """
    create new NC file and copy contents of clone to same
    """
    strt_yr = 2021
    end_yr = 2100
    extent = str(strt_yr) + '-' + str(end_yr)
    nmnths = (end_yr - strt_yr + 1) * 12

    # reform root file name
    # =====================
    fn_root = splitext(split(clone_fn)[1])[0]
    fn_root_list = fn_root.split('_')
    fn_root_list = fn_root_list[:-1] + [extent]
    fn_new_root = ('_').join(fn_root_list)

    out_fut_fn = join(out_dir, fn_new_root + '.nc')
    if isfile(out_fut_fn) and delete_flag:
        try:
            remove(out_fut_fn)
        except PermissionError as err:
            print(ERROR_STR + str(err))
            return None

    print('\ncreating new dataset: ' + out_fut_fn)
    create_new_nc(clone_fn, out_fut_fn, metric, strt_yr, nmnths)

    return out_fut_fn

#======================================== historic ================================
def _append_to_new_hist_nc(this_nc, out_nc_dset, metric, time_indx):
    """
    add slice to output dataset
    """
    nc_dset = Dataset(this_nc, 'r')
    this_slice = nc_dset.variables['Band1'][:,:]
    out_nc_dset.variables[metric][time_indx, :, :] = this_slice
    nc_dset.close()

    return

def _create_new_hist_nc(clone_fn, out_dir, metric, nmnths, delete_flag):
    """
    create new NC file and copy contents of clone to same
    """
    fn_root = splitext(split(clone_fn)[1])[0]
    yr_mnth = fn_root.split('_')[-1]
    yr_str = yr_mnth.split('-')[0]
    extent = '_' + yr_str + '-' + str(int(yr_str) + round(nmnths/12) - 1)

    out_hist_fn = join(out_dir, fn_root.rstrip('_' + yr_mnth) + extent + '.nc')
    if isfile(out_hist_fn) and delete_flag:
        try:
            remove(out_hist_fn)
        except PermissionError as err:
            print(ERROR_STR + str(err))
            return None

    print('\ncreating new dataset: ' + out_hist_fn)
    create_new_nc(clone_fn, out_hist_fn, metric, int(yr_str), nmnths)

    return out_hist_fn

def make_tave_from_tmax_tmin(form):
    """

    """
    delete_flag = form.w_del_nc.isChecked()
    ssp = form.w_combo10.currentText()

    out_dir = join(form.settings['wthr_dir'], 'outputs', 'Monthly')
    if not isdir(out_dir):
        makedirs(out_dir)

    # gather tmax datasets
    # ====================
    metric = 'tave'
    tmax_ncs = glob(out_dir + '\\*' + 'tmax' + '*.nc')
    n_complete = 0
    for tmax_nc in tmax_ncs:
        tmin_list = tmax_nc.split('_tmax_')
        tmin_nc = '_tmin_'.join(tmin_list)
        if isfile(tmin_nc):
            tave_nc = '_tave_'.join(tmin_list)
            print('will create tave ' + split(tave_nc)[1] + ' from tmax/tmin')
        else:
            print('File ' + split(tmin_nc)[1] + ' does not exist')
            continue

        # create new NC file and copy contents of clone to same
        # =====================================================
        if isfile(tave_nc) and delete_flag:
            try:
                remove(tave_nc)
            except PermissionError as err:
                print(ERROR_STR + str(err))
                return None

        strt_yr, end_yr, nmnths = fetch_yrs_extent_from_fn(tmax_nc)
        retcode = create_new_nc(tmax_nc, tave_nc, metric, strt_yr, nmnths)
        if retcode is None:
            continue

        tave_nc_dset = Dataset(tave_nc, 'a')  # leave dataset open

        print('appending average of ' + tmax_nc + '\n\tand ' + tmin_nc)

        nc_dset_max = Dataset(tmax_nc, 'r')
        nc_dset_min = Dataset(tmin_nc, 'r')
        nsteps = len(nc_dset_max.variables['time'])

        last_time = time()
        for time_indx in range(nsteps):
            this_slice_max = nc_dset_max.variables['tmax'][time_indx, :, :]
            this_slice_min = nc_dset_min.variables['tmin'][time_indx, :, :]
            tave_nc_dset.variables[metric][time_indx, :, :] = (this_slice_max + this_slice_min) / 2

            last_time = update_progress(last_time, time_indx, nsteps)

        nc_dset_max.close()
        nc_dset_min.close()
        tave_nc_dset.close()

        print('\nProcessing for ' + tave_nc + ' complete')
        n_complete += 1

    print('\nWrote {} tave NCs to {}'.format(n_complete, out_dir))

    return
