#-------------------------------------------------------------------------------
# Name:
# Purpose:     GUI front end to enable checking of Fortran modules
# Author:      Mike Martin
# Created:     25/7/2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# Creates an Excel file consisting of redundant subroutines

__prog__ = 'CntryIsoCodeGUI.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, \
                                                                                            QFileDialog, QCheckBox
from common_funcs import process_zip_files
from  hilda_fns import add_codes_countries_nc
from initialise_cntry_code import initiation, _write_setup_file

class Form(QWidget):

    def __init__(self, parent=None):

        super(Form, self).__init__(parent)

        self.version = 'CountryCodes'
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

        # line 4 
        # ======
        irow = 4
        w_codes_fn = QPushButton("Country codes file")
        helpText = 'identify CSV file of ISO 3166-1 alpha-3 three-letter country codes and associated country names'
        w_codes_fn.setToolTip(helpText)
        w_codes_fn.clicked.connect(self.fetchCodesFname)
        grid.addWidget(w_codes_fn, irow, 0)

        lbl04 = QLabel(self.codes_fname)
        grid.addWidget(lbl04, irow, 1, 1, 5)
        self.lbl04 = lbl04
 
        # line 5
        # ======
        irow += 1
        w_zip_dir= QPushButton("Zip files dir")
        helpText = 'Directory zip files reside.'
        w_zip_dir.setToolTip(helpText)
        grid.addWidget(w_zip_dir, irow, 0)
        w_zip_dir.clicked.connect(self.fetchZipDir)

        lbl05 = QLabel(self.zip_dir)
        grid.addWidget(lbl05, irow, 1, 1, 5)
        self.lbl10 = lbl05

        # line 8
        # ======
        irow += 3
        w_over_write = QCheckBox('Overwrite existing files')
        grid.addWidget(w_over_write, irow, 0, 1, 3)
        if self.overwrite_flag:
            w_over_write.setChecked(True)
        else:
            w_over_write.setChecked(False)
        self.w_over_write = w_over_write

        # line 10
        # =======
        irow += 2
        w_zip_dir= QPushButton("Country shapes dir")
        helpText = 'Directory where country shapes reside.'
        w_zip_dir.setToolTip(helpText)
        grid.addWidget(w_zip_dir, irow, 0)
        w_zip_dir.clicked.connect(self.fetchCntryDir)

        lbl10 = QLabel(self.cntry_shp_dir)
        grid.addWidget(lbl10, irow, 1, 1, 5)
        self.lbl10 = lbl10

        # spacer
        # ======
        irow += 1
        grid.addWidget(QLabel(), irow, 1)

        # line 19
        # =======
        irow += 8
        w_apply_codes = QPushButton("Apply Country Codes")
        helpText = 'Apply country codes to prexisting NetCDF file of countries'
        w_apply_codes.setToolTip(helpText)
        grid.addWidget(w_apply_codes, irow, 0)
        w_apply_codes.clicked.connect(self.applyCntryCodes)

        w_prcss_zipfns = QPushButton("Process zip files")
        helpText = 'create directory with name of correspnding country and unpack each zip file in this directory'
        w_prcss_zipfns.setToolTip(helpText)
        grid.addWidget(w_prcss_zipfns, irow, 1, 1, 2)
        w_prcss_zipfns.clicked.connect(self.prcssZipFiles)

        exit = QPushButton("Exit", self)
        grid.addWidget(exit, irow, 5, 1, 2)
        exit.clicked.connect(self.exitClicked)

        # add grid to RH vertical box
        rh_vbox.addLayout(grid)

        # vertical box goes into horizontal box
        hbox.addLayout(rh_vbox)

        # the horizontal box fits inside the window
        self.setLayout(hbox)

        # posx, posy, width, height
        self.setGeometry(300, 300, 690, 250)
        self.setWindowTitle('Unpack and organise zip files')

    def applyCntryCodes(self):

        add_codes_countries_nc(self)

    def fetchCodesFname(self):

        fname = self.codes_fname
        if fname == "":
            fname = self.root_dir

        fname, dummy = QFileDialog.getOpenFileName(self, 'Open country codes file', fname, 'ods files (*.ods)' )

        self.lbl04.setText(fname)
        self.codes_fname = fname

    def prcssZipFiles(self):

        # write last path selections
        process_zip_files(self)

    def fetchZipDir(self):
        '''
        select the output directory for the CSV or NetCDF files
        '''
        fname = self.zip_dir
        fname = QFileDialog.getExistingDirectory(self, 'Select directory files reside', fname)
        if fname == '':
            fname = self.zip_dir
        else:
            if fname != self.zip_dir:
                # TODO: need to check this is a directory with write permissions
                self.zip_dir = fname
                self.lbl05.setText(fname)

    def fetchCntryDir(self):
        '''
        select the output directory for the CSV or NetCDF files
        '''
        fname = self.cntry_shp_dir
        fname = QFileDialog.getExistingDirectory(self, 'Select directory files reside', fname)
        if fname == '':
            fname = self.cntry_shp_dir
        else:
            if fname != self.cntry_shp_dir:
                # TODO: need to check this is a directory with write permissions
                self.cntry_shp_dir = fname
                self.lbl10.setText(fname)

    def exitClicked(self):

        # write last path selections
        _write_setup_file(self)

        self.close()

def main():

    app = QApplication(sys.argv)  # create QApplication object
    form = Form()     # instantiate form
    form.show()       # paint form
    sys.exit(app.exec_())   # start event loop

if __name__ == '__main__':
    main()
