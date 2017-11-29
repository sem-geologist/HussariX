from PyQt5 import QtGui, Qt, QtWidgets

from lib.ui import mainWindowUI

from lib.ui import spectrum_widget_Qt5 as swidget
from lib.ui import image_widget_Qt5 as iwidget
from lib.parsers import jeol

from math import log10

import pyqtgraph as pg

import sys

from os.path import expanduser

pg.setConfigOptions(imageAxisOrder='row-major')

HOME = expanduser("~")

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
        self.current_sample_index = None

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
        self.sampleView.selectionModel().currentChanged.disconnect()
        self.projectBox.currentIndexChanged.connect(self.change_view_model)
        self.change_view_model(0)
        self.sampleView.customContextMenuRequested.connect(
            self.show_view_item_menu)

    def change_view_model(self, index):
        self.sampleView.setModel(self.sample_models[index])
        self.sampleView.selectionModel().currentChanged.connect(self.set_view)
        self.current_sample_index = index

    def load_project(self):

        file_ext = ';; '.join(SEM_PROJECT_TYPE)
        fd = QtGui.QFileDialog(self)
        da_file = fd.getOpenFileName(self,
                                     'Open SEM project file',
                                     HOME,
                                     file_ext)
        self.projectBox.disconnect()
        self.projectBox.clear()
        if da_file[1] == SEM_PROJECT_TYPE[0]: #jeol
            self.project = jeol.JeolProject(da_file[0])
            for i in range(len(self.project.samples)):
                self.sample_models[i] = jeol.JeolSampleViewListModel(
                    self.project.samples[i])
                self.projectBox.addItem(' '.join(['Sample', str(i)+':',
                                                  self.project.samples[i].memo]))
            self.sampleView.setModel(self.sample_models[0])
            self.treeSampleView.setModel(self.sample_models[0])
            self._postponed_connections()

    def clear_views(self):
        self.image_wdg.canvas.clear()
        self.spectra_wdg.canvas.clear()

    #def raiseContextMenu(self, ev):
        #menu = self.getContextMenus()

        ## Let the scene add on to the end of our context menu
        ## (this is optional)
        ##menu = self.scene().addParentContextMenus(self, menu, ev)

        #pos = ev.screenPos()
        #menu.popup(QtCore.QPoint(pos.x(), pos.y()))
        #return True

    ## This method will be called when this item's _children_ want to raise
    ## a context menu that includes their parents' menus.
    #def getViewContextMenus(self, event=None):
        #if self.menu is None:
            #self.menu = QtGui.QMenu()
            #self.menu.setTitle("axis options..")
                        
            #scale = QtGui.QWidgetAction(self.menu)
            #groupBox = QtGui.QGroupBox()
            #verticalLayout = QtGui.QVBoxLayout(groupBox)
            #self.energyButton.setParent(groupBox)
            #verticalLayout.addWidget(self.energyButton)
            #self.thetaButton.setParent(groupBox)
            #verticalLayout.addWidget(self.thetaButton)
            #scale.setDefaultWidget(groupBox)
            #self.menu.addAction(scale)
            #self.menu.scale = scale
            #self.menu.groupBox = groupBox
        #return self.menu

    def show_view_item_menu(self, point):

        index = self.sampleView.indexAt(point)
        view = self.sample_models[self.current_sample_index].data(index, 0x0100)
        if index.isValid() and len(view.image_list) > 1:
            print('context_menu_requested')
            menu = QtGui.QMenu()
            menu.setTitle('set primary image...')
            for i in view.image_list:
                print(i.metadata['Image']['Title'])
                action = QtGui.QAction(i.metadata['Image']['Title'])
                func = lambda : self.image_wdg.set_new_image(i.pg_image_item)
                action.triggered.connect(func)
                menu.addAction(action)

                #button = QtGui.QRadioButton(i.memo)
                #button.setParent(groupBox)
                #verticalLayout.addWidget(button)
            #menu.addAction(image)
            menu.exec(self.sampleView.mapToGlobal(point))

    def set_view(self, *args):
        new_item = args[0]
        self.image_wdg.canvas.clear()
        self.spectra_wdg.canvas.clear()
        view = self.sample_models[self.current_sample_index].data(new_item, 0x0100)
        self.current_view = view
        size = 10 ** (int(log10(view.width)) - 1)
        self.image_wdg.canvas.addItem(view.def_image.pg_image_item)
        for i in view.eds_list:
            self.image_wdg.canvas.addItem(i.marker)
            self.spectra_wdg.canvas.addItem(i.pg_curve)
        self.image_wdg.scale_bar.change_scale(size)
        self.image_wdg.scale_bar.updateBar()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_()) 
