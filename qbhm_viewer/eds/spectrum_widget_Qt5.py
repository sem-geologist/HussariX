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

from PyQt5 import QtCore, Qt,  QtGui,  QtWidgets
import pyqtgraph as pg

from . import xray_util as xu
from .node import ElementLineTreeModel, SimpleDictNode

from . import element_table_Qt5
from os import path
import json

main_path = path.join(path.dirname(__file__), path.pardir)
icon_path = path.join(main_path, 'icons')
conf_path = path.join(main_path,
                      'configurations',
                      'lines.json')

with open(conf_path) as fn:
    jsn = fn.read()
lines = json.loads(jsn)


# dealling with greek letters, where windows dos retards made it
# into  latin:

dos_greek = {'a': 'α', 'b': 'β', 'g': 'γ'}


def utfize(text):
    """replace the a,b,c latin letters used by retards stuck in
    ms-dos age to greek α, β, γ
    """
    return ''.join(dos_greek[s] if s in dos_greek else s for s in text)


class XRayElementTable(element_table_Qt5.ElementTableGUI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setSpan(0, 3, 1, 3)  # for preview option
        self.setSpan(1, 3, 1, 3)  # for line intensity filter
        self.preview = Qt.QTableWidgetItem('preview')
        self.setItem(0, 3, self.preview)
        self.previewCheck = self.item(0, 3)
        self.previewCheck.setCheckState(QtCore.Qt.Checked)
        self.hv_value = Qt.QDoubleSpinBox()
        self.hv_value.setValue(15.)
        self.hv_value.setSuffix(" kV")
        self.hv_value.setToolTip(''.join(['set HV value which restricts x',
                                          'axis and influences\n',
                                          'heights of',
                                          'preview lines as function\n',
                                          ' of effectivness (2.7 rule)']))
        self.hv_value.setRange(0.1, 1e4)
        self.setCellWidget(1, 3, self.hv_value)
        self.itemChanged.connect(self.setPreviewEnabled)
    
    def setPreviewEnabled(self):
        self.preview_enabled = self.previewCheck.checkState()
        

class AutoEditor(Qt.QDialog):
    """widget for entering min max x and y for
    auto range of the spectra"""
    def __init__(self, title, x_range, y_range, parent=None):
        Qt.QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.verticalLayout = Qt.QVBoxLayout(self)
        self._setup_ui()
        self._setup_connections(x_range, y_range)

    def _setup_ui(self):
        self.groupBox1 = Qt.QGroupBox("x min-max", self)
        self.gridLayout = Qt.QHBoxLayout(self.groupBox1)
        self.x_min = Qt.QLineEdit()
        self.x_max = Qt.QLineEdit()
        self.gridLayout.addWidget(self.x_min)
        self.gridLayout.addWidget(self.x_max)
        self.verticalLayout.addWidget(self.groupBox1)

        self.groupBox2 = Qt.QGroupBox("y min-max", self)
        self.gridLayout2 = Qt.QHBoxLayout(self.groupBox2)
        self.y_min = Qt.QLineEdit()
        self.y_max = Qt.QLineEdit()
        self.gridLayout2.addWidget(self.y_min)
        self.gridLayout2.addWidget(self.y_max)
        self.verticalLayout.addWidget(self.groupBox2)

        self.buttonBox = Qt.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(Qt.QDialogButtonBox.Cancel |
                                          Qt.QDialogButtonBox.Ok)
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


class LeavableTreeView(QtWidgets.QTreeView):
    """Customised QTreeView to emit signal when mouse leaves
    emits mouseLeft signal
    """    
    mouseLeft = QtCore.pyqtSignal() 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        
    def leaveEvent(self, event):
        self.mouseLeft.emit()
        super().leaveEvent(event)
        

class LineEnabler(Qt.QWidget):
    
    def __init__(self, parent=None):
        Qt.QWidget.__init__(self,  parent)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.buttonHide = QtWidgets.QPushButton(self)
        self.buttonHide.setText('Hide')
        self.gridLayout.addWidget(self.buttonHide, 4, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40,
                                           QtWidgets.QSizePolicy.Minimum,
                                           QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 2, 1, 1)
        self.buttonToggle = QtWidgets.QPushButton(self)
        self.buttonToggle.setText('Save to custom')
        self.gridLayout.addWidget(self.buttonToggle, 2, 2, 1, 1)
        self.buttonSave = QtWidgets.QPushButton(self)
        self.buttonSave.setText('Save to default')
        self.gridLayout.addWidget(self.buttonSave, 1, 2, 1, 1)
        self.atom = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(40)
        self.atom.setFont(font)
        self.atom.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.atom.setFrameShadow(QtWidgets.QFrame.Raised)
        self.atom.setLineWidth(2)
        self.atom.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.atom, 0, 2, 1, 1)
        self.lineView = LeavableTreeView(self)
        self.gridLayout.addWidget(self.lineView, 0, 0, 4, 2)
        if parent is not None:
            self.buttonHide.pressed.connect(parent.hide)
        else:
            self.buttonHide.pressed.connect(self.hide)
        
    @QtCore.pyqtSlot(str)
    def set_element_lines(self,  element):
        if self.parent() is not None:
            if self.parent().isHidden():
                self.parent().show()
        else:
            self.show()
        self.atom.setText(element)
        node_tree = SimpleDictNode.node_builder(lines[element],
                                                name=element)
        model = ElementLineTreeModel(node_tree)
        self.lineView.setModel(model)
        

