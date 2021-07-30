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

from os import path
import json
from re import sub, findall
from math import log, log10, degrees, atan
from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
from pyqtgraph import InfiniteLine, mkPen
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtGui import QPen, QPixmap, QColor, QPainter, QIcon, QFont
from PyQt5.QtWidgets import (QWidget,
                             QAction,
                             QWidgetAction,
                             QLabel,
                             QMenu,
                             QListView,
                             QSizePolicy,
                             QAbstractScrollArea,
                             QHBoxLayout)

from .CamecaQtModels import (WDSPlotItem,
                             SpecXTALCombiModel)
from ..misc import xray_util as xu
from .node import ElementLineTreeModel, SimpleDictNode

from .qpet import element_table as qpet
from . import CustomWidgets as cw
from .CustomPGWidgets import CustomViewBox, CustomAxisItem
from .spectrum_curve import SpectrumCurveItem

main_path = path.join(path.dirname(__file__), path.pardir)
conf_path = path.join(main_path,
                      'configurations',
                      'lines.json')

with open(conf_path) as fn:
    jsn = fn.read()
lines = json.loads(jsn)

# dealling with windows-mind-slaves casted greek letters into latin:
dos_greek = {'a': 'α', 'b': 'β', 'c': 'γ', 'z': 'ζ'}


# QColor.name() returns the RGB not RGBA
def color_to_css(qcolor):
    """convert color to css string 'rgba(tuple)' format
       with alpha value. (QColor.name() is insufficient - without alpha)"""
    css_color = 'rgba({0}, {1}, {2}, {3})'.format(
                *pg.colorTuple(qcolor))
    return css_color


def darken_lighten(color, times, color_list=None, dark_mode=False):
    """return the list of recursively darkened/lighten QtColors
    darkening or lightening is chosen depending from dark_mode/used theme"""
    if color_list is None:
        color_list = [color]
    if times > 0:
        color = color.darker(150) if dark_mode else color.lighter(133)
        color_list.append(color)
        darken_lighten(color, times - 1, color_list=color_list,
                       dark_mode=dark_mode)
    return color_list


def menu_linestyle_entry_generator(pen_style=Qt.SolidLine, width=2,
                                   parent=None):
    """return QWidgetAction with QLabel widget as main widget where
    it is displaying sample line painted with provided pen_style and width"""
    menu_entry = QWidgetAction(parent)
    label = QLabel(parent)
    pix = QPixmap(74, 24)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    pen = QPen(QColor(246, 116, 0), width,
               pen_style)
    painter.setPen(pen)
    painter.drawLine(5, 12, 75, 12)  # ForegroundNeutral
    painter.end()
    label.setPixmap(pix)
    menu_entry.setDefaultWidget(label)
    menu_entry.pen = pen  # this attribute will hold the style
    return menu_entry


def utfize(text):
    """replace the a,b,c latin letters used by retards stuck in
    ms-dos age to greek α, β, γ
    """
    return ''.join(dos_greek[s] if s in dos_greek else s for s in text)

# pg.setConfigOptions(background=pg.mkColor(0, 43, 54))


def format_line(text, order=1):
    """wrap x-ray line plain text notation with html formating"""
    if text in xu.siegbahn_names:
        string = '{0}<i>{1}</i><sub>{2}</sub>'.format(text[0], text[1],
                                                      text[2:])
    else:
        string = sub(r'([1-7]+)', r'<sub>\1</sub>', text)
    if order == 2:
        string += '<sup>2<sup>nd</sup></sup>'
    elif order == 3:
        string += '<sup>3<sup>rd</sup></sup>'
    elif order > 3:
        string = '{0}<sup>{1}<sup>th</sup></sup>'.format(string, order)
    return string


class XtalListView(QListView):

    def __init__(self, parent=None):
        QListView.__init__(self, parent=parent)
        line_pattern_menu = QMenu("line pattern")
        for i in [Qt.SolidLine, Qt.DotLine, Qt.DashLine, Qt.DashDotLine,
                  Qt.DashDotDotLine]:
            action = menu_linestyle_entry_generator(pen_style=i,
                                                    parent=line_pattern_menu)
            line_pattern_menu.addAction(action)

            line_pattern_menu.addSeparator()
        self.l_pattern_menu = line_pattern_menu
        line_width_menu = QMenu("line width")
        for j in [1, 2, 3, 4, 5]:
            action = menu_linestyle_entry_generator(width=j,
                                                    parent=line_width_menu)
            line_width_menu.addAction(action)
            line_width_menu.addSeparator()
        self.l_width_menu = line_width_menu
        self.line_style_menu = QMenu()
        self.line_style_menu.addMenu(line_pattern_menu)
        self.line_style_menu.addMenu(line_width_menu)
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self.set_style_from_menu_entry)
        self.setMinimumSize(24, 24)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.setWhatsThis("""
        <h4>XTAL-spectrometer combination view.</h4>
        <p>
        This widget exposes aggregated categories from WDS file tree view;
        Categories are made for all unique combinations found in opened
        WDS files for spectrometer and diffracting crystal combinations</p>
        <p> When checking/tick'ing category, algorithm iterates through
        <bold>all</bold>
        opened WDS datasets and generates plotting curves which is added
        to plotting canvas. By default curves can be invisible, unless it
        is marked in the main WDS dataset/files tree.</p>
        <p> With right-mouse click on the category, curve line style and
        line weight of given category can be changed with a help of popup
        menu; Changes are going to be applied only to curves appearing on
        the canvas of this widget.</p>""")

    def set_style_from_menu_entry(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        pos_glob = self.mapToGlobal(pos)
        menu_entry = self.line_style_menu.exec(pos_glob)
        xtal_model = self.model()
        if menu_entry in self.l_pattern_menu.actions():
            role = xtal_model.LineStyleRole
            value = menu_entry.pen.style()
        elif menu_entry in self.l_width_menu.actions():
            role = xtal_model.LineWidthRole
            value = menu_entry.pen.width()
        else:
            return
        xtal_model.setData(index, value, role)


class XRayElementTable(qpet.ElementTableGUI):
    ordersChanged = Signal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.preview = QtWidgets.QCheckBox('emission')
        self.preview.setToolTip('preview emission lines')
        self.preview.setMinimumSize(16, 16)
        self.preview_edge = QtWidgets.QCheckBox('absorption')
        self.preview_edge.setToolTip('preview absorption edges')
        self.preview_edge.setMinimumSize(16, 16)
        self.siegbahn = QtWidgets.QCheckBox('Siegbahn')
        self.siegbahn.setToolTip("checked - Siegbahn notation "
                                 "(limited lines)\n"
                                 "unchecked - IUPAC notatation "
                                 "(more lines)")
        self.siegbahn.setMinimumSize(16, 16)
        self.hv_value = QtWidgets.QDoubleSpinBox()
        self.hv_value.setMinimumSize(16, 16)
        self.hv_value.setSuffix(" kV")
        self.hv_value.setToolTip("HV value restricts x axis (max) and\n"
                                 "approximates the heights of preview "
                                 "lines as\na function of effectivness "
                                 "of excitation\n(2.7 rule)")
        self.hv_value.setRange(0.1, 1e4)
        # add those parameters to the groupbox:
        self.preview_group = QtWidgets.QGroupBox('on hover:')
        self.preview_group.setLayout(QtWidgets.QGridLayout())
        self.p_layout = self.preview_group.layout()
        self.layout().addWidget(self.preview_group, 0, 2, 3, 10)
        self.p_layout.setMargin(0)
        self.p_layout.setHorizontalSpacing(0)
        self.p_layout.setVerticalSpacing(0)
        self.p_layout.addWidget(self.preview, 0, 0, 1, 1)
        self.p_layout.addWidget(self.preview_edge, 1, 0, 1, 1)
        self.p_layout.addWidget(self.siegbahn, 0, 1, 1, 1)
        self.p_layout.addWidget(self.hv_value, 1, 1, 1, 1)
        # set the default states:
        self.preview.setCheckState(Qt.Checked)
        self.siegbahn.setCheckState(Qt.Checked)
        self.hv_value.setValue(15.)
        self.preview_edge.setCheckState(Qt.Checked)
        self.orders_interface = QtWidgets.QLineEdit()
        self.orders_interface.setMinimumSize(16, 16)
        self.layout().addWidget(self.orders_interface, 0, 12, 1, 5)
        self.orders_interface.setToolTip("orders of diffracted lines\n"
                                         "to be previewed")
        self.orders = set([1])
        self.orders_interface.setText('1')
        self.orders_interface.setClearButtonEnabled(True)
        self.orders_interface.returnPressed.connect(self.parseOrders)

    def parseOrders(self):
        orders = set()
        ptext = str(self.orders_interface.text())
        ranges = findall(r"([1-9])-\b([2-9]|1[0-5])\b", ptext)
        for i in ranges:
            orders.update(range(int(i[0]), int(i[1])))
        individual_values = findall(r"\b([1-9]|1[0-5])\b", ptext)
        orders.update([int(j) for j in individual_values])
        if len(orders) > 0:
            self.setOrders(orders)
            self.focusNextChild()
            self.ordersChanged.emit()
        else:
            self.setOrders(self.orders)

    def setOrders(self, orders):
        self.orders = orders
        orders_str = str(orders).strip('{').strip('}')
        self.orders_interface.setText(orders_str)


class FramelessXRayElementTable(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent=parent, **kwargs)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.pet = XRayElementTable(parent=self)
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.label = QtWidgets.QLabel('Element Table')
        self.label.setAlignment(Qt.AlignHCenter)
        if parent is not None:
            self.set_new_title(self.parent().name)
            self.parent().sig_name_had_changed.connect(self.set_new_title)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.pet)
        self.layout().setContentsMargins(0, 1, 0, 0)
        self.layout().setSpacing(0)

    def set_new_title(self, new_text):
        self.label.setText('Element Table of {}'.format(new_text))

    def mousePressEvent(self, event):
        self._mouse_clicked_x_coord = event.x()
        self._mouse_clicked_y_coord = event.y()

    def mouseMoveEvent(self, event):
        self.move(event.globalX() - self._mouse_clicked_x_coord,
                  event.globalY() - self._mouse_clicked_y_coord)


