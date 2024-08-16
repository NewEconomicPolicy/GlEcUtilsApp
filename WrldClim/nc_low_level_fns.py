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

from calendar import monthrange
from _datetime import datetime
from numpy import arange
from locale import format_string
from time import time
from sys import stdout

def get_gcm_ssp_lists(form, all_gcms, all_ssps):
    """
    return gcm and ssp lists from GUI
    """
    gcm_gui = form.w_combo11.currentText()
    ssp_gui = form.w_combo10.currentText()

    gcm_list = []
    ssp_list = []

    if form.w_all_gcms.isChecked():
        for gcm in all_gcms:
            gcm_list.append(gcm)
        ssp_list.append(ssp_gui)

    elif form.w_all_ssps.isChecked():
        for ssp in all_ssps:
            ssp_list.append(ssp)
        gcm_list.append(gcm_gui)

    else:
        gcm_list.append(gcm_gui)
        ssp_list.append(ssp_gui)

    return gcm_list, ssp_list

def generate_mnthly_atimes(fut_start_year, num_months):
    """
    expect 1092 for 91 years plus 2 extras for 40 and 90 year differences
    """

    atimes = arange(num_months)     # create ndarray
    atimes_strt = arange(num_months)
    atimes_end  = arange(num_months)

    date_1900 = datetime(1900, 1, 1, 12, 0)
    imnth = 1
    year = fut_start_year
    prev_delta_days = -999
    for indx in arange(num_months + 1):
        date_this = datetime(year, imnth, 1, 12, 0)
        delta = date_this - date_1900   # days since 1900-01-01

        # add half number of days in this month to the day of the start of the month
        # ==========================================================================
        if indx > 0:
            atimes[indx-1] = prev_delta_days + int((delta.days - prev_delta_days)/2)
            atimes_strt[indx-1] = prev_delta_days
            atimes_end[indx-1] =  delta.days - 1

        prev_delta_days = delta.days
        imnth += 1
        if imnth > 12:
            imnth = 1
            year += 1

    return atimes, atimes_strt, atimes_end

def update_progress(last_time, time_indx, nsteps):
    """
    Update progress bar
    """
    this_time = time()
    if (this_time - last_time) > 5.0:
        remain_str = format_string("%d", nsteps - time_indx, grouping=True)
        cmplt_str = format_string("%d", time_indx, grouping=True)
        stdout.flush()
        stdout.write('\r                                                                                          ')
        stdout.write('\rComplete: {} Remaining: {}'.format(cmplt_str, remain_str))
        return this_time

    return last_time