from PyQt5 import QtGui, Qt, QtWidgets

from lib.ui import mainWindowUI

from lib.ui import spectrum_widget_Qt5 as swidget
from lib.ui import image_widget_Qt5 as iwidget
from lib.parsers import jeol

from math import log10

import pyqtgraph as pg

pg.setConfigOptions(imageAxisOrder='row-major')

import sys

from os.path import expanduser
home = expanduser("~")

SEM_PROJECT_TYPE = ['Jeol Analysis Station project (*.ASW)',
                    #'Bruker Project (*.rtx);;',
                   ]

class MainWindow(mainWindowUI.Ui_MainWindow,
                 QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self._setup_widgets()
        self.sample_models = {}
        self._setup_connections()
        self.current_view = None
    
    def _setup_widgets(self):
        self.spectra_wdg = swidget.EDSSpectraGUI(icon_size=24,
                                             pet_opacity=0.8)  #TODO configs
        spec_layout = QtGui.QHBoxLayout()
        spec_layout.setContentsMargins(0,0,0,0)
        self.spectraTab.setLayout(spec_layout)
        spec_layout.addWidget(self.spectra_wdg)
        self.spectra_wdg.setParent(self.spectraTab)
        
        self.image_wdg = iwidget.SEMImageGUI(icon_size=24)
        img_layout = QtGui.QHBoxLayout()
        img_layout.setContentsMargins(0,0,0,0)
        self.imagePlace.setLayout(img_layout)
        img_layout.addWidget(self.image_wdg)
        self.image_wdg.setParent(self.imagePlace)
    
    def scale_view(self, value):
        scale_val = (value, value*6/8)
        self.sampleView.setIconSize(Qt.QSize(*scale_val))
        
    def scale_tree_view(self, value):
        scale_val = (value, value*6/8)
        self.treeSampleView.setIconSize(Qt.QSize(*scale_val))
    
    def _setup_connections(self):
        self.sampleViewSlider.valueChanged.connect(self.scale_view)
        self.treeSampleViewSlider.valueChanged.connect(self.scale_tree_view)
        self.actionLoad.triggered.connect(self.load_project)
        
    def _postponed_connections(self):
        self.sampleView.selectionModel().currentChanged.connect(self.set_view)
        
    def load_project(self):
        
        file_ext = ';; '.join(SEM_PROJECT_TYPE)
        fd = QtGui.QFileDialog(self)
        da_file = fd.getOpenFileName(self,
                                     'Open SEM project file',
                                     home,
                                     file_ext)
        if da_file[1] == SEM_PROJECT_TYPE[0]: #jeol
            self.project = jeol.JeolProject(da_file[0])
            for i in range(len(self.project.samples)):
                self.sample_models[i] = jeol.JeolSampleViewListModel(
                    self.project.samples[i])
                self.projectBox.addItem('Sample '+str(i))
            self.sampleView.setModel(self.sample_models[0])
            self.treeSampleView.setModel(self.sample_models[0])
            self._postponed_connections()
            
    def set_view(self, *args):
        new_item = *args[0]
        self.image_wdg.canvas.clear()
        self.spectra_wdg.canvas.clear()
        view = self.sample_models[0].data(new_item, 0x0100)
        self.current_view = view
        size = 10 ** (int(log10(view.width)) - 1)
        self.image_wdg.canvas.addItem(view.def_image.pg_image_item)
        for i in view.eds_list:
            self.image_wdg.canvas.addItem(i.marker)
            self.spectra_wdg.canvas.addItem(i.pg_curve)
        self.image_wdg.scale_bar.updateBar()
        self.image_wdg.scale_bar.change_scale(size)
        self.image_wdg.scale_bar.update()
        self.image_wdg.canvas.vb.update()
        self.image_wdg.canvas.update()
        self.image_wdg.pg_graphics_layout.update()
        self.image_wdg.scale_bar.bar.update()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_()) 
