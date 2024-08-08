#-------------------------------------------------------------------------------
# Name:
# Purpose:     GUI front end to enable checking of Fortran modules
# Author:      Mike Martin
# Created:     25/7/2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# Creates an Excel file consisting of redundant subroutines

__prog__ = 'DvrseUtilsGUI.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

import sys
from os import getenv

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit, \
                                                                                QPushButton, QCheckBox, QFileDialog

from initialise_dvrse_utils import initiation, read_config_file, write_config_file
from chess_download import fetch_chess_files, fetch_n_depos_files, fetch_chess_daily
from ecosse_related_utils import add_vigour, concat_met_files, create_ecosse_inst, separate_projects
from ecosse_related_utils_2 import clean_sv_runs, check_sv_runs
from chess_dwnld_historic import fetch_chess_daily_hist, chess_daily_to_mnthly
from wrldclim_dwnld import fetch_worldclim_monthly

STD_FLD_SIZE_60 = 60

class Form(QWidget):

    def __init__(self, parent=None):

        super(Form, self).__init__(parent)

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
        pixmap = QPixmap(self.fpng)
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

        # =========================================
        w_inp_psh = QPushButton('Inputs dir')

        irow = 1
        grid.addWidget(w_inp_psh, irow, 0)
        w_inp_psh.clicked.connect(self.fetchRefDir)

        w_inp_dir = QLabel()
        grid.addWidget(w_inp_dir, irow, 1, 1, 5)
        self.w_inp_dir = w_inp_dir

        # =========================================
        w_out_dir = QPushButton('Outputs dir')

        irow = 4
        grid.addWidget(w_out_dir, irow, 0)
        w_out_dir.clicked.connect(self.fetchRefDir)

        w_lbl04 = QLabel()
        grid.addWidget(w_lbl04, irow, 1, 1, 5)
        self.w_lbl04 = w_lbl04

        # report
        # ======
        irow += 1
        w_lbl05 = QLabel('')
        grid.addWidget(w_lbl05, irow, 1, 1, 5)
        self.w_lbl05 = w_lbl05

        # ===================
        irow += 2
        lbl02a = QLabel('Number of datasets:')
        lbl02a.setAlignment(Qt.AlignRight)
        grid.addWidget(lbl02a, irow, 0)        

        w_ndsets = QLineEdit()
        w_ndsets.setFixedWidth(STD_FLD_SIZE_60)
        grid.addWidget(w_ndsets, irow, 1)
        self.w_ndsets = w_ndsets

        # line 19
        # =======
        irow = 19
        w_get_chess = QPushButton('Fetch CHESS files')
        helpText = 'Download complete set of CHESS files'
        w_get_chess.setToolTip(helpText)
        w_get_chess.clicked.connect(self.fetchChessFilesClicked)
        grid.addWidget(w_get_chess, irow, 0)
        
        w_del_sims = QPushButton('Fetch N deposition')
        helpText = ''
        w_del_sims.setToolTip(helpText)
        w_del_sims.clicked.connect(self.fetchNdeposClicked)
        grid.addWidget(w_del_sims, irow, 1)

        w_add_vig = QPushButton('Add vigour')
        helpText = 'edits specified file management.dat file'
        w_add_vig.setToolTip(helpText)
        w_add_vig.clicked.connect(self.addVigourClicked)
        grid.addWidget(w_add_vig, irow, 2)

        w_concat_met = QPushButton('Concat met')
        helpText = 'concatenate ECOSSE met files into a single file with years'
        w_concat_met.setToolTip(helpText)
        w_concat_met.clicked.connect(self.concatMetFilesClicked)
        grid.addWidget(w_concat_met, irow, 3)

        w_list_path = QPushButton('List paths')
        helpText = 'set of directories where executable programs are located making up the PATH environment variable'
        w_list_path.setToolTip(helpText)
        w_list_path.clicked.connect(self.listPathsClicked)
        grid.addWidget(w_list_path, irow, 4)

        w_clean_sv = QPushButton('Clean SV')
        helpText = 'remove fort.123 files from SV runs'
        w_clean_sv.setToolTip(helpText)
        w_clean_sv.clicked.connect(self.cleanSvClicked)
        grid.addWidget(w_clean_sv, irow, 5)

        # line 20
        # =======
        irow += 1
        w_sep_proj = QPushButton('Separate projects')
        helpText = 'Separate site specific from limited data ECOSSE projects'
        w_sep_proj.setToolTip(helpText)
        w_sep_proj.clicked.connect(self.separateProjsClicked)
        grid.addWidget(w_sep_proj, irow, 0)

        w_copy = QCheckBox('Copy')
        helpText = 'Copy instead of rename directories'
        w_copy.setToolTip(helpText)
        grid.addWidget(w_copy, irow, 1)
        w_copy.setChecked(False)
        self.w_copy = w_copy

        w_cpy_mnfsts = QPushButton('Copy manifests')
        helpText = 'Copy manifests'
        w_cpy_mnfsts.setToolTip(helpText)
        w_cpy_mnfsts.setEnabled(False)
        w_cpy_mnfsts.clicked.connect(self.copyManifestsClicked)
        grid.addWidget(w_cpy_mnfsts, irow, 2)

        w_chck_svout = QPushButton('Check SV out')
        helpText = 'run an instance of ECOSSE'
        w_chck_svout.setToolTip(helpText)
        w_chck_svout.clicked.connect(self.checkSvClicked)
        grid.addWidget(w_chck_svout, irow, 3)

        w_run_ecosse = QPushButton('Run Ecosse')
        helpText = 'run an instance of ECOSSE'
        w_run_ecosse.setToolTip(helpText)
        w_run_ecosse.clicked.connect(self.runEcosseClicked)
        grid.addWidget(w_run_ecosse, irow, 4)

        exit = QPushButton('Exit', self)
        grid.addWidget(exit, irow, 6)
        exit.clicked.connect(self.exitClicked)

        # line 21
        # =======
        irow += 1
        w_get_chess = QPushButton('Fetch CHESS daily')
        helpText = 'Download complete set of CHESS daily files'
        w_get_chess.setToolTip(helpText)
        w_get_chess.clicked.connect(self.fetchDailyChessFilesClicked)
        grid.addWidget(w_get_chess, irow, 0)

        w_daily_mnthly = QPushButton('Daily to Monthly')
        helpText = 'Read CHESS daily and write monthly NC files'
        w_daily_mnthly.setToolTip(helpText)
        w_daily_mnthly.clicked.connect(self.dailyToMonthlyChessClicked)
        grid.addWidget(w_daily_mnthly, irow, 1)

        w_chess_hist = QPushButton('Fetch CHESS historic')
        helpText = 'Download complete set of CHESS daily historic files'
        w_chess_hist.setToolTip(helpText)
        w_chess_hist.clicked.connect(self.fetchChessHistoricClicked)
        grid.addWidget(w_chess_hist, irow, 3)

        # =======
        irow += 1
        w_wrldclim = QPushButton('Fetch WorldClim')
        helpText = 'Download complete set of WorldClim monthly files'
        w_wrldclim.setToolTip(helpText)
        w_wrldclim.clicked.connect(self.fetchWorldClimFilesClicked)
        grid.addWidget(w_wrldclim, irow, 0)

        # ===============
        rh_vbox.addLayout(grid)     # add grid to RH vertical box
        hbox.addLayout(rh_vbox)     # vertical box goes into horizontal box
        self.setLayout(hbox)        # the horizontal box fits inside the window

        self.setGeometry(300, 300, 690, 250)   # posx, posy, width, height
        self.setWindowTitle('Collection of Global Ecosse related utilities')

        # reads and set values from last run
        # ==================================
        read_config_file(self)
        # self.w_lbl05.setText(check_sims_direcs(self))

    def fetchWorldClimFilesClicked(self):

        fetch_worldclim_monthly(self)

        return

    def dailyToMonthlyChessClicked(self):

        chess_daily_to_mnthly(self)

        return

    def checkSvClicked(self):

        ref_dir = self.w_lbl04.text()
        check_sv_runs(self, ref_dir)

        return

    def cleanSvClicked(self):

        ref_dir = self.w_lbl04.text()
        clean_sv_runs(ref_dir)

        return

    def copyManifestsClicked(self):

        # copy_manifests(self)

        return

    def separateProjsClicked(self):

        separate_projects(self)

        return

    def concatMetFilesClicked(self):

        concat_met_files(self)

        return

    def runEcosseClicked(self):

        create_ecosse_inst(self)

        return

    def addVigourClicked(self):

        add_vigour(self)

        return

    def listPathsClicked(self):

        path_env = getenv('PATH')
        for dir_name in sorted(path_env.split(';')):
            print(dir_name)
        return

    def fetchRefDir(self):

        # We pop up the QtGui.QFileDialog. The first string in the getOpenFileName()
        # method is the caption. The second string specifies the dialog working directory.
        # By default, the file filter is set to All files (*)
        ref_dir = self.w_lbl04.text()
        fname = ref_dir
        fname = QFileDialog.getExistingDirectory(self, 'Select directory', fname)
        if fname != '' and fname != ref_dir:
            self.w_lbl04.setText(fname)
            # self.w_lbl05.setText(check_sims_direcs(self))

    def fetchChessHistoricClicked(self):

        fetch_chess_daily_hist(self)

    def fetchChessFilesClicked(self):

         fetch_chess_files(self)

    def fetchDailyChessFilesClicked(self):

        fetch_chess_daily(self)

    def fetchNdeposClicked(self):

         fetch_n_depos_files(self)

    def exitClicked(self):

        # write last path selections
        write_config_file(self)

        self.close()

def main():

    app = QApplication(sys.argv)  # create QApplication object
    form = Form()     # instantiate form
    form.show()       # paint form
    sys.exit(app.exec_())   # start event loop

if __name__ == '__main__':
    main()
