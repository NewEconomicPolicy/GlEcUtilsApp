#-------------------------------------------------------------------------------
# Name:
# Purpose:     diverse
# Author:      Mike Martin
# Created:     26/05/2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'chess_dwnld_historic.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from sys import stdout
from os.path import isdir, join, normpath, isfile
from os import chdir, getcwd, mkdir, name as name_os
from glob import glob
from subprocess import Popen, PIPE, STDOUT
from time import strftime
from time import time, sleep
from calendar import monthrange
from datetime import timedelta

ERROR_STR = '*** Error *** '

sleepTime = 5
SCENARIOS = list(['rcp26', 'rcp45', 'rcp60', 'rcp85'])
REALISATIONS = list(['01', '04', '06', '15'])
'''
hurs relative_humidity; huss specific_humidity;
rlds surface_downwelling_longwave_flux_in_air;
huss surface_downwelling_shortwave_flux_in_air
'''
CHESS_REPOSIT = 'M:\\CHESS_daily_data.ceda.ac.uk\\data.ceda.ac.uk\\badc\\deposited2021\\chess-scape\data'
METRICS = list(['hurs', 'huss', 'pr', 'rlds', 'rsds', 'sfcWind', 'tas', 'tasmax', 'tasmin'])

def chess_daily_to_mnthly(form):
    '''

    '''
    out_dir = form.w_lbl04.text()
    if not isdir(out_dir):
        print(ERROR_STR + out_dir + ' must exist')
        return

    for scenario in SCENARIOS:
        for variant in REALISATIONS:
            for metric in METRICS:
                # create monthly NC file
                # ======================
                metric_dir = CHESS_REPOSIT + '/' + scenario + '_bias-corrected' + '/' + variant + '/' + 'daily' + \
                             '/' +  metric + '/'
                nc_files = glob(normpath(metric_dir) + '\\*.nc')
                for nc_fn in nc_files:
                    # create monthly values and write to newly created NC file
                    
                    pass


    curr_dir = getcwd()
    chdir(out_dir)

def fetch_chess_daily_hist(form, time_step = 'daily'):
    '''
    Link to the CHESS rcp data on CEDA:
            https://data.ceda.ac.uk/badc/deposited2021/chess-scape/data

    cmd_test = 'wget --http-user = mmartin@abdn.ac.uk --http-passwd=Rethymno13\) -e robots=off --mirror --no-parent '
    cmd_test += '- P . -r '
    cmd_test += 'https://dap.ceda.ac.uk/badc/deposited2021/chess-scape/data/rcp26/01/monthly/'
    cmd_test += 'chess-scape_rcp26_01_dtr_uk_1km_monthly_19801201-20801130.nc'
    '''
    out_dir = form.w_lbl04.text()
    if not isdir(out_dir):
        print(ERROR_STR + out_dir + ' must exist')
        return

    curr_dir = getcwd()
    chdir(out_dir)

    try:
        ndsets = int(form.w_ndsets.text())
    except ValueError as err:
        ndsets = 2

    print('Will download {} datasets'.format(ndsets))

    userid = 'mmartin@abdn.ac.uk'
    passwd = 'Rethymno13\)'
    '''
    -e robots=off   execute a `.wgetrc'-style command
    --no-parent     don't ascend to the parent directory
    '''
    arg_strng = ' --http-user=' + userid + ' --http-passwd=' + passwd
    arg_strng += ' -v -e robots=off --mirror --no-parent -P . -r '

    # construct file name
    # ===================
    root_dir = '/data.ceda.ac.uk/badc/deposited2021/chess-scape/data/'
    root_dir = '/catalogue.ceh.ac.uk/datastore/eidchub/2ab15bf0-ad08-415c-ba64-831168be7293/'

    wget_exe, hist_log_fn, stdout_dir = _dynamic_vars()

    fobj_log = open(normpath(hist_log_fn), 'w')
    ndown_load = 0
    nexist = 0
    time_accum = 0

    date_stamp = strftime('_%Y_%m_%d_%I_%M_%S')  # string to uniquely identify log files
    stdout_fname = join(stdout_dir, 'stdout_' + date_stamp + '.log')

    for metric in METRICS:
        remote_dir = root_dir + metric + '/'
        local_dir = join(out_dir, metric)
        if not isdir(local_dir):
            mkdir(local_dir)

        for yr in range(1961, 2017 + 1):
            yr_str = str(yr)
            for imnth in range(1, 13):

                yr_mnth_str = yr_str + '{0:0=2d}'.format(imnth)
                days_in_mnth = str(monthrange(yr, imnth)[1])
                fname = 'chess-met_' + metric
                fname += '_gb_1km_' + time_step + '_' + yr_mnth_str + '01-' + yr_mnth_str + days_in_mnth + '.nc'
                remote_fname = 'https:/' + remote_dir + fname

                # skip pre-existing files
                # =======================
                local_fname = join(local_dir, fname)
                if isfile(local_fname):
                    nexist += 1
                    continue

                cmd = wget_exe + arg_strng + remote_fname

                if ndown_load < ndsets:
                    print('\nDownloading: ' + fname)
                    start_time = time()
                    new_inst = Popen(cmd, shell=False, stdin=PIPE, stdout=open(stdout_fname, 'w'), stderr=STDOUT)
                    while new_inst.poll() is None:
                        stdout.flush()
                        stdout.write('\rTime elapsed: ' + str(timedelta(seconds = round(time() - start_time))))
                        sleep(sleepTime)

                    time_accum += time() - start_time
                    ndown_load += 1

                    fobj_log.write('cmd: ' + cmd + '\n')

    fobj_log.close()

    print('\nExisting files: {}\tdownloaded: {}\tto: {}'.format(nexist, ndown_load, out_dir))
    avrg_dnld_time = timedelta(seconds = round(time_accum/ndown_load))
    print('Wrote summary: {}\taverage download time: {}'.format(hist_log_fn, avrg_dnld_time))

    chdir(curr_dir)     # revert

    return

def _dynamic_vars():
    '''

    '''
    if name_os == 'nt':
        wget_exe = 'E:\\Freeware\\UnxUtils\\usr\\local\wbin\\wget.exe'
        out_fn = 'E:\\temp\\chess\\chess_daily_hist.log'
        stdout_dir = 'F:\\GreenHouse\\logs'
    else:
        wget_exe = '/usr/bin/wget'
        out_fn = '/mnt/e/temp/chess_daily_hist.log'
        stdout_dir = '/mnt/f/GreenHouse/logs'

    return wget_exe, out_fn, stdout_dir
