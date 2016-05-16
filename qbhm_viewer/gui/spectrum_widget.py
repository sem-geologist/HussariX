# -*- coding: utf-8 -*-
#
# Copyright 2016 Petras Jokubauskas
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any project and source this library is coupled.
# If not, see <http://www.gnu.org/licenses/>.
#

from PyQt4 import QtCore, QtGui

from utils import xray_util as xu

from . import element_table as pet
pet.debug_flag = 0

import pyqtgraph as pg


# dealling with greek letters, where windows dos retards made it
# into  latin:

dos_greek = {'a': 'α', 'b': 'β', 'g': 'γ'}


def utfize(text):
    """replace the a,b,c latin letters used by ms-dos retards to greek α, β, γ
    """
    return ''.join(dos_greek[s] if s in dos_greek else s for s in text)


class AutoEditor(QtGui.QDialog):
    """widget for entering min max x and y for
    auto range of the spectra"""
    def __init__(self, title, x_range, y_range, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self._setup_ui()
        self._setup_connections(x_range, y_range)

    def _setup_ui(self):
        self.groupBox1 = QtGui.QGroupBox("x min-max", self)
        self.gridLayout = QtGui.QHBoxLayout(self.groupBox1)
        self.x_min = QtGui.QLineEdit()
        self.x_max = QtGui.QLineEdit()
        self.gridLayout.addWidget(self.x_min)
        self.gridLayout.addWidget(self.x_max)
        self.verticalLayout.addWidget(self.groupBox1)

        self.groupBox2 = QtGui.QGroupBox("y min-max", self)
        self.gridLayout2 = QtGui.QHBoxLayout(self.groupBox2)
        self.y_min = QtGui.QLineEdit()
        self.y_max = QtGui.QLineEdit()
        self.gridLayout2.addWidget(self.y_min)
        self.gridLayout2.addWidget(self.y_max)
        self.verticalLayout.addWidget(self.groupBox2)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
                                          QtGui.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)

    def _setup_connections(self, x_range, y_range):
        self.x_min.setText(str(x_range[0]))
        self.x_max.setText(str(x_range[1]))
        self.y_min.setText(str(y_range[0]))
        self.y_max.setText(str(y_range[1]))
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)

    def return_ranges(self):
        x_range = (float(self.x_min.text()), float(self.x_max.text()))
        y_range = (float(self.y_min.text()), float(self.y_max.text()))
        return x_range, y_range


class PenEditor(QtGui.QDialog):
    def __init__(self, text_size, text_color, pen, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle('customize preview')
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self._setup_ui()
        self._setup_connections(text_size, text_color, pen)

    def _setup_ui(self):
        self.groupBox1 = QtGui.QGroupBox("Text Style", self)
        self.formLayout = QtGui.QFormLayout(self.groupBox1)
        self.formLayout.setWidget(0,
                                  QtGui.QFormLayout.LabelRole,
                                  QtGui.QLabel('color'))
        self.text_color_btn = pg.ColorButton()
        self.formLayout.setWidget(0,
                                  QtGui.QFormLayout.FieldRole,
                                  self.text_color_btn)
        self.formLayout.setWidget(1,
                                  QtGui.QFormLayout.LabelRole,
                                  QtGui.QLabel('size'))
        self.text_size_spn = pg.SpinBox(value=12, bounds=(1, 64),
                                        suffix='pt', step=1,
                                        int=True)
        self.formLayout.setWidget(1,
                                  QtGui.QFormLayout.FieldRole,
                                  self.text_size_spn)
        self.verticalLayout.addWidget(self.groupBox1)

        self.groupBox2 = QtGui.QGroupBox("Line Style", self)
        self.formLayout2 = QtGui.QFormLayout(self.groupBox2)
        self.formLayout2.setWidget(0,
                                  QtGui.QFormLayout.LabelRole,
                                  QtGui.QLabel('color'))
        self.line_color_btn = pg.ColorButton()
        self.formLayout2.setWidget(0,
                                  QtGui.QFormLayout.FieldRole,
                                  self.line_color_btn)
        self.formLayout2.setWidget(1,
                                  QtGui.QFormLayout.LabelRole,
                                  QtGui.QLabel('width'))
        self.line_width_spn = pg.SpinBox(value=2, bounds=(0.1, 10),
                                         dec=1, minStep=0.1)
        self.formLayout2.setWidget(1,
                                  QtGui.QFormLayout.FieldRole,
                                  self.line_width_spn)
        self.verticalLayout.addWidget(self.groupBox2)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel |
                                          QtGui.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)

    def _setup_connections(self, text_size, text_color, pen):
        self.text_size_spn.setValue(text_size)
        self.text_color_btn.setColor(text_color)
        self.line_color_btn.setColor(pen.color())
        self.line_width_spn.setValue(pen.width())
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)

    def return_styles(self):
        text_size = self.text_size_spn.value()
        text_color = self.text_color_btn.color()
        line_pen = pg.mkPen(color=self.line_color_btn.color(),
                            width=self.line_width_spn.value())
        return text_size, text_color, line_pen



