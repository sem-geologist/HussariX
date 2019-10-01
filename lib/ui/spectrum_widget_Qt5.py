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

from PyQt5 import QtCore, Qt, QtGui, QtWidgets
import pyqtgraph as pg

from ..misc import xray_util as xu
from .node import ElementLineTreeModel, SimpleDictNode

from . import element_table_Qt5
from . import CustomWidgets as cw
from .CustomPGWidgets import CustomViewBox, CustomAxisItem
from os import path
import json
from re import sub, findall
from math import log10

main_path = path.join(path.dirname(__file__), path.pardir)
icon_path = path.join(main_path, 'icons')
conf_path = path.join(main_path,
                      'configurations',
                      'lines.json')

with open(conf_path) as fn:
    jsn = fn.read()
lines = json.loads(jsn)

BACKGROUND_COLOR = pg.mkColor(0, 43, 54)


# dealling with greek letters, where windows dos retards made it
# into  latin:
dos_greek = {'a': 'α', 'b': 'β', 'c': 'γ'}


def colorCSS(qcolor):
    """convert color to css string 'rgba(tuple)' format
       while preserving the alpha value"""
    css_color = 'rgba({0}, {1}, {2}, {3})'.format(
                *pg.colorTuple(qcolor))
    return css_color


def darken(color, times, color_list=None):
    """return the list of recursively darkened QtColors"""
    if color_list is None:
        color_list = [color]
    if times > 0:
        color = color.darker(175)
        color_list.append(color)
        darken(color, times - 1, color_list=color_list)
    return color_list


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


class XRayElementTable(element_table_Qt5.ElementTableGUI):
    ordersChanged = QtCore.pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.preview = Qt.QCheckBox('emission')
        self.preview.setToolTip('preview emission lines')
        self.preview.setMinimumSize(16, 16)
        self.preview_edge = Qt.QCheckBox('absorption')
        self.preview_edge.setToolTip('preview absorption edges')
        self.preview_edge.setMinimumSize(16, 16)
        self.siegbahn = Qt.QCheckBox('Siegbahn')
        self.siegbahn.setToolTip("""checked - Siegbahn notation (limited lines)
unchecked - IUPAC notatation (all known lines)""")
        self.siegbahn.setMinimumSize(16, 16)
        self.hv_value = Qt.QDoubleSpinBox()
        self.hv_value.setMinimumSize(16, 16)
        self.hv_value.setSuffix(" kV")
        self.hv_value.setToolTip("""HV value which restricts x axis (max) and
approximates the heights of preview lines as
a function of effectivness (2.7 rule)""")
        self.hv_value.setRange(0.1, 1e4)
        # add those parameters to the groupbox:
        self.preview_group = Qt.QGroupBox('on hover:')
        self.preview_group.setLayout(Qt.QGridLayout())
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
        self.preview.setCheckState(QtCore.Qt.Checked)
        self.siegbahn.setCheckState(QtCore.Qt.Checked)
        self.hv_value.setValue(15.)
        self.preview_edge.setCheckState(QtCore.Qt.Checked)
        self.orders_interface = Qt.QLineEdit()
        self.orders_interface.setMinimumSize(16, 16)
        self.layout().addWidget(self.orders_interface, 0, 12, 1, 5)
        self.orders_interface.setToolTip(
            "orders of diffracted lines\n"
            "to be previewed")
        self.orders = set([1])
        self.orders_interface.setText('1')
        self.orders_interface.setClearButtonEnabled(True)
        self.orders_interface.returnPressed.connect(self.parseOrders)

    def parseOrders(self):
        orders = set()
        ptext = str(self.orders_interface.text())
        ranges = findall(r"[1-9]-[2-9]", ptext)
        for i in ranges:
            orders.update(range(int(i[0]), int(i[2])))
        single_digits = findall(r"[1-9]", ptext)
        orders.update([int(j) for j in single_digits])
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
        self.lineView = cw.LeavableTreeView(self)
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
    def __init__(self, font, text_color, pen, parent=None):
        Qt.QDialog.__init__(self, parent)
        self.setWindowTitle('customize preview')
        self.verticalLayout = Qt.QVBoxLayout(self)
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
        self.font_btn = QtWidgets.QToolButton()
        self.font_btn.setText('Fe_Ka')
        self.formLayout.setWidget(1,
                                  Qt.QFormLayout.FieldRole,
                                  self.font_btn)
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
        colors = [i.name() for i in darken(self.line_color_btn.color(), 8)]
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


