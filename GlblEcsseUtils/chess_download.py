#-------------------------------------------------------------------------------
# Name:
# Purpose:     diverse
# Author:      Mike Martin
# Created:     26/05/2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'analyse_source.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from sys import stdout
from os.path import isdir, join, normpath, isfile
from os import chdir, getcwd, name as name_os
from subprocess import Popen, PIPE, STDOUT
from time import strftime
from time import time, sleep
from datetime import timedelta

sleepTime = 5
SCENARIOS = list(['rcp26', 'rcp45', 'rcp60', 'rcp85'])
REALISATIONS = list(['01', '04', '06', '15'])
'''
hurs relative_humidity; huss specific_humidity;
rlds surface_downwelling_longwave_flux_in_air;
huss surface_downwelling_shortwave_flux_in_air
'''
METRICS = list(['hurs', 'huss', 'pr', 'rlds', 'rsds', 'sfcWind', 'tas', 'tasmax', 'tasmin'])
N_DEPOS_METRICS = list(['NOy', 'NHx'])

def fetch_chess_daily(form, time_step = 'daily'):
    '''
    Link to the CHESS rcp data on CEDA:
            https://data.ceda.ac.uk/badc/deposited2021/chess-scape/data

    cmd_test = 'wget --http-user = mmartin@abdn.ac.uk --http-passwd=Rethymno13\) -e robots=off --mirror --no-parent '
    cmd_test += '- P . -r '
    cmd_test += 'https://dap.ceda.ac.uk/badc/deposited2021/chess-scape/data/rcp26/01/monthly/'
    cmd_test += 'chess-scape_rcp26_01_dtr_uk_1km_monthly_19801201-20801130.nc'
    '''
    out_dir = form.w_lbl04.text()
    if isdir(out_dir):
        curr_dir = getcwd()
        chdir(out_dir)

    try:
        ndsets = int(form.w_ndsets.text())
    except ValueError as err:
        ndsets = 2

    print('Will download {} datasets'.format(ndsets))

    userid = 'mmartin@abdn.ac.uk'
    passwd = 'Rethymno13\)'
    arg_strng = ' --http-user=' + userid + ' --http-passwd=' + passwd + ' -e robots=off --mirror --no-parent -P . -r '

    # construct file name
    # ===================
    bias_flag = True
    bias = '_bias-corrected'
    root_dir = '/data.ceda.ac.uk/badc/deposited2021/chess-scape/data/'

    if name_os == 'nt':
        wget_exe = 'E:\\Freeware\\UnxUtils\\usr\\local\wbin\\wget.exe'
        out_fn = 'E:\\temp\\chess\\test_output.txt'
        out_dir_root = join(normpath('F:\\New_Chess'), time_step)
        stdout_dir = 'F:\\GreenHouse\\logs'
    else:
        wget_exe = '/usr/bin/wget'
        out_fn = '/mnt/e/temp/test_output.txt'
        out_dir_root = join(normpath('/mnt/f/New_Chess'), time_step)
        stdout_dir = '/mnt/f/GreenHouse/logs'

    fobj = open(normpath(out_fn), 'w')
    ndown_load = 0
    nexist = 0
    time_accum = 0
    for scenario in SCENARIOS:
        if bias_flag:
            scenario += bias

        date_stamp = strftime('_%Y_%m_%d_%I_%M_%S')  # string to uniquely identify log files
        stdout_fname = join(stdout_dir, 'stdout_' + date_stamp + '.txt')

        for variant in REALISATIONS:
            for metric in METRICS:
                remote_dir = root_dir + scenario + '/' + variant + '/' + time_step + '/' + metric + '/'

                for yr in range(1980, 2080 + 1):
                    yr_str = str(yr)
                    for imnth in range(1, 13):

                        # start at Dec 1980
                        if yr == 1980 and imnth != 12:
                            continue

                        yr_mnth_str = yr_str + '{0:0=2d}'.format(imnth)
                        fname = 'chess-scape_' + scenario + '_' + variant + '_' + metric
                        fname += '_uk_1km_' + time_step + '_' + yr_mnth_str + '01-' + yr_mnth_str + '30.nc'
                        remote_fname = 'https:/' + remote_dir + fname

                        # skip pre-existing files
                        # =======================
                        local_fname = getcwd() + normpath(remote_dir + fname)
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

                            fobj.write('cmd: ' + cmd + '\n')

    fobj.close()

    print('\nExisting files: {}\tdownloaded: {}\tto: {}'.format(nexist, ndown_load, out_dir))
    avrg_dnld_time = timedelta(seconds = round(time_accum/ndown_load))
    print('Wrote summary: {}\taverage download time: {}'.format(out_fn, avrg_dnld_time))

    chdir(curr_dir)     # revert

    return