class AutoEditor(QtWidgets.QDialog):
    """widget for entering min max x and y for
    auto range of the spectra"""
    def __init__(self, title, x_range, y_range, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self._setup_ui()
        self._setup_connections(x_range, y_range)

    def _setup_ui(self):
        self.groupBox1 = QtWidgets.QGroupBox("x min-max", self)
        self.gridLayout = QHBoxLayout(self.groupBox1)
        self.x_min = QtWidgets.QLineEdit()
        self.x_max = QtWidgets.QLineEdit()
        self.gridLayout.addWidget(self.x_min)
        self.gridLayout.addWidget(self.x_max)
        self.verticalLayout.addWidget(self.groupBox1)

        self.groupBox2 = QtWidgets.QGroupBox("y min-max", self)
        self.gridLayout2 = QHBoxLayout(self.groupBox2)
        self.y_min = QtWidgets.QLineEdit()
        self.y_max = QtWidgets.QLineEdit()
        self.gridLayout2.addWidget(self.y_min)
        self.gridLayout2.addWidget(self.y_max)
        self.verticalLayout.addWidget(self.groupBox2)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel |
            QtWidgets.QDialogButtonBox.Ok)
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


class LineEnabler(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self,  parent)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.buttonHide = QtWidgets.QPushButton(self)
        self.buttonHide.setText('Hide')
        self.gridLayout.addWidget(self.buttonHide, 4, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Minimum,
                                           QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 2, 1, 1)
        self.buttonToggle = QtWidgets.QPushButton(self)
        self.buttonToggle.setText('Save to custom')
        self.gridLayout.addWidget(self.buttonToggle, 2, 2, 1, 1)
        self.buttonSave = QtWidgets.QPushButton(self)
        self.buttonSave.setText('Save to default')
        self.gridLayout.addWidget(self.buttonSave, 1, 2, 1, 1)
        self.atom = QLabel(self)
        font = QFont()
        font.setPointSize(40)
        self.atom.setFont(font)
        self.atom.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.atom.setFrameShadow(QtWidgets.QFrame.Raised)
        self.atom.setLineWidth(2)
        self.atom.setAlignment(Qt.AlignCenter)
        self.gridLayout.addWidget(self.atom, 0, 2, 1, 1)
        self.lineView = cw.LeavableTreeView(self)
        self.gridLayout.addWidget(self.lineView, 0, 0, 4, 2)
        if parent is not None:
            self.buttonHide.pressed.connect(parent.hide)
        else:
            self.buttonHide.pressed.connect(self.hide)

    @Slot(str)
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