class PenEditor(Qt.QDialog):
    def __init__(self, text_size, text_color, pen, parent=None):
        Qt.QDialog.__init__(self, parent)
        self.setWindowTitle('customize preview')
        self.verticalLayout = Qt.QVBoxLayout(self)
        self._setup_ui()
        self._setup_connections(text_size, text_color, pen)

    def _setup_ui(self):
        self.groupBox1 = Qt.QGroupBox("Text Style", self)
        self.formLayout = Qt.QFormLayout(self.groupBox1)
        self.formLayout.setWidget(0,
                                  Qt.QFormLayout.LabelRole,
                                  Qt.QLabel('color'))
        self.text_color_btn = pg.ColorButton()
        self.formLayout.setWidget(0,
                                  Qt.QFormLayout.FieldRole,
                                  self.text_color_btn)
        self.formLayout.setWidget(1,
                                  Qt.QFormLayout.LabelRole,
                                  Qt.QLabel('size'))
        self.text_size_spn = pg.SpinBox(value=12, bounds=(1, 64),
                                        suffix='pt', step=1,
                                        int=True)
        self.formLayout.setWidget(1,
                                  Qt.QFormLayout.FieldRole,
                                  self.text_size_spn)
        self.verticalLayout.addWidget(self.groupBox1)

        self.groupBox2 = Qt.QGroupBox("Line Style", self)
        self.formLayout2 = Qt.QFormLayout(self.groupBox2)
        self.formLayout2.setWidget(0,
                                  Qt.QFormLayout.LabelRole,
                                  Qt.QLabel('color'))
        self.line_color_btn = pg.ColorButton()
        self.formLayout2.setWidget(0,
                                  Qt.QFormLayout.FieldRole,
                                  self.line_color_btn)
        self.formLayout2.setWidget(1,
                                  Qt.QFormLayout.LabelRole,
                                  Qt.QLabel('width'))
        self.line_width_spn = pg.SpinBox(value=2, bounds=(0.1, 10),
                                         dec=1, minStep=0.1)
        self.formLayout2.setWidget(1,
                                  Qt.QFormLayout.FieldRole,
                                  self.line_width_spn)
        self.verticalLayout.addWidget(self.groupBox2)
        self.buttonBox = Qt.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(Qt.QDialogButtonBox.Cancel |
                                          Qt.QDialogButtonBox.Ok)
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