def fetch_chess_files(form, time_step = 'monthly'):
    '''
    Link to the CHESS rcp data on CEDA:
            https://data.ceda.ac.uk/badc/deposited2021/chess-scape/data

    cmd_test = 'wget --http-user = mmartin@abdn.ac.uk --http-passwd=Rethymno13\) -e robots=off --mirror --no-parent '
    cmd_test += '- P . -r '
    cmd_test += 'https://dap.ceda.ac.uk/badc/deposited2021/chess-scape/data/rcp26/01/monthly/'
    cmd_test += 'chess-scape_rcp26_01_dtr_uk_1km_monthly_19801201-20801130.nc'
    '''
    out_dir = form.w_lbl04.text()
    if isdir(out_dir):
        curr_dir = getcwd()
        chdir(out_dir)

    try:
        ndsets = int(form.w_ndsets.text())
    except ValueError as err:
        ndsets = 2

    print('Will download {} datasets'.format(ndsets))

    userid = 'mmartin@abdn.ac.uk'
    passwd = 'Rethymno13\)'
    arg_strng = ' --http-user=' + userid + ' --http-passwd=' + passwd + ' -e robots=off --mirror --no-parent -P . -r '

    # construct file name
    # ===================
    bias_flag = True
    bias = '_bias-corrected'
    root_dir = '/data.ceda.ac.uk/badc/deposited2021/chess-scape/data/'

    if name_os == 'nt':
        wget_exe = 'E:\\Freeware\\UnxUtils\\usr\\local\wbin\\wget.exe'
        out_fn = 'E:\\temp\\chess\\test_output.txt'
        out_dir_root = join(normpath('F:\\New_Chess'), time_step)
        stdout_dir = 'F:\\GreenHouse\\logs'
    else:
        wget_exe = '/usr/bin/wget'
        out_fn = '/mnt/e/temp/test_output.txt'
        out_dir_root = join(normpath('/mnt/f/New_Chess'), time_step)
        stdout_dir = '/mnt/f/GreenHouse/logs'

    fobj = open(normpath(out_fn), 'w')
    ndown_load = 0
    nexist = 0
    time_accum = 0
    for scenario in SCENARIOS:
        if bias_flag:
            scenario += bias

        for variant in REALISATIONS:
            for metric in METRICS:
                remote_dir = root_dir + scenario + '/' + variant + '/' + time_step + '/'
                fname = 'chess-scape_' + scenario + '_' + variant + '_' + metric
                fname += '_uk_1km_' + time_step + '_19801201-20801130.nc'
                remote_fname = 'https:/' + remote_dir + fname

                # skip pre-existing files
                # =======================
                local_fname = getcwd() + normpath(remote_dir + fname)
                if isfile(local_fname):
                    nexist += 1
                    continue

                date_stamp = strftime('_%Y_%m_%d_%I_%M_%S')     # string to uniquely identify log files
                stdout_fname = join(stdout_dir, 'stdout_' + date_stamp + '.txt')

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

                fobj.write('cmd: ' + cmd + '\n')

    fobj.close()

    print('\nExisting files: {}\tdownloaded: {}\tto: {}'.format(nexist, ndown_load, out_dir))
    avrg_dnld_time = timedelta(seconds = round(time_accum/ndown_load))
    print('Wrote summary: {}\taverage download time: {}'.format(out_fn, avrg_dnld_time))

    chdir(curr_dir)     # revert

    return