class PenEditor(QtWidgets.QDialog):
    def __init__(self, font, text_color, pen, dark_mode=False, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle('customize preview')
        self.dark_mode = dark_mode
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.groupBox1 = QtWidgets.QGroupBox("Text Style", self)
        self.formLayout = QtWidgets.QFormLayout(self.groupBox1)
        self.formLayout.setWidget(0,
                                  QtWidgets.QFormLayout.LabelRole,
                                  QLabel('color'))
        self.text_color_btn = pg.ColorButton()
        self.formLayout.setWidget(0,
                                  QtWidgets.QFormLayout.FieldRole,
                                  self.text_color_btn)
        self.formLayout.setWidget(1,
                                  QtWidgets.QFormLayout.LabelRole,
                                  QLabel('size'))
        self.font_btn = QtWidgets.QToolButton()
        self.font_btn.setText('Fe_Ka')
        self.formLayout.setWidget(1,
                                  QtWidgets.QFormLayout.FieldRole,
                                  self.font_btn)
        self.verticalLayout.addWidget(self.groupBox1)

        self.groupBox2 = QtWidgets.QGroupBox("Line Style", self)
        self.formLayout2 = QtWidgets.QFormLayout(self.groupBox2)
        self.formLayout2.setWidget(0,
                                   QtWidgets.QFormLayout.LabelRole,
                                   QLabel('color'))
        self.line_color_btn = pg.ColorButton()
        self.formLayout2.setWidget(0,
                                   QtWidgets.QFormLayout.FieldRole,
                                   self.line_color_btn)
        self.formLayout2.setWidget(1,
                                   QtWidgets.QFormLayout.LabelRole,
                                   QLabel('width'))
        self.line_width_spn = pg.SpinBox(value=2, bounds=(0.1, 10),
                                         dec=1, minStep=0.1)
        self.formLayout2.setWidget(1,
                                   QtWidgets.QFormLayout.FieldRole,
                                   self.line_width_spn)
        self.verticalLayout.addWidget(self.groupBox2)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel |
                                          QtWidgets.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
        self._setup_connections(font, text_color, pen)
        self.setColorTooltip()

    def _setup_connections(self, font, text_color, pen):
        self.font_btn.setFont(font)
        self.text_color_btn.setColor(text_color)
        self.line_color_btn.setColor(pen.color())
        self.line_color_btn.sigColorChanged.connect(self.setColorTooltip)
        self.line_width_spn.setValue(pen.width())
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        self.font_btn.clicked.connect(self.set_font)

    def set_font(self):
        font_dlg = QtWidgets.QFontDialog()
        font, ok = font_dlg.getFont(self.font_btn.font(), parent=self)
        if ok:
            self.font_btn.setFont(font)
            self.font_btn.adjustSize()

    def make_color_html_string(self):
        colors = [i.name()
                  for i in darken_lighten(self.line_color_btn.color(), 8,
                                          dark_mode=self.dark_mode)]
        string = """
<table>
  <tr>
    <td>Color</td>
    <td></td>
  </tr>
  <tr>
    <td style='background-color:{}; width:30px'></td>
    <td >1<sup>st</sup> order</td>
  </tr>
  <tr>
    <td style='background-color:{}'></td>
    <td >2<sup>nd</sup> order</td>
  </tr>
  <tr>
    <td style='background-color:{}'></td>
    <td >3<sup>rd</sup> order</td>
  </tr>
  <tr>
    <td style='background-color:{}'></td>
    <td >4<sup>th</sup> order</td>
  </tr>
  <tr>
    <td style='background-color:{}'></td>
    <td >5<sup>th</sup> order</td>
  </tr>
  <tr>
    <td style='background-color:{}'></td>
    <td >6<sup>th</sup> order</td>
  </tr>
  <tr>
    <td style='background-color:{}'></td>
    <td >7<sup>th</sup> order</td>
  </tr>
  <tr>
    <td style='background-color:{}'></td>
    <td >8<sup>th</sup> order</td>
  </tr>
  <tr>
    <td style='background-color:{}'></td>
    <td >9<sup>th</sup> order</td>
  </tr>
</table>
        """.format(*colors)
        return string

    def setColorTooltip(self):
        self.line_color_btn.setToolTip(self.make_color_html_string())

    def return_styles(self):
        font = self.font_btn.font()
        text_color = self.text_color_btn.color()
        line_pen = pg.mkPen(color=self.line_color_btn.color(),
                            width=self.line_width_spn.value())
        return font, text_color, line_pen


class XrayCanvas(pg.PlotWidget):

    xAxisUnitsChanged = Signal(str)

    def __init__(self, kv=15, initial_mode='energy', dark_mode=False):
        plot_bkg_color = pg.mkColor(22, 33, 44) \
            if dark_mode else pg.mkColor(250, 250, 255)
        pg.PlotWidget.__init__(
            self,
            viewBox=CustomViewBox(),
            axisItems={'left': CustomAxisItem('left'),
                       'bottom': CustomAxisItem('bottom')},
            background=plot_bkg_color)
        self.dark_mode = dark_mode
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # p1 the main plotItem/canvas
        # p2 secondary viewbox for xray preview lines
        self.p1 = self.plotItem
        self.p2 = pg.ViewBox(enableMouse=True)
        self.p1.scene().addItem(self.p2)
        self.p2.setXLink(self.p1)
        self.bottom_axis = self.p1.axes['bottom']['item']
        self.left_axis = self.p1.axes['left']['item']
        self.updateViews()
        self.x_axis_mode = initial_mode
        self.y_axis_mode = 'cps'  # default
        self._gen_axis_actions()
        self.xtal_family_text_item = pg.TextItem(
            html='XTAL',
            anchor=(1, 1))
        self.xtal_family_text_family = pg.TextItem('family', anchor=(0, 1))
        self.xtal_family_text_family.setParentItem(self.bottom_axis)
        self.xtal_family_text_item.setParentItem(self.bottom_axis)
        self.set_xtal('PET', 8.75, 0.000144, 'PET')  # default to PET crystal
        self.xtal_family_text_item.setVisible(False)
        self.set_kv(kv)
        self.set_connections()
        self.init_x_axis()
        self.siegbahn = True
        self.p1.vb.sigResized.connect(self.updateViews)
        self.prev_text_font = QFont()
        if self.dark_mode:
            prev_marker_col = pg.mkColor((255, 200, 255, 180))
            self.prev_edge_text_color = pg.mkColor((200, 200, 200))
            self.prev_edge_pen = pg.mkPen((200, 200, 200, 200), width=2,
                                          dash=[0.5, 1.5])
        else:
            prev_marker_col = pg.mkColor((35, 10, 20, 180))
            self.prev_edge_text_color = pg.mkColor((50, 50, 50))
            self.prev_edge_pen = pg.mkPen((50, 50, 50, 200), width=2,
                                          dash=[0.5, 1.5])
        self.prev_marker_pen = [pg.mkPen(i, width=2) for i in
                                darken_lighten(prev_marker_col, 14,
                                               dark_mode=self.dark_mode)]
        self.prev_text_color = pg.mkColor((175, 175, 175))

        self.p1.setLimits(yMin=0)
        self.p2.setLimits(yMin=0)
        self.p2.setYRange(0, 1)
        self.orders = set([1])
        self.xray_line_cache = {}
        self.xray_edge_cache = {}
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.xtal_family_text_item.setPos(0, self.bottom_axis.height())

    def _gen_axis_actions(self):
        self.x_axis_ag = QtWidgets.QActionGroup(self)
        self.y_axis_ag = QtWidgets.QActionGroup(self)
        self.x_axis_ag.setExclusive(True)
        self.y_axis_ag.setExclusive(True)
        kev = QAction('keV', parent=self.x_axis_ag)
        kev._title = 'energy (keV)'
        kev._si_units = False
        kev.setCheckable(True)
        sin_thet = QAction('100k sin(θ)', parent=self.x_axis_ag)
        sin_thet._title = 'position (10<sup>5 </sup>sin(θ))'
        sin_thet._si_units = False
        sin_thet.setCheckable(True)
        nm = QAction('nm', parent=self.x_axis_ag)
        nm._title = 'wavelenght (nm)'
        nm._si_units = False
        nm.setCheckable(True)
        self.x_actions = [kev, sin_thet, nm]
        cts = QAction('cts', parent=self.y_axis_ag)
        cts._title = 'raw intensity'
        cts._si_units = True
        cts.setCheckable(True)
        cps = QAction('cps', parent=self.y_axis_ag)
        cps._title = 'time norm. intensity'
        cps._si_units = True
        cps.setCheckable(True)
        cpsna = QAction('cps/nA', parent=self.y_axis_ag)
        cpsna._title = 'exposure norm. intensity'
        cpsna._si_units = True
        cpsna.setCheckable(True)
        self.y_actions = [cts, cps, cpsna]
        self.bottom_axis.init_actions(self.x_actions, self.x_axis_ag)
        self.left_axis.init_actions(self.y_actions, self.y_axis_ag)
        cps.trigger()

    def set_connections(self):
        self.x_axis_ag.triggered.connect(self.set_axis_from_gui)
        self.y_axis_ag.triggered.connect(self.set_axis_from_gui)

    def set_siegbahn_state(self, state):
        self.siegbahn = state

    def set_axis_from_gui(self, action):
        if action in self.x_actions:
            i = self.x_actions.index(action)
            x_mode = ['energy', 'cameca', 'wavelenth'][i]
            self.set_x_mode(x_mode)
            y_mode = self.y_axis_mode
        else:
            x_mode = self.x_axis_mode
            j = self.y_actions.index(action)
            y_mode = ['cts', 'cps', 'cpsna'][j]
            self.y_axis_mode = y_mode
        for item in self.p1.curves:
            if isinstance(item, SpectrumCurveItem):
                item.set_spectrum_data(x_mode=x_mode, y_mode=y_mode)
        self.autoRange()

    def init_x_axis(self):
        if self.x_axis_mode == 'cameca':
            self.x_actions[1].trigger()
        elif self.x_axis_mode == 'wavelenth':
            self.x_actions[2].trigger()
        else:
            self.x_actions[0].trigger()

    def tweek_preview_style(self):
        style_dlg = PenEditor(self.prev_text_font,
                              self.prev_text_color,
                              self.prev_marker_pen[0],
                              dark_mode=self.dark_mode)
        if style_dlg.exec_():
            values = style_dlg.return_styles()
            self.prev_text_font, self.prev_text_color, prev_marker_pen = values
            colors = darken_lighten(prev_marker_pen.color(), 14,
                                    dark_mode=self.dark_mode)
            width = prev_marker_pen.widthF()
            self.prev_marker_pen = [pg.mkPen(color, width=width)
                                    for color in colors]

    def set_xtal(self, family_name, two_D, K, html=None):
        if html is not None:
            self.xtal_family_text_item.setHtml(html)
            self.xtal_family_text_item.setPos(0, self.bottom_axis.height())
            self.xtal_family_text_family.setPos(0, self.bottom_axis.height())
        self.xtal_family_name = family_name
        self.two_D = two_D
        self.K = K
        self.axis_quotient = xu.calc_scale_to_sin_theta(two_D, K)

    def set_x_mode(self, mode):
        self.x_axis_mode = mode
        if mode == 'energy':
            self.p1.setLimits(xMin=-0.5)
            self.setXRange(0.45, self.kv)
            self.set_kv(self.kv)
            self.xtal_family_text_item.setVisible(False)
            self.xtal_family_text_family.setVisible(False)
        elif mode == 'cameca':
            self.p1.setLimits(xMin=10000, xMax=95000)
            self.setXRange(20000, 95000)
            self.wds_orders = [1]
            self.xtal_family_text_item.setVisible(True)
            self.xtal_family_text_family.setVisible(True)
        elif mode == 'wavelenth':
            self.p1.setLimits(xMin=0, xMax=5)
            self.setXRange(0, 100)
            self.xtal_family_text_item.setVisible(False)
            self.xtal_family_text_family.setVisible(False)
        self.xAxisUnitsChanged.emit(mode)

    def set_kv(self, kv):
        self.kv = kv
        if self.x_axis_mode == 'energy':
            self.p1.setLimits(xMax=self.kv)

    def updateViews(self):
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)

    def previewEdges(self, element):
        self.p2.setZValue(9999)
        xec = self.xray_edge_cache
        xam = self.x_axis_mode
        if element not in xec:
            xec[element] = {}
        if xam == 'cameca':
            xfn = self.xtal_family_name 
        elem_dict = xec[element]
        if xam in elem_dict:
            if xam == 'energy':
                for item in elem_dict[xam]:
                    self.p2.addItem(item)
                return
            elif xam == 'cameca':
                if xfn in elem_dict[xam]:
                    for item in elem_dict[xam][xfn]:
                        self.p2.addItem(item)
                    return
        if xam == 'energy':
            lines = xu.xray_shells_for_plot(element)
        elif xam == 'cameca':
            lines = xu.xray_shells_for_plot_wds(element,
                                                two_D=self.two_D,
                                                K=self.K)
        if xam == 'energy':
            elem_dict[xam] = []
        elif xam == 'cameca':
            if xam not in elem_dict:
                elem_dict[xam] = {}
            elem_dict[xam][xfn] = []
        for i in lines:
            line = pg.PlotCurveItem([i[1], i[1]], [0.06, 1.2],
                                    pen=self.prev_edge_pen)
            self.p2.addItem(line)
            text = pg.TextItem(text="{0} {1}".format(element, i[0]),
                               anchor=(0., 1.),
                               angle=90)
            text.setFont(self.prev_text_font)
            self.p2.addItem(text)
            text.setPos(i[1], 1.)
            if xam == 'energy':
                final_list = elem_dict[xam]
            elif xam == 'cameca':
                final_list = elem_dict[xam][xfn]
            else:
                return
            final_list.append(line)
            final_list.append(text)

    def previewLines(self, element, kv=None, lines=None, siegbahn=None):
        if kv is None:
            kv = self.kv
        if siegbahn is None:
            siegbahn = self.siegbahn
        # self.p2.clear()
        self.p2.setZValue(9999)
        css_color = color_to_css(self.prev_text_color)
        if lines is None:
            if self.x_axis_mode == 'energy':
                lines = {1: xu.xray_lines_for_plot(element, kv, siegbahn)}
            elif self.x_axis_mode == 'cameca':
                min_x, max_x = self.getAxis('bottom').range
                lines = {i: xu.xray_lines_for_plot_wds(element,
                                                       two_D=self.two_D,
                                                       K=self.K,
                                                       xmax=max_x,
                                                       xmin=min_x,
                                                       hv=kv,
                                                       siegbahn=siegbahn,
                                                       order=i)
                         for i in self.orders}
        else:
            # TODO
            pass
        for j in lines:
            for i in lines[j]:
                line = pg.PlotCurveItem([i[1], i[1]],
                                        [0, i[2]],
                                        pen=self.prev_marker_pen[j-1])
                self.p2.addItem(line)
                text = pg.TextItem(html="""<body style="color:{0};">
{1} {2}</body>""".format(css_color, element, format_line(i[0], j)),
                                   anchor=(0., 1.))
                text.setFont(self.prev_text_font)
                self.p2.addItem(text)
                text.setPos(i[1], i[2])

    def previewOneLine(self, element, line):
        x_pos = xu.xray_energy(element, line)
        if self.x_axis_mode == 'wds':
            x_pos = self.axis_quotient / x_pos
        gr_line = pg.PlotCurveItem([x_pos,  x_pos],
                                   [0,  xu.xray_weight(element, line)],
                                   pen=self.prev_marker_pen)
        self.p2.addItem(gr_line)

    def clearPreview(self):
        self.p2.clear()
        self.p2.setZValue(-9999)

    def addLines(self, element, kv=None):
        pass

    def auto_custom(self):
        pass