class EDSCanvas(pg.PlotWidget):
    def __init__(self, kv=15):
        pg.PlotWidget.__init__(self)
        #p1 the main plotItem/canvas
        #p2 secondary viewbox for EDS preview lines
        self.p1 = self.plotItem
        self.p1.setLabels(left='cts', bottom='keV')
        self.p2 = pg.ViewBox()
        self.p1.scene().addItem(self.p2)
        self.p2.setXLink(self.p1)
        self.updateViews()
        self.set_kv(kv)
        self.p1.vb.sigResized.connect(self.updateViews)
        self.setXRange(0.45, self.kv)
        self.p1.setLimits(yMin=0, xMin=-0.5)
        self.p2.setLimits(yMin=0)
        self.p2.setYRange(0,1)
        self.prev_text_size = 12
        self.prev_marker_pen = pg.mkPen((255,200,255, 180), width=2)
        self.prev_text_color = pg.mkColor((200,200,200))
        #self.doubleClicked.connect(self.tweek_preview_style)
        
    def tweek_preview_style(self):
        style_dlg = PenEditor(self.prev_text_size,
                              self.prev_text_color,
                              self.prev_marker_pen)
        if style_dlg.exec_():
            values = style_dlg.return_styles()
            self.prev_text_size, self.prev_text_color,\
            self.prev_marker_pen = values
    
    def set_kv(self, kv):
        self.kv = kv
        self.p1.setLimits(xMax=self.kv)
        
    def updateViews(self):
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)
    
    def previewLines(self, element, kv=None):
        if kv == None:
            kv = self.kv
        self.p2.clear()
        lines = xu.xray_lines_for_plot(element, kv)
        for i in lines:
            line = pg.PlotCurveItem([i[1], i[1]],
                                    [0, i[2]],
                                    pen=self.prev_marker_pen)
            self.p2.addItem(line)
            html_color = 'rgba({0}, {1}, {2}, {3})'.format(
                self.prev_text_color.red(),
                self.prev_text_color.green(),
                self.prev_text_color.blue(),
                self.prev_text_color.alpha())
            text = pg.TextItem(html="""<body style="font-size:{2}pt;
                color:{3};">{0}<sub>{1}</sub></body>""".format(
                                element, utfize(i[0]),
                                self.prev_text_size, html_color),
                               anchor=(0., 0.))
            self.p2.addItem(text)
            text.setPos(i[1], i[2])
    
    def clearPreview(self, element):
        self.p2.clear()
        
    def addLines(self, element, kv=None):
        pass
    
    def auto_custom(self):
        pass


class CustomToolButton(QtGui.QToolButton):
    
    def __init__(self, parent = None):
        QtGui.QToolButton.__init__(self, parent)
        self.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
    
    def set_action_to_default(self):
        action = self.sender()
        if action != self.defaultAction():
            self.setDefaultAction(action)
            self.setToolTip(action.text())


