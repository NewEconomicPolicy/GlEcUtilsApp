#-------------------------------------------------------------------------------
# Name:
# Purpose:     Creates a GUI with five adminstrative levels plus country
# Author:      Mike Martin
# Created:     11/12/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'conversion_funcs.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from copy import deepcopy

def difference(vals, vals_null, num_time_vals):
    '''
    Subtract null run (vals_null) from transition results (vals)
    ===========================================================
    '''
    result = {}
    for key in vals.keys():
        result[key] = []
        for k in range(num_time_vals):
            result[key].append(vals[key][k] - vals_null[key][k])
    return result

def subtract_init_vals(vals, num_time_vals):
    '''
    Subtract initial value from all values
    ======================================
    invoked for situation where there is no null run
    '''
    result = deepcopy(vals)    # using out=vals[:] doesn't work - don't understand why
    for key in vals.keys():
        for k in range(num_time_vals):
            result[key][k] -= vals[key][0]
    return result

def convert(vals, factors, num_time_vals):
    '''
    Convert atomic to molecular mass
    ================================
    '''
    result = {}
    for key in vals.keys():
        result[key] = []
        for k in range(num_time_vals):
            result[key].append(vals[key][k]*factors[key])
    return result

def annualise(vals, num_time_vals, nyears, cumulative_flag):
    '''
    Annualise all metrics
    =====================

    period is in months
    '''

    # include first year is year increment is for 12 months
    period = nyears*12
    if period == 12:
        k_start = 0
    else:
        k_start = 12

    result = {}
    for key in vals.keys():
        result[key] = []
        for k in range(k_start, num_time_vals, period):
            # make sure we do not go over values list limit
            if k + period > num_time_vals:
                break

            # think of soc as a reservoir
            if key == 'soc':
                annual_val = vals[key][k + period - 1]
            else:
                annual_val = 0.0
                for mnth in range(period):
                    annual_val += vals[key][k + mnth]

            result[key].append(annual_val/nyears)

    # add all values together
    # ======================
    if cumulative_flag:
        for key in vals.keys():

            # think of soc as a reservoir
            if key == 'soc':
                cumulation = vals[key][-1] - vals[key][k_start]
            else:
                cumulation = sum(vals[key][k_start:])

            result[key].append(cumulation)

    return result

def combine(vals, factor_ghg):
    '''
    Add together all metrics to yield total GHG
    ===========================================
    '''
    result = []

    # create list zeros
    # =================
    num_years = len(vals['co2'])
    for k in range(num_years):
        result.append(0)

    # sum each metric and multiply by appropriate factor
    # ==================================================
    previous_year_val = 0.0
    for key in vals.keys():
        if key == 'soc':
            for k in range(num_years):
                soc_val = vals[key][k]*factor_ghg[key]
                result[k] += soc_val - previous_year_val
                previous_year_val = soc_val
        elif key != 'co2':
            for k in range(num_years):
                result[k] += vals[key][k]*factor_ghg[key]

    return result

def make_mean(vals, num_time_vals):
    '''
    Add together all metrics to yield total GHG
    ===========================================
    '''
    result = {}
    year_incr = 1
    period = year_incr*12
    for key in vals.keys():
        result[key] = []
        for k in range(12, num_time_vals, period):
            mean_val = 0.0
            if k + period > num_time_vals:
                break
            if key == 'soc':
                mean_val = vals[key][k + period -1] - vals[key][k]
            else:
                for mnth in range(period):
                    mean_val += vals[key][k+mnth]

            result[key].append(mean_val/year_incr)

    return result
