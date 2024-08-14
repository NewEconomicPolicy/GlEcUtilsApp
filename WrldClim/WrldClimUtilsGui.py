# -------------------------------------------------------------------------------
# Name:        WrldClimUtilsGui.py
# Purpose:     Creates a GUI to run limited data files for Ecosse
# Author:      Mike Martin
# Created:     16/05/2020
# Licence:     <your licence>
# --------------------------out_hist_nc------------------------------------------

__prog__ = 'WrldClimUtilsGui.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QLabel, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout,
                                QPushButton, QCheckBox, QFileDialog, QComboBox)

from initialise_wrldclim_utils import initiation, read_config_file, write_config_file
from wldclm_stage2_mkmnthly_ncs import make_wrldclim_dsets, make_tave_from_tmax_tmin
from wldclm_stage1_dwnld_cnvrt_tifs import download_hist_tifs, download_fut_tifs

WDGT_SIZE_60 = 60
WDGT_SIZE_90 = 90
WDGT_SIZE_110 = 110
WDGT_SIZE_135 = 135

METRICS = ['prec', 'tmax', 'tmin']
SSP_LIST = ['126', '245', '370', '585']     # Shared Socio-economic Pathways
GCM_LIST = ['ACCESS-CM2', 'BCC-CSM2-MR', 'CMCC-ESM2', 'EC-Earth3-Veg', 'GISS-E2-1-G', 'HadGEM3-GC31-LL', 'INM-CM5-0',
                            'IPSL-CM6A-LR', 'MIROC6', 'MPI-ESM1-2-HR', 'MRI-ESM2-0', 'UKESM1-0-LL']