class PositionMarker(InfiniteLine):
    def __init__(self, canvas=None, line_type='peak', **kwargs):
        """line_type one of peak, background"""
        InfiniteLine.__init__(self, )


class PositionMarkers:
    def __init__(self, canvas=None,
                 initial_values=None):
        """
        atrributes:
        canvas - the pyqtgraph scene where the markers will be placed on
        initial_values - the tuple with initial values for generation of
        marker set (name, peak_position, left_relative_position,
        right_relative_position, slope_val, background_modeling_mode)
        """
        if initial_values is not None:
            self.type = 'particular'
            self.initial_values = initial_values
            self.name = self.initial_values[0]
        else:
            self.type = 'generic'
            self.name = ''
            # modes: 'two_bkgd', 'single_bkgd', 'solo'
            self.mode = 'two_bkgd'
        self.canvas = None
        self.m_line = None
        self.bg1_line = None
        self.bg2_line = None
        self.bg1_text = None
        self.bg2_text = None
        self.m_text_pos = 0.80
        self.bg1_text_pos = 0.75
        self.bg2_text_pos = 0.75
        if canvas is not None:
            self.canvas = canvas
            self.initiate_lines()
            self.x_axis_mode = self.canvas.x_axis_mode

    def set_mode(self, mode):
        if mode not in ('two_bkgd', 'single_bkgd', 'solo'):
            raise KeyError("Position marker can be set only to one of:"
                           "['two_bkgd', 'single_bkgd', 'solo']")
        if mode == self.mode:
            return
        else:
            self.mode = mode

    def gen_positions(self):
        if self.type == 'generic':
            axis_range = self.canvas.getAxis('bottom').range
            width = axis_range[1] - axis_range[0]
            if self.mode in ('two_bkgd', 'single_bkgd'):
                lower = axis_range[0] + width * 0.25
            else:
                lower = None
            middle = axis_range[0] + width * 0.5
            if self.mode == 'two_bkgd':
                higher = axis_range[0] + width * 0.75
            else:
                higher = None
        elif self.type == 'particular':
            middle, lower, higher = self.initial_values[1:4]
            if lower is not None:
                lower = middle + lower
            if higher is not None:
                higher = middle + higher
        return lower, middle, higher

    def initiate_lines(self):
        if self.canvas.dark_mode:
            color = 'w'
        else:
            color = 'k'
        lower, middle, higher = self.gen_positions()
        self.m_line = InfiniteLine(middle, movable=True,
                                   pen=pg.mkPen(color, width=3.),
                                   name='main',
                                   markers=[('^', 0.99, 6.0)])
        if lower is not None:
            self.bg1_line = InfiniteLine(lower, movable=True,
                                         pen=pg.mkPen(color, width=1.5),
                                         name='bkgd1',
                                         markers=[('v', 0.01, 6.0)])
            self.bg1_text = pg.InfLineLabel(self.bg1_line, movable=True,
                                            color=color,
                                            position=self.bg1_text_pos)
            self.bg1_line.sigPositionChanged.connect(self.update_marker_str)

        if higher is not None:
            self.bg2_line = InfiniteLine(higher, movable=True,
                                         pen=pg.mkPen(color, width=1.5),
                                         name='bkgd2',
                                         markers=[('v', 0.01, 6.0)])
            self.bg2_text = pg.InfLineLabel(self.bg2_line, movable=True,
                                            color=color,
                                            position=self.bg2_text_pos)
            self.bg2_line.sigPositionChanged.connect(self.update_marker_str)
        self.m_text = pg.InfLineLabel(self.m_line, movable=True, color=color,
                                      position=self.m_text_pos)
        self.update_marker_str()
        self.m_line.sigPositionChanged.connect(self.update_marker_str)
        self.add_to_canvas()

    def initiate_positions(self):
        lower, middle, higher = self.gen_positions()
        if self.bg1_line is not None:
            if lower is not None:
                self.bg1_line.setValue(lower)
            else:
                self.canvas.removeItem(self.bg1_line)
                self.bg1_line = None
        if self.bg2_line is not None:
            if higher is not None:
                self.bg2_line.setValue(higher)
            else:
                self.canvas.removeItem(self.bg2_line)
                self.bg2_line = None
        self.m_line.setValue(middle)

    def update_marker_str(self):
        pos_format = self.gen_precission_formater()
        if self.bg1_text is not None:
            self.bg1_text.setText(pos_format.format(
                self.bg1_line.value() - self.m_line.value()))
        if self.bg2_text is not None:
            self.bg2_text.setText(pos_format.format(
                self.bg2_line.value() - self.m_line.value()))
        self.m_text.setText(pos_format.format(self.m_line.value()))

    def gen_precission_formater(self):
        a, b = self.canvas.getAxis('bottom').range
        rng = b - a
        if log10(rng) >= 3:
            rng = 3
        else:
            rng = log10(rng)
        precission = str(3 - int(rng))
        str_list = ['{:.', precission, 'f}']
        if self.type == 'particular':
            str_list.extend(['\n', self.name])
        return ''.join(str_list)

    def add_to_canvas(self):
        self.canvas.addItem(self.m_line)
        if self.bg1_line is not None:
            self.canvas.addItem(self.bg1_line)
        if self.bg2_line is not None:
            self.canvas.addItem(self.bg2_line)

    def remove_from_canvas(self):
        if self.m_line is not None:
            self.m_text_pos = self.m_text.orthoPos
            self.canvas.removeItem(self.m_line)
            self.m_line.sigPositionChanged.disconnect(self.update_marker_str)
            self.m_line = None
            self.m_text = None
        if self.bg1_line is not None:
            self.bg1_text_pos = self.bg1_text.orthoPos
            self.canvas.removeItem(self.bg1_line)
            self.bg1_line.sigPositionChanged.disconnect(self.update_marker_str)
            self.bg1_line = None
            self.bg1_text = None
        if self.bg2_line is not None:
            self.bg2_text_pos = self.bg2_text.orthoPos
            self.canvas.removeItem(self.bg2_line)
            self.bg2_line.sigPositionChanged.disconnect(self.update_marker_str)
            self.bg2_line = None
            self.bg2_text = None

    def register_canvas(self, canvas):
        self.canvas = canvas
        # if self.m_line is None:
        self.remove_from_canvas()
        self.initiate_lines()
        # else:
        #    self.initiate_positions()
        #    self.add_to_canvas()