class EDSSpectraGUI(QtGui.QMainWindow):
    def __init__(self, parent=None, icon_size=None, pet_opacity=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.resize(550,500)
        self.toolbar = QtGui.QToolBar('tools', parent=self)
        self._pet_opacity = pet_opacity
        if icon_size is not None:
            self.toolbar.setIconSize(QtCore.QSize(icon_size,
                                                icon_size))
        self.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)
        self.centralwidget = QtGui.QWidget()
        self.setCentralWidget(self.centralwidget)
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self._setup_toolbar()
        self.canvas = EDSCanvas()
        self._setup_connections()
        self.horizontalLayout.addWidget(self.canvas)
        
    def _setup_connections(self):
        self.pet.enableElementPrev.connect(self.canvas.previewLines)
        self.pet.disableElementPrev.connect(self.canvas.clearPreview)
        self.config_preview.triggered.connect(self.canvas.tweek_preview_style)
        self.pet.hv_value.valueChanged.connect(self.canvas.set_kv)
        self.actionFullscreen.triggered.connect(self.go_fullscreen)
        self.actionWindowed.triggered.connect(self.go_windowed)
        
    def _setup_toolbar(self):
        self.fullscreen_button =QtGui.QToolButton()
        self.toolbar.addWidget(self.fullscreen_button)
        self.actionFullscreen = QtGui.QAction(self)
        self.actionFullscreen.setIcon(QtGui.QIcon('gui/icons/tango_fullscreen.svg'))
        self.actionWindowed = QtGui.QAction(self)
        self.actionWindowed.setIcon(QtGui.QIcon('gui/icons/windowed.svg'))
        self.fullscreen_button.setDefaultAction(self.actionFullscreen)
        #add spacer:
        self._empty2 = QtGui.QWidget()
        self._empty2.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty2)
        self.actionElementTable = QtGui.QAction(self)
        self.actionElementTable.setIcon(QtGui.QIcon('gui/icons/pt.svg'))
        #self.actionElementTable.setCheckable(True)
        self.toolbar.addAction(self.actionElementTable)
        self._setup_pet()
        self.actionElementTable.triggered.connect(self.show_pet)
        self.toolbar.addSeparator()
        self.auto_button = CustomToolButton(self)
        self._setup_auto()
        self.toolbar.addWidget(self.auto_button)
        self.config_button = CustomToolButton(self)
        self.config_button.setIcon(QtGui.QIcon('gui/icons/tango_preferences_system.svg'))
        self._setup_config()
        self.toolbar.addWidget(self.config_button)
        self._empty1 = QtGui.QWidget()
        self._empty1.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty1)
        
        
    def _setup_auto(self):
        menu = QtGui.QMenu('auto range')
        self.auto_all = QtGui.QAction(QtGui.QIcon('gui/icons/auto_all.svg'),
                                 'all', self.auto_button)
        self.auto_width = QtGui.QAction(QtGui.QIcon('gui/icons/auto_width.svg'),
                                   'width', self.auto_button)
        self.auto_height = QtGui.QAction(QtGui.QIcon('gui/icons/auto_height.svg'),
                                    'height', self.auto_button)
        self.auto_custom = QtGui.QAction(QtGui.QIcon('gui/icons/auto_custom.svg'),
                                    'custom', self.auto_button)
        self.custom_conf = QtGui.QAction('custom config.', self.auto_button)
        action_list = [self.auto_all, self.auto_width, self.auto_height,
                       self.auto_custom, self.custom_conf]
        for i in action_list[:-1]:
            i.triggered.connect(self.auto_button.set_action_to_default)
        menu.addActions(action_list)
        self.auto_button.setMenu(menu)
        self.auto_button.setDefaultAction(self.auto_all)
        
    def _setup_config(self):
        menu = QtGui.QMenu('config')
        self.config_preview = QtGui.QAction(QtGui.QIcon('gui/icons/tango_preferences_system.svg'),
                                       'preview style',
                                       self.config_button)
        self.config_burned = QtGui.QAction(QtGui.QIcon('gui/icons/tango_preferences_system.svg'),
                                       'burned style',
                                       self.config_button)
        action_list = [self.config_preview, self.config_burned]
        for i in action_list:
            i.triggered.connect(self.config_button.set_action_to_default)
        menu.addActions(action_list)
        self.config_button.setMenu(menu)
        self.config_button.setDefaultAction(self.config_preview)
        
    def _setup_pet(self):
        self.dock_pet_win = QtGui.QDockWidget('Periodic table', self)
        
        self.pet = pet.ElementTableGUI(self.dock_pet_win)
        self.pet.hv_value = QtGui.QDoubleSpinBox()
        self.pet.hv_value.setValue(15.)
        self.pet.hv_value.setSuffix(" kV")
        self.pet.hv_value.setToolTip(
"""set HV value which restricts x axis and
influences heights of preview lines as function
of effectivness (2.7 rule)""")
        self.pet.hv_value.setRange(0.1, 1e4)
        self.pet.setCellWidget(8, 0, self.pet.hv_value)
        #self.dock_pet_win = QtGui.QDockWidget(self)
        self.dock_pet_win.setWidget(self.pet)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_pet_win)
        self.dock_pet_win.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
        self.dock_pet_win.setFloating(True)
        if self._pet_opacity:
            self.dock_pet_win.setWindowOpacity(self._pet_opacity)
        self.dock_pet_win.hide()
        
    def add_table(self, name):
        self.tableView[name] = QtGui.QTableView(self.tabWidget)
        self.tabWidget.addTab(self.tableView[name], name)
        
    def show_pet(self):
        #self.pet.setWindowOpacity(0.9)
        if self.dock_pet_win.isVisible():
            self.dock_pet_win.hide()
        else:
            self.dock_pet_win.show()
    
    def go_fullscreen(self):
        if self.parent() is not None:
            self.windowed_parent = self.parent()
            self.index_in_parent = self.windowed_parent.indexOf(self)
        self.windowed_flags = self.windowFlags()
        self.windowed_geometry = self.geometry()
        self.setParent(None)
        self.showFullScreen()
        self.fullscreen_button.removeAction(self.actionFullscreen)
        self.fullscreen_button.setDefaultAction(self.actionWindowed)
        
    def go_windowed(self):
        self.showNormal()
        if 'windowed_parent' in self.__dict__:
            self.windowed_parent.insertWidget(self.index_in_parent, self)
        self.setGeometry(self.windowed_geometry)
        self.fullscreen_button.removeAction(self.actionWindowed)
        self.fullscreen_button.setDefaultAction(self.actionFullscreen)
