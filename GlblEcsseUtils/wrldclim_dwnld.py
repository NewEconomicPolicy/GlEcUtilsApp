#-------------------------------------------------------------------------------
# Name:
# Purpose:     diverse
# Author:      Mike Martin
# Created:     26/05/2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

__prog__ = 'wrldclim_dwnld.py'
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
SSPS = list(['ssp126', 'ssp245', 'ssp370', 'ssp585'])     # Shared Socioeconomic Pathways

PERIODS = ['2021-2040', '2041-2060', '2061-2080', '2081-2100']
METRICS = list(['tn', 'pr'])

def fetch_worldclim_monthly(form, time_step = 'daily'):
    '''
    Link to the WorldClim data website:
            https://geodata.ucdavis.edu/climate/worldclim/2_1

    typically:        https://geodata.ucdavis.edu/climate/worldclim/2_1/cmip6/10m/IPSL-CM6A-LR/ssp585/

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