class LinearBackground(InfiniteLine):
    def __init__(self, plotting_widget, spect_xtal):
        self.pw = plotting_widget
        pos_markers = self.pw.pos_markers
        m_pos = pos_markers.m_line.getXPos()
        self.pm = pos_markers
        self.signal_header = spect_xtal
        if self.pw.canvas.dark_mode:
            color = 'y'
        else:
            color = 'r'
        super().__init__(pos=(m_pos, 300), angle=0, pen=mkPen(width=2,
                                                              color=color))
        self.setZValue(3001)  # over 3000
        self.pm.bg1_line.sigPositionChanged.connect(self.update_background)
        self.pm.bg2_line.sigPositionChanged.connect(self.update_background)
        self.sm = self.pw.wds_tree_selection_model
        self.sm.currentChanged.connect(self.update_background)
        self.update_background()

    def update_background(self):
        def filter_curve(curve):
            if (curve.signal_header == self.signal_header) and\
                    (curve in self.pw.canvas.p1.curves):
                return True
            return False

        bg1_pos = self.pm.bg1_line.getXPos()
        bg2_pos = self.pm.bg2_line.getXPos()
        lenght = bg1_pos - bg2_pos
        plot_curves = self.pw.wds_tree_model.data(self.sm.currentIndex(),
                                                  Qt.UserRole)
        if plot_curves is None:
            return
        filtered = list(filter(filter_curve, plot_curves))
        if len(filtered) == 1:
            curve = filtered[0]
        else:
            return
        data = curve.getData()
        idx1 = np.abs(data[0] - bg1_pos).argmin()
        idx2 = np.abs(data[0] - bg2_pos).argmin()
        x_pos1 = data[0][idx1]
        y_pos1 = data[1][idx1]
        y_pos2 = data[1][idx2]
        h = y_pos1 - y_pos2
        new_angle = degrees(atan(h/lenght))
        self.setAngle(new_angle)
        self.setPos((x_pos1, y_pos1))

    def prepare_to_destroy(self):
        self.pm.bg1_line.sigPositionChanged.disconnect(self.update_background)
        self.pm.bg2_line.sigPositionChanged.disconnect(self.update_background)
        self.sm.currentChanged.disconnect(self.update_background)