class EDSCanvas(pg.PlotWidget):
    def __init__(self, kv=15, initial_mode='eds'):
        pg.PlotWidget.__init__(self,
                               viewBox=CustomViewBox(),
                               labels={'left': ['counts', 'cts']},
                               axisItems={'left': pg.AxisItem('left'),
                                          'bottom': CustomAxisItem('bottom')},
                               background=BACKGROUND_COLOR)
        # p1 the main plotItem/canvas
        # p2 secondary viewbox for EDS preview lines
        self.p1 = self.plotItem
        self.p2 = pg.ViewBox(enableMouse=True)
        self.p1.scene().addItem(self.p2)
        self.p2.setXLink(self.p1)
        self.bottom_axis = self.p1.axes['bottom']['item']
        self.updateViews()
        self.x_axis_mode = initial_mode
        self.set_kv(kv)
        self.siegbahn = True
        self.p1.vb.sigResized.connect(self.updateViews)
        self.prev_text_font = Qt.QFont()
        prev_marker_col = pg.mkColor((255, 200, 255, 180))
        self.prev_marker_pen = [pg.mkPen(i, width=2) for i in
                                darken(prev_marker_col, 8)]
        self.prev_edge_pen = pg.mkPen((0, 0, 0, 200), width=2, dash=[0.5, 1.5])
        self.prev_text_color = pg.mkColor((200, 200, 200))
        self.prev_edge_text_color = pg.mkColor((0, 0, 0))
        self.p1.setLimits(yMin=0)
        self.p2.setLimits(yMin=0)
        self.p2.setYRange(0, 1)
        self.set_xtal(8.75, 0.000144)  # default to PET crystal
        self.set_x_mode(self.x_axis_mode)
        self.set_connections()
        self.orders = set([1])

    def set_connections(self):
        self.bottom_axis.energyButton.toggled.connect(self.set_x_axis_from_gui)

    def set_siegbahn_state(self, state):
        self.siegbahn = state

    def set_x_axis_from_gui(self):
        if self.bottom_axis.energyButton.isChecked():
            self.set_x_mode('eds')
        else:
            self.set_x_mode('wds')

    def set_x_axis(self):
        if self.x_axis_mode == 'eds':
            self.p1.setLimits(xMin=-0.5)
            self.p1.setLabels(bottom='keV')
            self.set_kv(self.kv)
        elif self.x_axis_mode == 'wds':
            self.p1.setLimits(xMin=10000, xMax=95000)
            self.p1.setLabels(bottom='sin θ')

    def tweek_preview_style(self):
        style_dlg = PenEditor(self.prev_text_font,
                              self.prev_text_color,
                              self.prev_marker_pen[0])
        if style_dlg.exec_():
            values = style_dlg.return_styles()
            self.prev_text_font, self.prev_text_color, prev_marker_pen = values
            colors = darken(prev_marker_pen.color(), 8)
            width = prev_marker_pen.widthF()
            self.prev_marker_pen = [pg.mkPen(color, width=width)
                                    for color in colors]

    def set_xtal(self, two_D, K):
        self.two_D = two_D
        self.K = K
        self.axis_quotient = xu.calc_scale_to_sin_theta(two_D, K)

    def set_x_mode(self, mode):
        self.x_axis_mode = mode
        self.set_x_axis()
        if mode == 'eds':
            self.setXRange(0.45, self.kv)
        elif mode == 'wds':
            self.setXRange(20000, 88000)
            self.wds_orders = [1]

    def set_kv(self, kv):
        self.kv = kv
        if self.x_axis_mode == 'eds':
            self.p1.setLimits(xMax=self.kv)
        elif self.x_axis_mode == 'wds':
            self.p1.setLimits(xMin=xu.energy_to_sin_theta(self.kv,
                                                          self.two_D,
                                                          self.K))

    def updateViews(self):
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)

    def previewEdges(self, element):
        self.p2.setZValue(9999)
        if self.x_axis_mode == 'eds':
            lines = xu.xray_shells_for_plot(element)
        elif self.x_axis_mode == 'wds':
            lines = xu.xray_shells_for_plot_wds(element,
                                                two_D=self.two_D,
                                                K=self.K)
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

    def previewLines(self, element, kv=None, lines=None, siegbahn=None):
        if kv is None:
            kv = self.kv
        if siegbahn is None:
            siegbahn = self.siegbahn
        self.p2.clear()
        self.p2.setZValue(9999)
        css_color = colorCSS(self.prev_text_color)
        if lines is None:
            if self.x_axis_mode == 'eds':
                lines = {1: xu.xray_lines_for_plot(element, kv, siegbahn)}
            elif self.x_axis_mode == 'wds':
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