def fetch_n_depos_files(form):
    '''
    cmd_test = 'wget --http-user = vdbuser --http-passwd=V3r1fy -e robots=off --mirror --no-parent '
    cmd_test += '- P . -r '
    cmd_test += 'https://verifydb.lsce.ipsl.fr/thredds/catalog/verify/VERIFY_INPUT/NITROGEN/catalog.html
'
    cmd_test += 'SYN_NHx_Deposition_EMEP-MSCW-1995_JRC_ANTH_EU_1M_V2_20210612_DENTENER_WP3_2D.nc'
    '''
    curr_dir = getcwd()
    out_dir = form.w_lbl04.text()
    if isdir(out_dir):
        chdir(out_dir)

    try:
        ndsets = int(form.w_ndsets.text())
    except ValueError as err:
        ndsets = 2

    print('Will download up to {} datasets'.format(ndsets))

    time_step = 'monthly'
    userid = 'vdbuser'
    passwd = 'V3r1fy'
    arg_strng = ' --http-user=' + userid + ' --http-passwd=' + passwd + ' -e robots=off --mirror --no-parent -P . -r '

    # construct file name
    # ===================
    remote_dir = '/verifydb.lsce.ipsl.fr/thredds/catalog/verify/VERIFY_INPUT/NITROGEN/' # catalog.html/'

    wget_exe = 'E:\\Freeware\\UnxUtils\\usr\\local\wbin\\wget.exe'
    out_fn = 'E:\\GlobalEcosseData\\N_deposition\\test_output.txt'
    stdout_dir = 'E:\\GlobalEcosseData\\N_deposition\\logs'

    fobj = open(normpath(out_fn), 'w')
    ndown_load = 0
    nexist = 0
    time_accum = 0

    for metric in N_DEPOS_METRICS:
        if ndown_load > ndsets:
            break

        for yr in range(1995,2018):
            if ndown_load > ndsets:
                break

            fname = 'SYN_' + metric + '_Deposition_EMEP-MSCW-' + str(yr)
            fname += '_JRC_ANTH_EU_1M_V2_20210612_DENTENER_WP3_2D.nc'
            remote_fname = 'https:/' + remote_dir + fname

            # skip pre-existing files
            # =======================
            local_fname = getcwd() + normpath(remote_dir + fname)
            if isfile(local_fname):
                nexist += 1
                continue

            date_stamp = strftime('_%Y_%m_%d_%I_%M_%S')     # string to uniquely identify log files
            stdout_fname = join(stdout_dir, 'stdout_' + date_stamp + '.txt')

            cmd = wget_exe + arg_strng + remote_fname

            print('\nDownloading: ' + fname)
            start_time = time()
            new_inst = Popen(cmd, shell=False, stdin=PIPE, stdout=open(stdout_fname, 'w'), stderr=STDOUT)
            while new_inst.poll() is None:
                stdout.flush()
                stdout.write('\rTime elapsed: ' + str(timedelta(seconds = round(time() - start_time))))
                sleep(sleepTime)

            time_accum += time() - start_time
            ndown_load += 1

            fobj.write('cmd: ' + cmd + '\n')

    fobj.close()

    print('\nExisting files: {}\tdownloaded: {}\tto: {}'.format(nexist, ndown_load, out_dir))
    avrg_dnld_time = timedelta(seconds = round(time_accum/max(ndown_load,1)))
    print('Wrote summary: {}\taverage download time: {}'.format(out_fn, avrg_dnld_time))

    chdir(curr_dir)     # revert

    return

def main():
    '''
    Entry point
    '''

    retcode = fetch_chess_files()

if __name__ == '__main__':
    main()