class ExponentialBackground(pg.PlotCurveItem):
    def __init__(self, plotting_widget, spect_xtal):
        self.pw = plotting_widget
        if self.pw.canvas.dark_mode:
            color = 'y'
        else:
            color = 'r'
        super().__init__(pen=mkPen(width=2, color=color))
        self.setZValue(3001)  # over 3000
        pos_markers = self.pw.pos_markers
        self.pm = pos_markers
        self.signal_header = spect_xtal
        self.pm.bg1_line.sigPositionChanged.connect(self.update_background)
        self.pm.bg2_line.sigPositionChanged.connect(self.update_background)
        self.pm.m_line.sigPositionChanged.connect(self.update_background)
        self.sm = self.pw.wds_tree_selection_model
        self.sm.currentChanged.connect(self.update_background)
        self.update_background()

    def update_background(self):
        def filter_curve(curve):
            if (curve.signal_header == self.signal_header) and\
                    (curve in self.pw.canvas.p1.curves):
                return True
            return False

        bg1_pos = self.pm.bg1_line.getXPos()
        bg2_pos = self.pm.bg2_line.getXPos()
        m_pos = self.pm.m_line.getXPos()
        min_pos = min(bg1_pos, bg2_pos, m_pos)
        max_pos = max(bg1_pos, bg2_pos, m_pos)
        width = max_pos - min_pos
        plot_curves = self.pw.wds_tree_model.data(self.sm.currentIndex(),
                                                  Qt.UserRole)
        if plot_curves is None:
            return
        filtered = list(filter(filter_curve, plot_curves))
        if len(filtered) == 1:
            curve = filtered[0]
        else:
            return
        data = curve.getData()
        idx1 = np.abs(data[0] - bg1_pos).argmin()
        idx2 = np.abs(data[0] - bg2_pos).argmin()
        x_pos1 = data[0][idx1]
        y_pos1 = data[1][idx1]
        x_pos2 = data[0][idx2]
        y_pos2 = data[1][idx2]
        f = log(y_pos1 / y_pos2) / log(x_pos2 / x_pos1)
        x_linespace = np.linspace(min_pos - 0.2 * width,
                                  max_pos + 0.2 * width,
                                  num=512)
        y = y_pos2 * (x_pos2 / x_linespace) ** f
        self.setData(x_linespace, y)

    def prepare_to_destroy(self):
        self.pm.bg1_line.sigPositionChanged.disconnect(self.update_background)
        self.pm.bg2_line.sigPositionChanged.disconnect(self.update_background)
        self.pm.m_line.sigPositionChanged.disconnect(self.update_background)
        self.sm.currentChanged.disconnect(self.update_background)


class SloppedBackground(InfiniteLine):
    def __init__(self, plotting_widget, spect_xtal):
        self.pw = plotting_widget
        pos_markers = self.pw.pos_markers
        m_pos = pos_markers.m_line.getXPos()
        self.pm = pos_markers
        self.signal_header = spect_xtal
        if self.pw.canvas.dark_mode:
            color = 'y'
        else:
            color = 'r'
        super().__init__(pos=(m_pos, 300), angle=0, pen=mkPen(width=2,
                                                              color=color))
        self.setZValue(3001)  # over 3000
        self.pm.bg1_line.sigPositionChanged.connect(self.update_background)
        self.pm.m_line.sigPositionChanged.connect(self.update_background)
        self.sm = self.pw.wds_tree_selection_model
        self.sm.currentChanged.connect(self.update_background)
        self.pw.slope_spin_box.sigValueChanging.connect(
            self.slope_from_spin_box)
        self.slope_from_spin_box(self.pw.slope_spin_box)

    def slope_from_spin_box(self, spin_box):
        self.slope = spin_box.value()
        self.update_background(slope=self.slope)

    def update_background(self, *args, slope=None):
        def filter_curve(curve):
            if (curve.signal_header == self.signal_header) and\
                    (curve in self.pw.canvas.p1.curves):
                return True
            return False

        if slope is None:
            slope = self.slope
        elif slope > 0.:
            self.slope = slope
        else:
            return
        m_pos = self.pm.m_line.getXPos()
        bg1_pos = self.pm.bg1_line.getXPos()
        lenght = bg1_pos - m_pos
        plot_curves = self.pw.wds_tree_model.data(self.sm.currentIndex(),
                                                  Qt.UserRole)
        if plot_curves is None:
            return
        filtered = list(filter(filter_curve, plot_curves))
        if len(filtered) == 1:
            curve = filtered[0]
        else:
            return
        data = curve.getData()
        idx = np.abs(data[0] - bg1_pos).argmin()
        x_pos = data[0][idx]
        y_pos = data[1][idx]
        y_pos_main = y_pos * slope
        h = y_pos - y_pos_main
        new_angle = degrees(atan(h/lenght))
        self.setAngle(new_angle)
        self.setPos((x_pos, y_pos))

    def prepare_to_destroy(self):
        self.pm.bg1_line.sigPositionChanged.disconnect(self.update_background)
        self.pm.m_line.sigPositionChanged.disconnect(self.update_background)
        self.sm.currentChanged.disconnect(self.update_background)
        self.pw.slope_spin_box.sigValueChanging.disconnect(
            self.slope_from_spin_box)