class PositionMarkers:
    def __init__(self, canvas=None):
        self.canvas = None
        self.m_line = None
        self.bg1_line = None
        self.bg2_line = None
        self.bg1_text = None
        self.bg2_text = None
        if canvas is not None:
            self.canvas = canvas
            self.initiate_lines()

    def gen_positions(self):
        axis_range = self.canvas.getAxis('bottom').range
        width = axis_range[1] - axis_range[0]
        lower = axis_range[0] + width * 0.25
        middle = axis_range[0] + width * 0.5
        higher = axis_range[0] + width * 0.75
        return lower, middle, higher

    def initiate_lines(self):
        lower, middle, higher = self.gen_positions()
        self.m_line = pg.InfiniteLine(middle, movable=True,
                                      pen=pg.mkPen('w', width=3.))
        self.bg1_line = pg.InfiniteLine(lower, movable=True,
                                        pen=pg.mkPen('w', width=1.5))
        self.bg2_line = pg.InfiniteLine(higher, movable=True,
                                        pen=pg.mkPen('w', width=1.5))
        self.bg1_text = pg.InfLineLabel(self.bg1_line, movable=True, color='w')
        self.bg2_text = pg.InfLineLabel(self.bg2_line, movable=True, color='w')
        self.m_text = pg.InfLineLabel(self.m_line, movable=True, color='w')
        self.update_marker_str()
        self.m_line.sigPositionChanged.connect(self.update_marker_str)
        self.bg1_line.sigPositionChanged.connect(self.update_marker_str)
        self.bg2_line.sigPositionChanged.connect(self.update_marker_str)
        self.add_to_canvas()

    def initiate_positions(self):
        lower, middle, higher = self.gen_positions()
        self.bg1_line.setValue(lower)
        self.bg2_line.setValue(higher)
        self.m_line.setValue(middle)

    def update_marker_str(self):
        pos_format = self.gen_precission_formater()
        self.bg1_text.setText(pos_format.format(
            self.bg1_line.value() - self.m_line.value()))
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
        return ''.join(['{:.', precission, 'f}'])

    def add_to_canvas(self):
        self.canvas.addItem(self.m_line)
        self.canvas.addItem(self.bg1_line)
        self.canvas.addItem(self.bg2_line)

    def remove_from_canvas(self):
        self.canvas.removeItem(self.m_line)
        self.canvas.removeItem(self.bg1_line)
        self.canvas.removeItem(self.bg2_line)

    def register_canvas(self, canvas):
        self.canvas = canvas
        if self.m_line is None:
            self.initiate_lines()
        else:
            self.initiate_positions()
            self.add_to_canvas()


