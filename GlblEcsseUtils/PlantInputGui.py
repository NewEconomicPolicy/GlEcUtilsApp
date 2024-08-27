#-------------------------------------------------------------------------------
# Name:
# Purpose:     Creates a GUI to run limited data files for Ecosse
# Author:      Mike Martin
# Created:     25/01/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

__prog__ = 'PlantInputGui.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from os.path import isdir, join, normpath, splitdrive
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QLabel, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton,
                                                                                            QLineEdit, QFileDialog)
from initialise_plant_input import read_config_file, write_config_file, initiation
from ecosse_related_utils_2 import convert_latlons, check_npp
from plant_input_funcs import (regrid_yields, convert_joe_plant_inputs_to_nc, split_filter_fertiliser,
                                                                                        split_check_sowing_dates)
from make_biofuel_inpt_file import main_biofuel
from jennifer_fns import filter_openfoodfacts_csv, edit_mngmnt
from jon_fns import copy_jon_lta_data, copy_jon_wthr_data, create_bash_script, identify_ssd

WARNING_STR = '*** Warning *** '

# =============================================
class Form(QWidget):

    def __init__(self, parent=None):

        super(Form, self).__init__(parent)

        # read settings and open log file
        initiation(self)

        # define two vertical boxes, in LH vertical box put the painter and in RH put the grid
        # define horizon box to put LH and RH vertical boxes in
        hbox = QHBoxLayout()
        hbox.setSpacing(10)

        # left hand vertical box consists of png image
        # ============================================
        lh_vbox = QVBoxLayout()

        # LH vertical box contains image only
        lbl20 = QLabel()
        pixmap = QPixmap(self.fname_png)
        lbl20.setPixmap(pixmap)

        lh_vbox.addWidget(lbl20)

        # add LH vertical box to horizontal box
        hbox.addLayout(lh_vbox)

        # right hand box consists of combo boxes, labels and buttons
        # ==========================================================
        rh_vbox = QVBoxLayout()

        # The layout is done with the QGridLayout
        grid = QGridLayout()
        grid.setSpacing(10)	# set spacing between widgets

        # actions
        # =======
        irow = 1
        w_cfg_file = QPushButton("Plant input file")
        helpText = 'Option to enable user to select a plant input file'
        w_cfg_file.setToolTip(helpText)
        grid.addWidget(w_cfg_file, irow, 0)
        w_cfg_file.clicked.connect(self.fetchYieldsFile)

        lbl01 = QLabel()
        grid.addWidget(lbl01, irow, irow, 1, 5)
        self.w_lbl01 = lbl01

        # ======
        irow += 1
        w_exe_file = QPushButton("HWSD CSV file")
        helpText = 'Option to enable user to select an HWSD csv file'
        w_exe_file.setToolTip(helpText)
        grid.addWidget(w_exe_file, irow, 0)
        w_exe_file.clicked.connect(self.fetchHwsdFile)

        lbl02 = QLabel()
        grid.addWidget(lbl02, irow, 1, 1, 5)
        self.w_lbl02 = lbl02

        # ======
        irow += 1
        w_run_ecosse = QPushButton('Regrid')
        helpText = 'Will create a configuration file for the spec.py script and run it.\n' \
                                                        + 'The spec.py script runs the ECOSSE programme'
        w_run_ecosse.setToolTip(helpText)
        w_run_ecosse.clicked.connect(self.runRegrid)
        grid.addWidget(w_run_ecosse, irow, 0)

        # ======
        irow += 1
        w_lat_lon = QPushButton("CSV lat/lon file")
        helpText = 'Option for selection of a CSV lat/lon file'
        w_lat_lon.setToolTip(helpText)
        grid.addWidget(w_lat_lon, irow, 0)
        w_lat_lon.clicked.connect(self.fetchLatLonFile)

        lbl05 = QLabel()
        grid.addWidget(lbl05, irow, 1, 1, 5)
        self.w_lbl05 = lbl05

        irow += 1
        grid.addWidget(QLabel(), irow, 1)   # spacer

        # ============
        irow += 1
        w_fert_file = QPushButton("Fertiliser file")
        helpText = 'Option to enable user to select a fertiliser file'
        w_fert_file.setToolTip(helpText)
        grid.addWidget(w_fert_file, irow, 0)
        w_fert_file.clicked.connect(self.fetchFertFile)

        lbl07 = QLabel()
        grid.addWidget(lbl07, irow, 1, 1, 5)
        self.w_lbl07 = lbl07

        # ======
        irow += 1
        w_sow_file = QPushButton("Sowing dates file")
        helpText = 'Option to enable user to select a sowing dates file'
        w_sow_file.setToolTip(helpText)
        grid.addWidget(w_sow_file, irow, 0)
        w_sow_file.clicked.connect(self.fetchSowingFile)

        lbl09 = QLabel()
        grid.addWidget(lbl09, irow, 1, 1, 5)
        self.w_lbl09 = lbl09

        irow += 1
        grid.addWidget(QLabel(), irow, 1)          # spacer

        # ==========
        irow += 1
        grid.addWidget(QLabel('Max records: '), irow, 0)

        w_max_recs = QLineEdit()
        w_max_recs.setFixedWidth(80)
        grid.addWidget(w_max_recs, irow, 1)
        self.w_max_recs = w_max_recs

        w_prgrss = QLabel()
        grid.addWidget(w_prgrss, irow, 2, 1, 5)
        self.w_prgrss = w_prgrss

        # output directory
        # =================
        irow += 1
        w_out_dir = QPushButton("Output dir")
        helpText = 'Directory containing outputs.'
        w_out_dir.setToolTip(helpText)
        grid.addWidget(w_out_dir, irow, 0)
        w_out_dir.clicked.connect(self.fetchOutDir)

        w_lbl_outdir = QLabel('')
        grid.addWidget(w_lbl_outdir, irow, 1, 1, 5)
        self.w_lbl_outdir = w_lbl_outdir

        irow += 1
        grid.addWidget(QLabel(), irow, 1)   # spacer

        # line 19
        # =======
        irow += 1
        w_run_fert = QPushButton('Fertiliser')
        helpText = 'check, filter and split an existing fertiliser file then write result to a new fertiliser file'
        w_run_fert.setToolTip(helpText)
        grid.addWidget(w_run_fert, irow, 0)
        w_run_fert.clicked.connect(self.processFertFile)

        w_run_sowing = QPushButton('Sowing dates')
        helpText = 'check, filter and split existing sowing dates file then write result to a new sowing dates file'
        w_run_sowing.setToolTip(helpText)
        grid.addWidget(w_run_sowing, irow, 1)
        w_run_sowing.clicked.connect(self.processSowingFile)

        w_gran_latlon = QPushButton('Map Lat/Lons')
        helpText = 'Generate file of granular Lat/Lons'
        w_gran_latlon.setToolTip(helpText)
        grid.addWidget(w_gran_latlon, irow, 2)
        w_gran_latlon.clicked.connect(self.convertLatLonFile)

        w_check_npp = QPushButton('Check NPP')
        helpText = 'test NPP Miami Dyce calculation using whatever met files are found'
        w_check_npp.setToolTip(helpText)
        grid.addWidget(w_check_npp, irow, 3)
        w_check_npp.clicked.connect(self.checkNpp)

        w_cnvrt2nc = QPushButton('Cnvrt PI to ann')
        helpText = 'reads monthly plant inputs and converts to annual'
        w_cnvrt2nc.setToolTip(helpText)
        grid.addWidget(w_cnvrt2nc, irow, 4)
        w_cnvrt2nc.clicked.connect(self.cnvrt2ncClicked)

        w_biofuel = QPushButton('biofuel dset')
        helpText = 'Create biofuel dataset'
        w_biofuel.setToolTip(helpText)
        grid.addWidget(w_biofuel, irow, 5)
        w_biofuel.clicked.connect(self.biofuelDatasetClicked)

        irow += 1
        w_integrity = QPushButton('Integrity')
        helpText = 'check data Integrity'
        w_integrity.setToolTip(helpText)
        grid.addWidget(w_integrity, irow, 0)
        w_integrity.clicked.connect(self.dataIntegrity)

        icol = 1
        w_edt_mngmnt = QPushButton('Edit mngmnt file')
        helpText = 'Edit management file'
        w_edt_mngmnt.setToolTip(helpText)
        grid.addWidget(w_edt_mngmnt, irow, icol)
        w_edt_mngmnt.clicked.connect(self.editMngmntClicked)

        icol += 1
        w_cpy_jon = QPushButton('Copy JM LTA')
        helpText = 'Copy John LTA data'
        w_cpy_jon.setToolTip(helpText)
        grid.addWidget(w_cpy_jon, irow, icol)
        w_cpy_jon.clicked.connect(lambda: self.copySsdClicked(True))

        icol += 1
        w_cpy_wthr_jon = QPushButton('Copy JM Wthr')
        helpText = 'Copy Jon Wthr data'
        w_cpy_wthr_jon.setToolTip(helpText)
        grid.addWidget(w_cpy_wthr_jon, irow, icol)
        w_cpy_wthr_jon.clicked.connect(lambda: self.copySsdClicked(False))

        icol += 1
        w_crt_bash_scrpt = QPushButton('Create bash script')
        helpText = 'Copy Jon Wthr data'
        w_crt_bash_scrpt.setToolTip(helpText)
        grid.addWidget(w_crt_bash_scrpt, irow, icol)
        w_crt_bash_scrpt.clicked.connect(self.crtBashScrptClicked)

        icol += 1
        w_jennifer = QPushButton('Open food facts')
        helpText = 'Create biofuel dataset'
        w_jennifer.setToolTip(helpText)
        grid.addWidget(w_jennifer, irow, icol)
        w_jennifer.clicked.connect(self.jenniferDatasetClicked)

        icol += 1
        exit = QPushButton('Exit', self)
        grid.addWidget(exit, irow, icol)
        exit.clicked.connect(self.exitClicked)

        # add grid to RH vertical box
        rh_vbox.addLayout(grid)

        # vertical box goes into horizontal box
        hbox.addLayout(rh_vbox)

        # the horizontal box fits inside the window
        self.setLayout(hbox)

        # posx, posy, width, height
        self.setGeometry(300, 300, 500, 250)
        self.setWindowTitle('Global Ecosse - Run ECOSSE programme')

        # read and set values from last run
        if not read_config_file(self):
            self.close()
            sys.exit()

    def dataIntegrity(self):
        """
        Cc integrity_check(self)
         """


        return

    def fetchOutDir(self):
        """
        select output directory
        """
        dirname = self.w_lbl_outdir.text()
        dirname = QFileDialog.getExistingDirectory(self, 'Select directory for outputs', dirname)
        if dirname != '':
            if isdir(dirname):
                self.w_lbl_outdir.setText(normpath(dirname))

        return

    def copySsdClicked(self, lta_flag=True):
        """
        check SSD is accessible
        """
        out_dir = self.w_lbl_outdir.text()
        ssd_found, use_drive, prtbl_ssd = identify_ssd()
        if ssd_found:
            if lta_flag:
                copy_jon_lta_data(self, use_drive, out_dir)
            else:
                copy_jon_wthr_data(self, use_drive, out_dir)
        else:
            print(WARNING_STR + prtbl_ssd + ' not accessible')

        return

    def crtBashScrptClicked(self):
        """
        C
        """
        ssd_found, use_drive, prtbl_ssd = identify_ssd()
        if ssd_found:
            out_dir = self.w_lbl_outdir.text()
            out_drv = splitdrive(out_dir)[0]
            create_bash_script(self, use_drive, out_drv)
        else:
            print(WARNING_STR + prtbl_ssd + ' not accessible')

        return

    def editMngmntClicked(self):
        """
        C
        """
        edit_mngmnt(self)

    def jenniferDatasetClicked(self):
        """
        C
        """
        filter_openfoodfacts_csv(self)

    def biofuelDatasetClicked(self):

        main_biofuel()

    def checkNpp(self):

        check_npp(self)

    def convertLatLonFile(self):

        convert_latlons(self)

    def processFertFile(self):

        split_filter_fertiliser(self)

    def fetchLatLonFile(self):
        """
        identify file of lat/lons
        """
        fname = self.w_lbl05.text()
        fname, dummy = QFileDialog.getOpenFileName(self, 'Open file', fname, 'Lat/Lon file (*.txt)')
        fname = normpath(fname)
        if fname != '':
            self.w_lbl05.setText(fname)

    def fetchFertFile(self):
        """
        identify the fertiliser file
        """
        fname = self.w_lbl07.text()
        fname, dummy = QFileDialog.getOpenFileName(self, 'Open file', fname, 'Fertiliser file (*.txt)')
        fname = normpath(fname)
        if fname != '':
            self.w_lbl07.setText(fname)

    def processSowingFile(self):

        split_check_sowing_dates(self)

    def fetchSowingFile(self):
        """
        identify the sowing file
        """
        fname = self.w_lbl09.text()
        fname, dummy = QFileDialog.getOpenFileName(self, 'Open file', fname, 'Sowing dates file (*.txt)')
        fname = normpath(fname)
        if fname != '':
            self.w_lbl09.setText(fname)

    def runRegrid(self):

        # run the make simulations script
        regrid_yields(self)

    def exitClicked(self):

        func_name =  __prog__ + ' exitClicked'

        write_config_file(self)   # write last GUI selections

        try:
            self.lgr.handlers[0].close() # close logging
        except AttributeError:
            pass
        self.close()

    def cnvrt2ncClicked(self):
        """
        identify the yields file
        """
        fname = self.w_lbl01.text()
        convert_joe_plant_inputs_to_nc(fname)

    def fetchYieldsFile(self):
        """
        identify the yields file
        """
        fname = self.w_lbl01.text()
        fname, dummy = QFileDialog.getOpenFileName(self, 'Open file', fname, 'Yields file (*.csv)')
        fname = normpath(fname)
        if fname != '':
            self.w_lbl01.setText(fname)

    def fetchHwsdFile(self):
        """
        identify the HWSD to be used
        """

        fname = self.w_lbl02.text()
        fname, dummy = QFileDialog.getOpenFileName(self, 'Select HWSD', fname, 'HWSD .csv file (*.csv)')
        fname = normpath(fname)
        if fname != '':
            self.w_lbl02.setText(fname)

def main():

    app = QApplication(sys.argv)  # create QApplication object
    form = Form()     # instantiate form
    form.show()       # paint form
    sys.exit(app.exec_())   # start event loop

if __name__ == '__main__':
    main()