class XraySpectraGUI(cw.FullscreenableWidget):
    sig_name_had_changed = Signal(str)

    def __init__(self, parent=None, icon_size=None,
                 pet_opacity=None, initial_mode='energy',
                 name='Plot Widget'):
        cw.FullscreenableWidget.__init__(self, parent, icon_size)
        self._name = name
        self.resize(550, 550)
        self._pet_opacity = pet_opacity
        self.pet = None
        self.splitter = QtWidgets.QSplitter(Qt.Vertical)
        self.setCentralWidget(self.splitter)
        self.bkgd_helper_widget = QWidget(self.splitter)
        self._setup_toolbar()
        self.canvas = XrayCanvas(initial_mode=initial_mode,
                                 dark_mode=self.dark_mode)
        self.canvas.setWhatsThis(
            """<h4>Plotting Canvas</h4>
            <p>plotting canvas can show spectra for checked datasets
            in WDS tree view, and checked xtal-spectrometer combinations
            enabled/checked in below attached widget.</p>
            <p>right clicking on y or x axis alows to change units;
            in case of changing x units to wavelenth or energy - that
            unlocks possibility to check xtal-spec combinations from
            different xtal families allowing to plot and compare overlapping
            spectral regions</p>""")
        size_policy_canvas = QSizePolicy()
        size_policy_canvas.setVerticalStretch(200)
        size_policy_canvas.setVerticalPolicy(QSizePolicy.Expanding)
        size_policy_canvas.setHorizontalPolicy(QSizePolicy.Expanding)
        self.canvas.setSizePolicy(size_policy_canvas)
        self._setup_connections()
        self.splitter.addWidget(self.canvas)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self.sig_name_had_changed.emit(new_name)

    def _setup_connections(self):
        self.auto_all.triggered.connect(self.canvas.p1.autoRange)
        self.auto_height.triggered.connect(self.auto_y)
        self.auto_width.triggered.connect(self.auto_x)

    def auto_y(self):
        self.canvas.p1.getViewBox().setAutoVisible(y=True)
        self.canvas.p1.getViewBox().enableAutoRange(pg.ViewBox.YAxis)

    def auto_x(self):
        self.canvas.p1.getViewBox().setAutoVisible(x=True)
        self.canvas.p1.getViewBox().enableAutoRange(pg.ViewBox.XAxis)

    def broker_orders_state_to_canvas(self):
        self.canvas.orders = self.pet.orders

    @Slot(bool)
    def preview_toggle(self, state):
        if state:
            self.pet.elementConsidered.connect(self.canvas.previewLines)
        else:
            self.pet.elementConsidered.disconnect(self.canvas.previewLines)

    @Slot(bool)
    def preview_edges_toggle(self, state):
        if state:
            self.pet.elementConsidered.connect(self.canvas.previewEdges)
        else:
            self.pet.elementConsidered.disconnect(self.canvas.previewEdges)

    def _setup_toolbar(self):
        # add spacer:
        self._empty2 = QtWidgets.QWidget()
        self._empty2.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty2)
        self.element_table_button = cw.CustomToolButton(self)
        self.toolbar.addWidget(self.element_table_button)
        self._setup_table_button()
        self.toolbar.addSeparator()
        self.auto_button = cw.CustomToolButton(self)
        self.auto_button.setWhatsThis(
            "This automatically adjust x and/or y axis range")
        self._setup_auto()
        self.toolbar.addWidget(self.auto_button)
        self._empty1 = QtWidgets.QWidget()
        self._empty1.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty1)

    def _setup_auto(self):
        menu = QMenu('auto range')
        self.auto_all = QAction(
            QIcon(self.icon_provider.get_icon_path('auto_all.svg')),
            'all',
            self.auto_button)
        self.auto_width = QAction(
            QIcon(self.icon_provider.get_icon_path('auto_width.svg')),
            'width',
            self.auto_button)
        self.auto_height = QAction(
            QIcon(self.icon_provider.get_icon_path('auto_height.svg')),
            'height',
            self.auto_button)
        self.auto_custom = QAction(
            QIcon(self.icon_provider.get_icon_path('auto_custom.svg')),
            'custom',
            self.auto_button)
        self.custom_conf = QAction('custom config.', self.auto_button)
        action_list = [self.auto_all, self.auto_width, self.auto_height,
                       self.auto_custom, self.custom_conf]
        for i in action_list[:-1]:
            i.triggered.connect(self.auto_button.set_action_to_default)
        menu.addActions(action_list)
        self.auto_button.setMenu(menu)
        self.auto_button.setDefaultAction(self.auto_all)

    def _setup_table_button(self):
        menu = QMenu('Element Table')
        self.action_element_table = QAction(self)
        self.action_element_table.setIcon(
            QIcon(self.icon_provider.get_icon_path('pt.svg')))
        self.action_element_table.setToolTip("show/hide element table")
        self.action_element_table.setWhatsThis("show/hide element table")
        self.action_element_table.triggered.connect(self.show_pet)
        self.config_preview = QAction(
            QIcon(self.icon_provider.get_icon_path(
                'line_preview_settings.svg')),
            'preview style',
            self.element_table_button)
        self.config_burned = QAction(
            QIcon(self.icon_provider.get_icon_path('line_burn_settings.svg')),
            'burned style',
            self.element_table_button)
        menu.addActions([self.config_preview,
                         self.config_burned])
        self.element_table_button.setMenu(menu)
        self.element_table_button.setDefaultAction(self.action_element_table)

    def _setup_pet(self):
        #self.dock_pet_win = QtWidgets.QWidget(self)
        #self.dock_pet_win.setSizePolicy(QSizePolicy.Minimum,
        #                                QSizePolicy.Minimum)
        self.dock_line_win = QtWidgets.QDockWidget('Line selection', self)
        #self.pet = XRayElementTable(parent=self.dock_pet_win)
        self.pet_win = FramelessXRayElementTable(parent=self)
        self.pet = self.pet_win.pet
        self.lineSelector = LineEnabler(self.dock_line_win)
        #self.dock_pet_win.setWidget(self.pet)
        #self.addDockWidget(Qt.RightDockWidgetArea,
        #                   self.dock_pet_win)
        #self.dock_pet_win.setAllowedAreas(Qt.NoDockWidgetArea)
        #self.dock_pet_win.setFloating(True)
        self.dock_line_win.setWidget(self.lineSelector)
        self.addDockWidget(Qt.RightDockWidgetArea,
                           self.dock_line_win)
        self.dock_line_win.setAllowedAreas(Qt.NoDockWidgetArea)
        self.dock_line_win.setFloating(True)
        if self._pet_opacity:
            self.pet_win.setWindowOpacity(self._pet_opacity)
        self.pet_win.resize(self.pet_win.minimumSizeHint())
        self.dock_line_win.hide()
        self.pet_win.hide()
        self.pet.elementConsidered.connect(self.canvas.previewEdges)
        self.pet.elementConsidered.connect(self.canvas.previewLines)
        self.pet.elementUnconsidered.connect(self.canvas.clearPreview)
        self.config_preview.triggered.connect(
            self.canvas.tweek_preview_style)
        self.pet.hv_value.valueChanged.connect(self.canvas.set_kv)
        self.pet.elementRightClicked.connect(
            self.lineSelector.set_element_lines)
        self.lineSelector.lineView.entered.connect(
            self.preview_hovered_lines)
        self.lineSelector.lineView.mouseLeft.connect(
            self.canvas.clearPreview)
        self.pet.siegbahn.toggled.connect(self.canvas.set_siegbahn_state)
        self.pet.ordersChanged.connect(self.broker_orders_state_to_canvas)
        self.pet.preview.toggled.connect(self.preview_toggle)
        self.pet.preview_edge.toggled.connect(self.preview_edges_toggle)

    def show_pet(self):
        if self.pet is None:
            self._setup_pet()
            self.pet_win.move(self.mapToGlobal(self.pos() + QPoint(5, 5)))
        if self.pet_win.isVisible():
            self.pet_win.hide()
        else:
            self.pet_win.show()

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
            self.canvas.previewLines(element,
                                     siegbahn=self.pet.siegbahn_enabled)