class EDSSpectraGUI(cw.FullscreenableWidget):
    def __init__(self, parent=None, icon_size=None,
                 pet_opacity=None, initial_mode='eds'):
        cw.FullscreenableWidget.__init__(self, parent, icon_size)
        self.resize(550, 550)
        self._pet_opacity = pet_opacity
        self.centralwidget = Qt.QWidget()
        self.setCentralWidget(self.centralwidget)
        self.horizontalLayout = Qt.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(1, 1, 1, 1)
        self._setup_toolbar()
        self.canvas = EDSCanvas(initial_mode='eds')
        self.pos_markers = PositionMarkers()
        self._setup_menu()
        self._setup_connections()
        self.horizontalLayout.addWidget(self.canvas)

    def _setup_menu(self):
        menu = self.canvas.p1.getViewBox().menu
        self.actionClearMarker = menu.addAction('Remove cursors')

    def _setup_connections(self):
        self.pet.elementHoveredOver.connect(self.canvas.previewLines)
        self.pet.elementHoveredOver.connect(self.canvas.previewEdges)
        self.pet.elementHoveredOff.connect(self.canvas.clearPreview)
        self.config_preview.triggered.connect(
            self.canvas.tweek_preview_style)
        self.pet.hv_value.valueChanged.connect(self.canvas.set_kv)
        self.pet.someButtonRightClicked.connect(
            self.lineSelector.set_element_lines)
        self.lineSelector.lineView.entered.connect(
            self.preview_hovered_lines)
        self.lineSelector.lineView.mouseLeft.connect(
            self.canvas.clearPreview)
        self.pet.siegbahn.stateChanged.connect(
            self.broker_siegbahn_state_to_canvas)
        self.pet.ordersChanged.connect(self.broker_orders_state_to_canvas)
        self.actionMarker.triggered.connect(self.show_markers_on_canvas)
        self.actionClearMarker.triggered.connect(
            self.pos_markers.remove_from_canvas)
        self.pet.preview.toggled.connect(self.preview_toggle)
        self.pet.preview_edge.toggled.connect(self.preview_edges_toggle)

    def broker_siegbahn_state_to_canvas(self):
        self.canvas.siegbahn = self.pet.siegbahn.checkState()

    def broker_orders_state_to_canvas(self):
        self.canvas.orders = self.pet.orders

    @QtCore.pyqtSlot(bool)
    def preview_toggle(self, state):
        if state:
            self.pet.elementHoveredOver.connect(self.canvas.previewLines)
        else:
            self.pet.elementHoveredOver.disconnect(self.canvas.previewLines)

    @QtCore.pyqtSlot(bool)
    def preview_edges_toggle(self, state):
        if state:
            self.pet.elementHoveredOver.connect(self.canvas.previewEdges)
        else:
            self.pet.elementHoveredOver.disconnect(self.canvas.previewEdges)

    def _setup_toolbar(self):
        # add spacer:
        self._empty2 = Qt.QWidget()
        self._empty2.setSizePolicy(Qt.QSizePolicy.Expanding,
                                   Qt.QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty2)
        self.actionElementTable = Qt.QAction(self)
        self.actionElementTable.setIcon(Qt.QIcon(path.join(icon_path,
                                                           'pt.svg')))
        self.toolbar.addAction(self.actionElementTable)
        self._setup_pet()
        self.actionElementTable.triggered.connect(self.show_pet)
        self.toolbar.addSeparator()
        self.auto_button = cw.CustomToolButton(self)
        self._setup_auto()
        self.toolbar.addWidget(self.auto_button)
        self.config_button = cw.CustomToolButton(self)
        self.config_button.setIcon(
            Qt.QIcon(path.join(icon_path, 'tango_preferences_system.svg')))
        self._setup_config()
        self.toolbar.addWidget(self.config_button)
        self._empty1 = Qt.QWidget()
        self._empty1.setSizePolicy(Qt.QSizePolicy.Expanding,
                                   Qt.QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty1)
        self.actionMarker = Qt.QAction(self)
        self.actionMarker.setIcon(Qt.QIcon(path.join(icon_path,
                                                     'lines.svg')))
        self.toolbar.addAction(self.actionMarker)

    def show_markers_on_canvas(self):
        self.pos_markers.register_canvas(self.canvas.p1)

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
        self.dock_pet_win.setSizePolicy(QtGui.QSizePolicy.Minimum,
                                        QtGui.QSizePolicy.Minimum)
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
        self.dock_pet_win.resize(self.dock_pet_win.minimumSizeHint())
        self.dock_line_win.hide()
        self.dock_pet_win.hide()

    def show_pet(self):
        if self.dock_pet_win.isVisible():
            self.dock_pet_win.hide()
        else:
            self.dock_pet_win.show()

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