class CustomViewBox(pg.ViewBox):
    """overriden pyqtgraph.ViewBox class with scaleBy method
    allowing to bound bottom during zoom to 0.0"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def scaleBy(self, s=None, center=None, x=None, y=None):
        """copied from pyqtgraph, with minimal mdification
        """
        if s is not None:
            scale = pg.Point(s)
        else:
            scale = [x, y]
        
        affect = [True, True]
        if scale[0] is None and scale[1] is None:
            return
        elif scale[0] is None:
            affect[0] = False
            scale[0] = 1.0
        elif scale[1] is None:
            affect[1] = False
            scale[1] = 1.0
            
        scale = pg.Point(scale)
            
        if self.state['aspectLocked'] is not False:
            scale[0] = scale[1]

        vr = self.targetRect()
        if center is None:
            center = pg.Point(vr.center())
        else:
            center = pg.Point(center)
        
        tl = center + (vr.topLeft()-center) * scale
        br = center + (vr.bottomRight()-center) * scale
        
        if not affect[0]:
            self.setYRange(tl.y(), br.y(), padding=0)
        elif not affect[1]:
            self.setXRange(tl.x(), br.x(), padding=0)
        else:
            new_rect = QtCore.QRectF(tl, br)
            #??? Why needs to be Top, it is intended to bound Bottom:
            new_rect.moveTop(0.0)
            self.setRange(new_rect, padding=0)


class EDSCanvas(pg.PlotWidget):
    def __init__(self, kv=15):
        pg.PlotWidget.__init__(self, viewBox=CustomViewBox())
        #p1 the main plotItem/canvas
        #p2 secondary viewbox for EDS preview lines
        #p3 third viewbox for EDS marked lines
        self.p1 = self.plotItem
        self.p1.setLabels(left='cts', bottom='keV')
        self.p2 = pg.ViewBox()
        self.p3 = pg.ViewBox()
        self.p1.scene().addItem(self.p2)
        self.p2.setXLink(self.p1)
        self.p3.setXLink(self.p1)
        self.p3.setYLink(self.p1)
        self.updateViews()
        self.set_kv(kv)
        self.p1.vb.sigResized.connect(self.updateViews)
        self.setXRange(0.45, self.kv)
        self.p1.setLimits(yMin=0, xMin=-0.5, )
        self.p3.setLimits(yMin=0)
        self.p2.setLimits(yMin=0)
        self.p2.setYRange(0,1)
        self.prev_text_size = 12
        self.prev_marker_pen = pg.mkPen((255,200,255, 180), width=2)
        self.prev_text_color = pg.mkColor((200,200,200))
    
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
    
    def previewLines(self, element, kv=None, lines=[]):
        if kv is None:
            kv = self.kv
        self.p2.clear()
        if len(lines) == 0:
            lines = xu.xray_lines_for_plot(element, kv)
        else:
            #TODO
            pass
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
                               anchor=(0., 1.))
            self.p2.addItem(text)
            text.setPos(i[1], i[2])
            
    def previewOneLine(self, element, line):
        energy = xu.xray_energy(element, line)
        gr_line = pg.PlotCurveItem([energy,  energy],
                        [0,  xu.xray_weight(element, line)], 
                        pen=self.prev_marker_pen)
        self.p2.addItem(gr_line)
    
    def clearPreview(self):
        self.p2.clear()
        
    def addLines(self, element, kv=None):
        pass
    
    def auto_custom(self):
        pass


class CustomToolButton(Qt.QToolButton):
    
    def __init__(self, parent = None):
        Qt.QToolButton.__init__(self, parent)
        self.setPopupMode(Qt.QToolButton.MenuButtonPopup)
    
    def set_action_to_default(self):
        action = self.sender()
        if action != self.defaultAction():
            self.setDefaultAction(action)
            self.setToolTip(action.text())


class EDSSpectraGUI(Qt.QMainWindow):
    def __init__(self, parent=None, icon_size=None, pet_opacity=None):
        Qt.QMainWindow.__init__(self, parent)
        self.resize(550,550)
        self.toolbar = Qt.QToolBar('tools', parent=self)
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self._pet_opacity = pet_opacity
        if icon_size is not None:
            self.toolbar.setIconSize(QtCore.QSize(icon_size,
                                                icon_size))
        self.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)
        self.centralwidget = Qt.QWidget()
        self.setCentralWidget(self.centralwidget)
        self.horizontalLayout = Qt.QHBoxLayout(self.centralwidget)
        self._setup_toolbar()
        self.canvas = EDSCanvas()
        self._setup_connections()
        self.horizontalLayout.addWidget(self.canvas)
        
    def _setup_connections(self):
        self.pet.elementHoveredOver.connect(self.canvas.previewLines)
        self.pet.elementHoveredOff.connect(self.canvas.clearPreview)
        self.config_preview.triggered.connect(
            self.canvas.tweek_preview_style)
        self.pet.hv_value.valueChanged.connect(self.canvas.set_kv)
        self.actionFullscreen.triggered.connect(self.go_fullscreen)
        self.actionWindowed.triggered.connect(self.go_windowed)
        self.pet.someButtonRightClicked.connect(
            self.lineSelector.set_element_lines)
        self.lineSelector.lineView.entered.connect(
            self.preview_hovered_lines)
        self.lineSelector.lineView.mouseLeft.connect(
            self.canvas.clearPreview)
        
    def _setup_toolbar(self):
        self.actionFullscreen = Qt.QAction(self)
        self.actionFullscreen.setIcon(
            Qt.QIcon(path.join(icon_path, 'tango_fullscreen.svg')))
        self.actionWindowed = Qt.QAction(self)
        self.actionWindowed.setIcon(Qt.QIcon(path.join(icon_path,
                                                       'windowed.svg')))
        #add spacer:
        self._empty2 = Qt.QWidget()
        self._empty2.setSizePolicy(Qt.QSizePolicy.Expanding,
                                   Qt.QSizePolicy.Expanding)
        self.toolbar.addAction(self.actionFullscreen)
        self.toolbar.addWidget(self._empty2)
        self.actionElementTable = Qt.QAction(self)
        self.actionElementTable.setIcon(Qt.QIcon(path.join(icon_path,
                                                           'pt.svg')))
        self.toolbar.addAction(self.actionElementTable)
        self._setup_pet()
        self.actionElementTable.triggered.connect(self.show_pet)
        self.toolbar.addSeparator()
        self.auto_button = CustomToolButton(self)
        self._setup_auto()
        self.toolbar.addWidget(self.auto_button)
        self.config_button = CustomToolButton(self)
        self.config_button.setIcon(
            Qt.QIcon(path.join(icon_path, 'tango_preferences_system.svg')))
        self._setup_config()
        self.toolbar.addWidget(self.config_button)
        self._empty1 = Qt.QWidget()
        self._empty1.setSizePolicy(Qt.QSizePolicy.Expanding,
                                   Qt.QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty1)
        
        
    def _setup_auto(self):
        menu = Qt.QMenu('auto range')
        self.auto_all = Qt.QAction(Qt.QIcon(path.join(icon_path,
                                                      'auto_all.svg')),
                                   'all', self.auto_button)
        self.auto_width = Qt.QAction(Qt.QIcon(path.join(icon_path,
                                                        'auto_width.svg')),
                                     'width', self.auto_button)
        self.auto_height = Qt.QAction(Qt.QIcon(path.join(icon_path,
                                                    'auto_height.svg')),
                                      'height', self.auto_button)
        self.auto_custom = Qt.QAction(Qt.QIcon(path.join(icon_path,
                                                    'auto_custom.svg')),
                                      'custom', self.auto_button)
        self.custom_conf = Qt.QAction('custom config.', self.auto_button)
        action_list = [self.auto_all, self.auto_width, self.auto_height,
                       self.auto_custom, self.custom_conf]
        for i in action_list[:-1]:
            i.triggered.connect(self.auto_button.set_action_to_default)
        menu.addActions(action_list)
        self.auto_button.setMenu(menu)
        self.auto_button.setDefaultAction(self.auto_all)
        
    def _setup_config(self):
        menu = Qt.QMenu('config')
        self.config_preview = Qt.QAction(Qt.QIcon(path.join(icon_path,
                                        'tango_preferences_system.svg')),
                                    'preview style',
                                    self.config_button)
        self.config_burned = Qt.QAction(Qt.QIcon(path.join(icon_path,
                                        'tango_preferences_system.svg')),
                                    'burned style',
                                    self.config_button)
        action_list = [self.config_preview, self.config_burned]
        for i in action_list:
            i.triggered.connect(self.config_button.set_action_to_default)
        menu.addActions(action_list)
        self.config_button.setMenu(menu)
        self.config_button.setDefaultAction(self.config_preview)
        
    def _setup_pet(self):
        self.dock_pet_win = Qt.QDockWidget('Periodic table', self)
        self.dock_pet_win.setSizePolicy(QtGui.QSizePolicy.Maximum,
                                        QtGui.QSizePolicy.Maximum)
        self.dock_line_win = Qt.QDockWidget('Line selection', self)
        self.pet = XRayElementTable(parent=self.dock_pet_win)
        self.lineSelector = LineEnabler(self.dock_line_win)
        self.dock_pet_win.setWidget(self.pet)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.dock_pet_win)
        self.dock_pet_win.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
        self.dock_pet_win.setFloating(True)
        self.dock_line_win.setWidget(self.lineSelector)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.dock_line_win)
        self.dock_line_win.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
        self.dock_line_win.setFloating(True)
        if self._pet_opacity:
            self.dock_pet_win.setWindowOpacity(self._pet_opacity)
        self.dock_line_win.hide()
        self.dock_pet_win.hide()
        
    #deprecated:
    #def add_table(self, name):
    #    self.tableView[name] = Qt.QTableView(self.tabWidget)
    #    self.tabWidget.addTab(self.tableView[name], name)
        
    def show_pet(self):
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
        self.toolbar.insertAction(self.actionFullscreen,
                                  self.actionWindowed)
        self.toolbar.removeAction(self.actionFullscreen)
        
    def go_windowed(self):
        self.showNormal()
        if 'windowed_parent' in self.__dict__:
            self.windowed_parent.insertWidget(self.index_in_parent, self)
        self.setGeometry(self.windowed_geometry)
        self.toolbar.insertAction(self.actionWindowed,
                                  self.actionFullscreen)
        self.toolbar.removeAction(self.actionWindowed)
        
    def preview_hovered_lines(self, item):
        self.canvas.clearPreview()
        
        if item is None:
            self.canvas.clearPreview()
            return
        
        h_item = self.lineSelector.lineView.model().getNode(item)
        # hovered item/node ^
        path = h_item.get_tree_path().split(' ')
        
        if 'line' in h_item.name:
            item_type = 'family'
        elif 'line' in h_item._parent.name:
            item_type = 'line'
        else:
            item_type = 'element'
            
        if item_type == 'line':
            element = path[-3]
            line = path[-1]
            self.canvas.previewOneLine(element, line)
        elif item_type == 'family':
            element = path[-2]
            for i in h_item._children:
                self.canvas.previewOneLine(element, i.name)
        elif item_type == 'element':
            self.canvas.previewLines(element)
        