# ==================================================================================================
class Form(QWidget):
    """
    C
    """
    def __init__(self, parent=None):

        super(Form, self).__init__(parent)

        # read settings
        initiation(self)

        # define two vertical boxes, in LH vertical box put the painter and in RH put the grid
        # define horizon box to put LH and RH vertical boxes in
        hbox = QHBoxLayout()
        hbox.setSpacing(10)

        # left hand vertical box consists of png image
        # ============================================
        lh_vbox = QVBoxLayout()

        # LH vertical box contains image only
        w_lbl20 = QLabel()
        pixmap = QPixmap(self.settings['fname_png'])
        w_lbl20.setPixmap(pixmap)

        lh_vbox.addWidget(w_lbl20)

        # add LH vertical box to horizontal box
        hbox.addLayout(lh_vbox)

        # right hand box consists of combo boxes, labels and buttons
        # ==========================================================
        rh_vbox = QVBoxLayout()

        # The layout is done with the QGridLayout
        grid = QGridLayout()
        grid.setSpacing(10)	# set spacing between widgets

        # ========== spacer
        irow = 1
        grid.addWidget(QLabel(' '), irow, 0)

        # settings check boxes
        # ====================
        irow += 1
        w_del_nc = QCheckBox('Overwrite existing dsets')
        grid.addWidget(w_del_nc, irow, 1, 1, 2)
        helpText = 'Overwrite existing datasets'
        w_del_nc.setToolTip(helpText)
        w_del_nc.setChecked(True)
        self.w_del_nc = w_del_nc

        w_rprt_only = QCheckBox('Report only')
        grid.addWidget(w_rprt_only, irow, 4)
        helpText = 'Report but do not download datasets'
        w_rprt_only.setToolTip(helpText)
        w_rprt_only.setChecked(False)
        self.w_rprt_only = w_rprt_only

        # ========== spacer
        irow += 1
        grid.addWidget(QLabel(' '), irow, 0)

        # only one history NC dataset
        # ===========================
        irow += 1
        w_pop_hist = QCheckBox('History data')
        helpText = 'Download and convert history data only'
        w_pop_hist.setToolTip(helpText)
        grid.addWidget(w_pop_hist, irow, 1, 1, 2)
        self.w_pop_hist = w_pop_hist

        w_pop_fut = QCheckBox('Future data')
        grid.addWidget(w_pop_fut, irow, 3, 1, 2)
        helpText = 'Download and convert future climate data only'
        w_pop_fut.setToolTip(helpText)
        self.w_pop_fut = w_pop_fut

        # ========== spacer
        irow += 1
        grid.addWidget(QLabel(' '), irow, 0)

        # ==========
        irow += 1
        w_lbl11 = QLabel('GCMs: ')
        helpText = 'General Circulation Models'
        w_lbl11.setToolTip(helpText)
        w_lbl11.setAlignment(Qt.AlignRight)
        grid.addWidget(w_lbl11, irow, 0)

        w_combo11 = QComboBox()
        w_combo11.setToolTip(helpText)
        for gcm in GCM_LIST:
            w_combo11.addItem(str(gcm))
        w_combo11.setFixedWidth(WDGT_SIZE_135)
        w_combo11.setToolTip(helpText)
        grid.addWidget(w_combo11, irow, 1)
        self.w_combo11 = w_combo11

        w_all_gcms = QCheckBox('Download all GCMs')
        grid.addWidget(w_all_gcms, irow, 3, 1, 2)
        helpText = 'Download and convert future climate data for all GCMs for the selected SSP'
        w_all_gcms.setToolTip(helpText)
        w_all_gcms.clicked.connect(lambda: self.chckDwnldButts(True))
        self.w_all_gcms = w_all_gcms

        # ========== spacer
        irow += 1
        grid.addWidget(QLabel(' '), irow, 0)

        # ==========
        irow += 1
        w_lbl10 = QLabel('Climate SSPs: ')
        helpText = 'Shared Socio-economic Pathways (SSPs): 126, 245, 370 and 585'
        w_lbl10.setToolTip(helpText)
        w_lbl10.setAlignment(Qt.AlignRight)
        grid.addWidget(w_lbl10, irow, 0)

        w_combo10 = QComboBox()
        w_combo10.setToolTip(helpText)
        for ssp in SSP_LIST:
            w_combo10.addItem(str(ssp))
        w_combo10.setFixedWidth(WDGT_SIZE_60)
        grid.addWidget(w_combo10, irow, 1)
        self.w_combo10 = w_combo10

        w_all_ssps = QCheckBox('Download all SSPs')
        grid.addWidget(w_all_ssps, irow, 3, 1, 2)
        helpText = 'Download and convert future climate data for all SSPs for the selected GCM'
        w_all_ssps.setToolTip(helpText)
        w_all_ssps.clicked.connect(lambda: self.chckDwnldButts(False))
        self.w_all_ssps = w_all_ssps

        # ========== spacer
        irow += 1
        grid.addWidget(QLabel(' '), irow, 0)

        # ======= operations ========
        irow += 1
        w_dwnld_hist = QPushButton('Download historic')
        helpText = 'Download historic datasets'
        w_dwnld_hist.setToolTip(helpText)
        w_dwnld_hist.setFixedWidth(WDGT_SIZE_110)
        w_dwnld_hist.clicked.connect(self.dwnldHist)
        grid.addWidget(w_dwnld_hist, irow, 0)

        w_dwnld_fut = QPushButton('Download future')
        helpText = 'Download future datasets'
        w_dwnld_fut.setToolTip(helpText)
        w_dwnld_fut.setFixedWidth(WDGT_SIZE_110)
        w_dwnld_fut.clicked.connect(self.dwnldFut)
        grid.addWidget(w_dwnld_fut, irow, 1)

        w_make_ncs = QPushButton('Make metrics')
        helpText = 'Make WorldClim NCs for all metrics: precipitation, and min, max and average temperatures'
        w_make_ncs.setToolTip(helpText)
        w_make_ncs.setFixedWidth(WDGT_SIZE_90)
        w_make_ncs.clicked.connect(self.makeNcs)
        grid.addWidget(w_make_ncs, irow, 2)

        # ==================
        w_save = QPushButton('Save', self)
        grid.addWidget(w_save, irow, 5)
        w_save.clicked.connect(lambda: self.exitClicked(False))

        w_exit = QPushButton('Exit', self)
        grid.addWidget(w_exit, irow, 6)
        w_exit.clicked.connect(lambda: self.exitClicked(True))

        # ==================
        # add grid to RH vertical box
        rh_vbox.addLayout(grid)

        # vertical box goes into horizontal box
        hbox.addLayout(rh_vbox)

        # the horizontal box fits inside the window
        self.setLayout(hbox)

        # posx, posy, width, height
        # =========================
        self.setGeometry(300, 300, 650, 250)
        self.setWindowTitle('Functions to generate NetCDF files from the WorldClim data website')
        read_config_file(self)

    # ============================================================================================
    def chckDwnldButts(self, gcms_flag=True):
        """
        C
        """
        if gcms_flag:
            if self.w_all_ssps.isChecked():
                self.w_all_ssps.setCheckState(0)
        else:
            if self.w_all_gcms.isChecked():
                self.w_all_gcms.setCheckState(0)

        return

    def dwnldHist(self):
        """
        C
        """
        download_hist_tifs(self)

    def dwnldFut(self):
        """
        C
        """
        download_fut_tifs(self)

    def makeNcs(self):
        """
        C
        """
        make_wrldclim_dsets(self)
        make_tave_from_tmax_tmin(self)

    def exitClicked(self, exit_flag):
        """

        """
        write_config_file(self)
        if exit_flag:
            self.close()

def main():

    app = QApplication(sys.argv)  # create QApplication object
    form = Form()     # instantiate form
    form.show()       # paint form
    sys.exit(app.exec_())   # start event loop

if __name__ == '__main__':
    main()