class WDSSpectraGUI(XraySpectraGUI):
    def __init__(self, wds_tree_model, wds_tree_selection_model):
        XraySpectraGUI.__init__(self, pet_opacity=0.9,
                                initial_mode='cameca')
        self.pos_markers = PositionMarkers()
        self.backgrounds = []
        self._setup_wds_additions()
        self._setup_markers()
        self._setup_marker_remove()
        self.spect_xtal_combo_view = XtalListView(parent=self.splitter)
        size_policy = QSizePolicy()
        size_policy.setVerticalStretch(1)
        size_policy.setVerticalPolicy(QSizePolicy.Minimum)
        size_policy.setHorizontalPolicy(QSizePolicy.Minimum)
        self.spect_xtal_combo_view.setSizePolicy(size_policy)
        self.splitter.addWidget(self.bkgd_helper_widget)
        bkgd_layout = QHBoxLayout(self.bkgd_helper_widget)
        bkgd_layout.addWidget(QLabel("Background slope"))
        bkgd_layout.setContentsMargins(2, 2, 2, 2)
        self.slope_spin_box = pg.SpinBox(
            value=1.0, dec=True, min=0.001, max=1000, decimals=6)
        self.slope_spin_box.setMinimumHeight(24)
        bkgd_layout.addWidget(self.slope_spin_box)
        self.bkgd_helper_widget.setSizePolicy(size_policy)
        self.bkgd_helper_widget.hide()
        self.splitter.addWidget(self.spect_xtal_combo_view)
        self.actionWDSSelector.toggled.connect(
            self.spect_xtal_combo_view.setVisible)
        self.actionWDSSelector.setChecked(True)
        self.xtal_model = SpecXTALCombiModel(wds_tree_model)
        self.spect_xtal_combo_view.setModel(self.xtal_model)
        self.wds_tree_model = wds_tree_model
        self.wds_tree_selection_model = wds_tree_selection_model
        self.add_spectrum_curves(alpha=self.wds_tree_model.global_alpha)
        self.wds_tree_model.wds_files_appended.connect(
            self.add_spectrum_curves)
        self.xtal_model.xtalFamilyChanged.connect(self.canvas.set_xtal)
        self.canvas.xAxisUnitsChanged.connect(self.change_xtal_exclusivness)
        self.xtal_model.combinationCheckedStateChanged.connect(
            self.change_curves)
        self.xtal_model.dataChanged.connect(self.change_style_of_spect)
        self.xtal_model.combinationCheckedStateChanged.connect(
            self.set_background_model)

    def _setup_wds_additions(self):
        self.marker_button = cw.CustomToolButton(self)
        self.marker_button.setWhatsThis(
            """This adds movable line marker with single, double or any
            background line markers; Drop down menu of this widget allows to
            set some available background modeling for selected markers"""
        )
        self.toolbar.addWidget(self.marker_button)
        self._setup_markers()
        self.actionWDSSelector = QAction(self)
        self.actionWDSSelector.setIcon(QIcon(
            self.icon_provider.get_icon_path('wds_selection.svg')))
        self.actionWDSSelector.setCheckable(True)
        self.actionWDSSelector.setToolTip(
            'hide/show WDS-XTAL-spectrometer combination categories')
        self.toolbar.addAction(self.actionWDSSelector)

    def _setup_marker_remove(self):
        menu = self.canvas.p1.getViewBox().menu
        self.actionClearMarker = menu.addAction('Remove markers')
        self.actionClearMarker.setIcon(
            QIcon(self.icon_provider.get_icon_path('lines_hide.svg')))
        self.actionClearMarker.triggered.connect(
            self.clear_background_models)
        self.actionClearMarker.triggered.connect(
            self.pos_markers.remove_from_canvas)

    def set_background_model(self):
        self.clear_background_models()
        xtal_spect_combi = self.xtal_model.get_checked_combinations()
        if len(xtal_spect_combi) == 0:
            return
        if self.action_linear_background.isChecked():
            if self.pos_markers.mode == 'two_bkgd':
                for combi in xtal_spect_combi:
                    bkg = LinearBackground(self, combi)
                    self.backgrounds.append(bkg)
                    self.canvas.addItem(bkg)
            if self.pos_markers.mode == 'single_bkgd':
                for combi in xtal_spect_combi:
                    bkg = SloppedBackground(self, combi)
                    self.backgrounds.append(bkg)
                    self.canvas.addItem(bkg)
        if self.action_exp_background.isChecked():
            for combi in xtal_spect_combi:
                bkg = ExponentialBackground(self, combi)
                self.backgrounds.append(bkg)
                self.canvas.addItem(bkg)

    def clear_background_models(self):
        if len(self.backgrounds) > 0:
            for bkgd in self.backgrounds:
                bkgd.prepare_to_destroy()
                self.canvas.p1.removeItem(bkgd)
            self.backgrounds.clear()  # just to be sure none left

    def show_three_markers_on_canvas(self):
        self.clear_background_models()
        self.pos_markers.set_mode('two_bkgd')
        self.pos_markers.register_canvas(self.canvas)
        self.action_exp_background.setEnabled(True)
        self.action_linear_background.setEnabled(True)
        self.set_background_model()

    def show_two_markers_on_canvas(self):
        self.clear_background_models()
        self.pos_markers.set_mode('single_bkgd')
        self.pos_markers.register_canvas(self.canvas)
        self.action_linear_background.setEnabled(True)
        self.action_exp_background.setEnabled(False)
        self.action_exp_background.setChecked(False)
        self.set_background_model()

    def show_single_marker_on_canvas(self):
        self.clear_background_models()
        self.pos_markers.set_mode('solo')
        self.action_linear_background.setChecked(False)
        self.action_exp_background.setChecked(False)
        self.pos_markers.register_canvas(self.canvas)
        self.action_linear_background.setEnabled(False)
        self.action_exp_background.setEnabled(False)

    def _setup_markers(self):
        menu = QMenu('markers and backgrounds')
        self.action_marker_bgx2 = QAction(
            QIcon(self.icon_provider.get_icon_path('lines_bgx2.svg')),
            'peak and 2 background',
            self.marker_button)
        self.action_marker_bgx2.triggered.connect(self.bkgd_helper_widget.hide)
        self.action_marker_and_1bkg = QAction(
            QIcon(self.icon_provider.get_icon_path('lines_pk_1xbkg.svg')),
            'peak and single background',
            self.marker_button)
        self.action_marker_and_1bkg.triggered.connect(
            self.bkgd_helper_widget.show)
        self.action_marker_only = QAction(
            QIcon(self.icon_provider.get_icon_path('lines_1x_only.svg')),
            'single marker only',
            self.marker_button)
        self.action_marker_only.triggered.connect(self.bkgd_helper_widget.hide)
        self.action_linear_background = QAction('linear background')
        self.action_linear_background.toggled.connect(
            self.set_background_model)
        self.action_linear_background.setCheckable(True)
        self.action_exp_background = QAction('exponential background')
        self.action_exp_background.setCheckable(True)
        self.action_exp_background.toggled.connect(
            self.set_background_model)
        for action in [self.action_marker_bgx2, self.action_marker_and_1bkg,
                       self.action_marker_only]:
            action.triggered.connect(self.marker_button.set_action_to_default)
        menu.addAction(self.action_marker_bgx2)
        menu.addAction(self.action_marker_and_1bkg)
        menu.addAction(self.action_marker_only)
        menu.addSection("Background models:")
        menu.addAction(self.action_linear_background)
        menu.addAction(self.action_exp_background)
        self.marker_button.setMenu(menu)
        self.marker_button.setDefaultAction(self.action_marker_bgx2)
        self.action_marker_bgx2.triggered.connect(
            self.show_three_markers_on_canvas)
        self.action_marker_and_1bkg.triggered.connect(
            self.show_two_markers_on_canvas)
        self.action_marker_only.triggered.connect(
            self.show_single_marker_on_canvas)

    def change_curves(self, xtal, state):
        if state:
            self.add_spectrum_curves(spect_headers=[xtal],
                                     alpha=self.wds_tree_model.global_alpha)
            self.canvas.autoRange()
        else:
            self.remove_spectrum_curves(xtal)

    def change_style_of_spect(self, index_u, index_d, roles=[]):
        if len(roles) != 1:
            return
        role = roles[0]
        if role in [self.xtal_model.LineWidthRole,
                    self.xtal_model.LineStyleRole]:
            xm = self.xtal_model
            spect_header = xm.data(index_u, xm.SpectXtalCombinationRole)
            curves = [i for i in self.canvas.p1.curves
                      if i.signal_header == spect_header]
            for curve in curves:
                if role == self.xtal_model.LineWidthRole:
                    curve.set_curve_width(spect_header.q_pen_width)
                else:
                    curve.set_curve_style(spect_header.q_pen_style)

    def add_spectrum_curves(self, wds_files=None,
                            spect_headers=None, alpha=200):
        if spect_headers is None:
            spect_headers = [i for i in
                             self.xtal_model.combinations
                             if i.q_checked_state]
        if wds_files is None:
            wds_files = self.wds_tree_model.collection
        for wds_file in wds_files:
            for dataset in wds_file.content.datasets:
                for item in dataset.items:
                    if item.signal_header in spect_headers:
                        # spect_header is copy with custom attributes
                        # for pen style and width
                        # where .signal_header has not those
                        i = spect_headers.index(item.signal_header)
                        WDSPlotItem(item, self.canvas,
                                    pen_style=spect_headers[i].q_pen_style,
                                    pen_width=spect_headers[i].q_pen_width,
                                    alpha=alpha)
        # highlight spectra if it is selected in tree view:
        self.wds_tree_model.highlight_spectra(
            self.wds_tree_selection_model.selection())

    def remove_spectrum_curves(self, spect_header):
        # we cant iterate over canvas.p1.items, while removing,
        # we need a copy of list to iterate through
        curves_list = [i for i in self.canvas.p1.curves
                       if i.signal_header == spect_header]
        for curve in curves_list:
            curve.remove_from_model()
            self.canvas.p1.removeItem(curve)

    def change_xtal_exclusivness(self, mode):
        if mode == 'cameca':
            self.xtal_model.setIgnoreFamilyConstrain(False)
        else:
            self.xtal_model.setIgnoreFamilyConstrain(True)

    def prepare_to_destroy(self):
        for curve in self.canvas.p1.curves:
            if isinstance(curve, WDSPlotItem):
                curve.remove_from_model()
        self.canvas.p1.clear()
        if hasattr(self, 'pet_win'):
            self.pet_win.close()


