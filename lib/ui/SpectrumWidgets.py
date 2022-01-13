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
from PyQt5.QtCore import Qt, QPoint, QSize, QSignalBlocker, QEvent, QObject
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtGui import QIcon, QFont, QColor, QIntValidator, QPalette
from PyQt5.QtWidgets import (QWidget,
                             QAction,
                             QCheckBox,
                             QComboBox,
                             QLabel,
                             QMenu,
                             QListView,
                             QSizePolicy,
                             QAbstractScrollArea,
                             QHBoxLayout,
                             QGridLayout,
                             QSpinBox,
                             QSizeGrip,
                             QSpacerItem,
                             QTabWidget,
                             QInputDialog)


from .CamecaQtModels import (WDSPlotItem,
                             SpecXTALCombiModel)
from ..misc import xray_util as xu
from .node import ElementLineTreeModel, SimpleDictNode
from ..icons.icons import IconProvider
from .qpet import element_table as qpet
from . import CustomWidgets as cw
from .CustomPGWidgets import (CustomViewBox,
                              CustomAxisItem,
                              LineStyleButton,
                              menu_linestyle_entry_generator)
from .spectrum_curve import SpectrumCurveItem

import warnings
warnings.simplefilter('ignore', np.RankWarning)
# here we ignore polynomial  warnings, as we are not going to use
# polynomial outside initial data bounds

GAS_IN_COUNTER = ["Ar", "C", "H"]

main_path = path.join(path.dirname(__file__), path.pardir)
conf_path = path.join(main_path,
                      'configurations',
                      'lines.json')
#TODO coliding name, and oversimpilified json
with open(conf_path) as fn:
    jsn = fn.read()
lines = json.loads(jsn)

# TODO remove this
# dealling with windows-mind-slaves casted greek letters into latin:
dos_greek = {'a': 'α', 'b': 'β', 'c': 'γ', 'z': 'ζ'}


# QColor.name() returns the RGB not RGBA
def color_to_css(qcolor):
    """convert color to css string 'rgba(tuple)' format
       with alpha value. (QColor.name() is insufficient - without alpha)"""
    css_color = 'rgba({0}, {1}, {2}, {3})'.format(
                *pg.colorTuple(qcolor))
    return css_color


def desaturate(init_color, times, desat=True, lighten_darken="darken"):
    """return the list of recursively desaturated QColors
    desaturated and brightened/darkened (optionanly) at HSV space"""
    hsv = (init_color.hue(), init_color.hsvSaturation(),
           init_color.value(), init_color.alpha())
    if lighten_darken == "lighten":
        value_step = (hsv[2] - 255) // (times + 1)
    elif lighten_darken == "darken":
        value_step = hsv[2] // (times + 1)
    else:
        value_step = 0
    if desat:
        desat_step = hsv[1] // (times + 1)
    else:
        desat_step = 0
    color_list = [QColor.fromHsv(hsv[0],
                                 hsv[1] - desat_step * i,
                                 hsv[2] - value_step * i,
                                 hsv[3])
                  for i in range(times)]
    return color_list


def make_color_html_string(colors):
    """makes tooltip string with colors from color list"""
    colors = (i.name() for i in colors[:9])
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


# TODO Remove this
def utfize(text):
    """replace the a,b,c latin letters used by retards stuck in
    ms-dos age to greek α, β, γ
    """
    return ''.join(dos_greek[s] if s in dos_greek else s for s in text)

# pg.setConfigOptions(background=pg.mkColor(0, 43, 54))


def format_line_annotation(text, siegbahn=False):
    """wrap x-ray line plain text notation with html formating"""
    if siegbahn and (text in xu.iupac_siegbahn):
        text = xu.iupac_siegbahn[text]
        string = '{0}<i>{1}</i><sub>{2}</sub>'.format(text[0], text[1],
                                                      text[2:])
    else:
        string = sub(r'([1-7]+)', r'<sub>\1</sub>', text)
    return string


def string_with_order(string, order):
    if order == 2:
        string += '<sup>2<sup>nd</sup></sup>'
    elif order == 3:
        string += '<sup>3<sup>rd</sup></sup>'
    elif order > 3:
        string = '{0}<sup>{1}<sup>th</sup></sup>'.format(string, order)
    return string


def validate_idx_range(data_len, idx, window_size):
    """return min and max indexes for given distance from given index
    so that min and max values would stay in bounts of data length"""
    if idx - window_size > 0:
        idx_min = idx - window_size
    else:
        idx_min = 0
    if idx + window_size < data_len - 1:
        idx_max = idx + window_size
    else:
        idx_max = data_len - 1
    return idx_min, idx_max


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
        self.setMinimumSize(28, 28)
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
    fontStyleChanged = Signal(QFont)
    fontColorChanged = Signal(QColor)
    annotAnchorChanged = Signal(int)
    # anchor: 0 - left, 1 - left-bottom, 2 - bottom
    #         3 - botom-right, 4 - right

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_provider = IconProvider(self)
        self.siegbahn = QtWidgets.QPushButton('Siegbahn')
        self.siegbahn.setCheckable(True)
        self.siegbahn.setChecked(True)
        self.siegbahn.setToolTip("checked - Siegbahn notation "
                                 "(limited lines)\n"
                                 "unchecked - IUPAC notatation "
                                 "(more lines)")
        self.siegbahn.setMinimumSize(16, 16)
        self.hv_value = QtWidgets.QDoubleSpinBox()
        self.hv_value.setMinimumSize(16, 16)
        self.hv_value.setSuffix(" kV")
        self.hv_value.setToolTip(
            "HV value restricts x axis (max) in keV range and\n"
            "approximates the heights of preview lines as\n"
            "a function of effectivness of excitation\n"
            "(2.7 rule)")
        self.hv_value.setRange(0.1, 1e4)
        # add those parameters to the groupbox:
        self.g_line_par_group = QtWidgets.QFrame()
        self.g_line_par_group.setLayout(QtWidgets.QFormLayout())
        self.g_layout = self.g_line_par_group.layout()
        self.g_layout.setVerticalSpacing(1)
        self.g_layout.setContentsMargins(6, 0, 6, 6)
        self.layout().addWidget(self.g_line_par_group, 0, 2, 3, 10)
        self._setup_hidden_settings()
        # set the default states:
        self.preview_main_emission.setChecked(True)
        self.hv_value.setValue(15.)
        self.preview_edge.setCheckState(Qt.Checked)
        self.orders_interface = QtWidgets.QLineEdit()
        self.orders_interface.setMinimumSize(16, 16)
        self.orders_interface.setSizePolicy(QSizePolicy.Preferred,
                                            QSizePolicy.Preferred)
        self.g_layout.addRow("orders", self.orders_interface)
        self.g_layout.addRow("HV limit", self.hv_value)
        self.orders_interface.setToolTip("orders of diffracted lines\n"
                                         "to be shown on the plot")
        self.orders = set([1])
        self.orders_interface.setText('1')
        self.orders_interface.setClearButtonEnabled(True)
        self.orders_interface.returnPressed.connect(self.parseOrders)
        self.siegbahn.toggled.connect(self.set_notation_btn_text)
        self.preview_tab_settings.setVisible(False)
        icon = QIcon(self.icon_provider.get_icon_path(
                     'line_preview_settings.svg'))
        self.settings_button = QtWidgets.QPushButton(self)
        self.settings_button.setIcon(icon)
        self.settings_button.setCheckable(True)
        self.settings_button.toggled.connect(
            self.preview_tab_settings.setVisible)
        prev_shortcut_toggles = QtWidgets.QWidget()
        prev_shortcut_toggles.setLayout(QHBoxLayout())
        pst_l = prev_shortcut_toggles.layout()
        pst_l.setContentsMargins(0, 0, 0, 0)
        emi_icon = QIcon(self.icon_provider.get_icon_path('emission.svg'))
        self.all_emission_preview = QtWidgets.QCheckBox('')
        self.all_emission_preview.setToolTip(
            "Show Emission lines\n"
            "(for customisation look at settings\n"
            "at right)")
        self.all_emission_preview.setChecked(True)
        self.all_emission_preview.setMinimumSize(QSize(16, 16))
        self.all_emission_preview.setIcon(emi_icon)
        pst_l.addWidget(self.all_emission_preview)
        abs_icon = QIcon(self.icon_provider.get_icon_path("absorption.svg"))
        self.all_absorption_preview = QtWidgets.QCheckBox('')
        self.all_absorption_preview.setMinimumSize(QSize(16, 16))
        self.all_absorption_preview.setToolTip("Show Absorptions")
        self.all_absorption_preview.setChecked(True)
        self.all_absorption_preview.setIcon(abs_icon)
        pst_l.addWidget(self.all_absorption_preview)
        self.g_layout.addRow("on hover:", prev_shortcut_toggles)
        self.settings_button.toggled.connect(
            self.move_settings_but)
        self.settings_button.show()
        self.layout().addWidget(self.settings_button, 0, 18, 9, 1)
        self.settings_button.setMinimumSize(QSize(16, 16))
        self.settings_button.setMaximumHeight(1000)
        self.settings_button.setSizePolicy(QSizePolicy.Preferred,
                                           QSizePolicy.Expanding)
        self.layout().addWidget(self.preview_tab_settings, 0, 18, 9, 1)
        self.preview_tab_settings.setSizePolicy(QSizePolicy.Preferred,
                                                QSizePolicy.Preferred)
        self.preview_tab_settings.setMinimumWidth(160)
        self.preview_tab_settings.setMaximumWidth(180)
        self.settings_button.setToolTip("Show/hide preview-on-hover settings")
        self.prev_check_boxes = [self.preview_main_emission,
                                 self.preview_sat,
                                 self.preview_rae]
        self._temp_prev_states = [a.isChecked()
                                  for a in self.prev_check_boxes]
        self._temp_abs_states = [self.preview_edge.isChecked(),
                                 self.preview_edge_curve.isChecked()]
        self.all_emission_preview.toggled.connect(
            self.gatekeep_emission_preview)
        self.preview_main_emission.toggled.connect(
            self.keep_incheck_preview_gatekeeper)
        self.preview_sat.toggled.connect(
            self.keep_incheck_preview_gatekeeper)
        self.preview_rae.toggled.connect(
            self.keep_incheck_preview_gatekeeper)
        self.preview_edge.toggled.connect(
            self.keep_incheck_abs_gatekeeper)
        self.all_absorption_preview.toggled.connect(
            self.gatekeep_absorption_preview)

    def keyPressEvent(self, event):
        """Reimplementation of keyPressEvents to deal with
        CLI stealing the keyboard"""
        if self.notation_font_cb.hasFocus():
            event.ignore()
        else:
            super().keyPressEvent(event)

    def keep_incheck_preview_gatekeeper(self, box_checked):
        if box_checked:
            if self.all_emission_preview.isChecked():
                return
            else:
                self.all_emission_preview.blockSignals(True)
                self.all_emission_preview.setChecked(True)
                self.all_emission_preview.blockSignals(False)
        else:
            if not self.all_emission_preview.isChecked():
                return
            if any([a.isChecked() for a in self.prev_check_boxes]):
                return
            else:
                self.all_emission_preview.setChecked(False)

    def gatekeep_emission_preview(self, permit):
        if permit:
            if not any(self._temp_prev_states):
                self.preview_main_emission.setChecked(True)
            else:
                for i, check_box in enumerate(self.prev_check_boxes):
                    check_box.setChecked(self._temp_prev_states[i])
        else:
            self._temp_prev_states = [a.isChecked()
                                      for a in self.prev_check_boxes]
            for i in self.prev_check_boxes:
                i.setChecked(False)

    def keep_incheck_abs_gatekeeper(self, box_checked):
        self.all_absorption_preview.blockSignals(True)
        self.all_absorption_preview.setChecked(box_checked)
        self.all_absorption_preview.blockSignals(False)

    def gatekeep_absorption_preview(self, permit):
        self.preview_edge.setChecked(permit)

    def move_settings_but(self, state):
        if state:
            self.preview_tab_settings.setCornerWidget(self.settings_button)
            self.settings_button.show()
        else:
            self.layout().addWidget(self.settings_button, 0, 18, 8, 1)

    def _make_angle_spin_box(self, init_val):
        angle_box = QtWidgets.QSpinBox()
        angle_box.setValue(init_val)
        angle_box.setMaximum(90)
        angle_box.setMinimum(-90)
        angle_box.setSingleStep(15)
        angle_box.setPrefix("annot. ∡ ")
        angle_box.setSuffix("°")
        angle_box.setMinimumHeight(16)
        return angle_box

    def _setup_hidden_settings(self):
        self.preview_main_emission = QCheckBox("diagram lines")
        self.preview_main_emission.setToolTip(
            'preview-on-hover emission lines')
        self.preview_sat = QCheckBox('satelite lines')
        self.preview_sat.setToolTip("preview on hover sattelite lines")
        self.preview_sat.setMinimumSize(16, 16)
        self.preview_rae = QCheckBox("RAE lines")
        self.preview_rae.setToolTip("preview Radiative Auger Effect lines")
        self.preview_rae.setMinimumSize(16, 16)
        self.preview_edge = QCheckBox('edges')
        self.preview_edge.setToolTip('preview absorption edges')
        self.preview_edge.setMinimumSize(16, 16)
        self.preview_edge_curve = QCheckBox('spectrum')
        self.preview_edge_curve.setDisabled(True)
        #TODO hard disabled until curve data will be included
        self.preview_edge_curve.setToolTip("preview absorption curves (NIST)")
        self.preview_edge_curve.setMinimumSize(16, 16)
        self.preview_tab_settings = QTabWidget(self)
        self.emi_setup_group = QWidget()
        self.emi_setup_group.setLayout(QGridLayout())
        self.emi_layout = self.emi_setup_group.layout()
        self.emi_layout.setContentsMargins(2, 2, 2, 2)
        self.emi_layout.setHorizontalSpacing(1)
        self.emi_layout.setVerticalSpacing(1)
        self.emi_layout.addWidget(self.preview_main_emission, 0, 0, 1, 1)
        self.emi_layout.addWidget(self.siegbahn, 1, 0, 1, 1,
                                  Qt.AlignRight)
        self.emi_layout.addWidget(self.preview_sat, 2, 0, 1, 1)
        self.emi_layout.addWidget(self.preview_rae, 3, 0, 1, 1)
        self.emi_annot_rotator = self._make_angle_spin_box(0)
        self.emi_layout.addWidget(self.emi_annot_rotator, 4, 0, 2, 0)
        self.abs_setup_group = QWidget()
        self.abs_setup_group.setLayout(QGridLayout())
        self.abs_layout = self.abs_setup_group.layout()
        self.abs_layout.setContentsMargins(2, 2, 2, 2)
        self.abs_layout.setHorizontalSpacing(1)
        self.abs_layout.setVerticalSpacing(1)
        self.abs_layout.addWidget(self.preview_edge, 0, 0, 1, 1)
        self.abs_layout.addWidget(self.preview_edge_curve, 1, 0, 1, 1)
        self.prev_line_style_btn = LineStyleButton(size=None)
        self.prev_line_style_btn.setMinimumHeight(18)
        self.prev_line_style_btn.setMinimumWidth(18)
        self.emi_layout.addWidget(self.prev_line_style_btn, 0, 2, 3, 1)
        self.prev_line_style_btn.setSizePolicy(QSizePolicy.Expanding,
                                               QSizePolicy.Expanding)
        self.abs_style_btn = LineStyleButton(size=None)
        self.abs_style_btn.setMinimumHeight(18)
        self.abs_style_btn.setMinimumWidth(18)
        self.abs_layout.addWidget(self.abs_style_btn, 0, 1, 1, 1)
        self.preview_tab_settings.tabBar().setExpanding(False)
        self.preview_tab_settings.setStyleSheet(
            "QTabBar::tab { width: 44px; height:24px; }")
        tab_idx = self.preview_tab_settings.addTab(
            self.emi_setup_group,
            QIcon(self.icon_provider.get_icon_path('emission.svg')),
            "")
        self.preview_tab_settings.setTabToolTip(
            tab_idx, "emission preview settings")
        tab_idx = self.preview_tab_settings.addTab(
            self.abs_setup_group,
            QIcon(self.icon_provider.get_icon_path('absorption.svg')),
            "")
        self.preview_tab_settings.setTabToolTip(
            tab_idx, "absorption preview settings")
        self.notation_setup_group = QWidget()
        self.notation_setup_group.setLayout(QGridLayout())
        self.notation_layout = self.notation_setup_group.layout()
        self.notation_font_cb = QtWidgets.QFontComboBox()
        self.notation_font_cb.setMinimumWidth(48)
        self.notation_layout.addWidget(self.notation_font_cb, 0, 0, 1, 2)
        self.notation_layout.setContentsMargins(2, 2, 2, 2)
        self.notation_layout.setSpacing(1)
        self.notation_font_size_cb = QComboBox(self)
        self.notation_font_size_cb.setEditable(True)
        self.notation_font_size_cb.setValidator(QIntValidator(4, 100))
        self.notation_font_size_cb.addItems(
            [str(i) for i in [6, 8, 10, 12, 14, 16, 18, 20, 24, 32, 48, 72]])
        self.notation_font_size_cb.setCurrentIndex(2)
        self.notation_font_size_cb.setMinimumWidth(24)
        self.notation_layout.addWidget(self.notation_font_size_cb, 1, 0, 1, 1)
        self.notation_font_color = pg.ColorButton(self)
        self.notation_font_color.setMinimumWidth(24)
        self.notation_layout.addWidget(self.notation_font_color, 1, 1, 1, 1)
        self.annot_sample_anchor = QWidget()
        self.annot_sample_anchor.setLayout(QGridLayout())
        self.annot_anch_layout = self.annot_sample_anchor.layout()
        self.annot_anch_layout.setContentsMargins(1, 1, 1, 1)
        self.annot_anch_layout.setSpacing(0)
        self.radio_boxes = [QtWidgets.QRadioButton("", self) for i in range(5)]
        self.preview_text = QLabel("Ti K<i>α</i><sub>1</sub><sup>2nd</sup>")
        self.preview_text.setMaximumHeight(44)
        self.preview_text.setMaximumWidth(112)
        self.annot_anch_layout.addWidget(self.preview_text, 0, 1, 1, 1)
        self.annot_anch_layout.addWidget(
            self.radio_boxes[0], 0, 0, 1, 1, Qt.AlignRight)
        self.radio_boxes[1].setChecked(True)
        self.annot_anch_layout.addWidget(
            self.radio_boxes[1], 1, 0, 1, 1, Qt.AlignRight | Qt.AlignTop)
        self.annot_anch_layout.addWidget(self.radio_boxes[2], 1, 1, 1, 1,
                                         Qt.AlignCenter | Qt.AlignTop)
        self.annot_anch_layout.addWidget(self.radio_boxes[3], 1, 2, 1, 1,
                                         Qt.AlignLeft | Qt.AlignTop)
        self.annot_anch_layout.addWidget(self.radio_boxes[4], 0, 2, 1, 1)
        # self.text_anchor_group = QtWidgets.QButtonGroup()
        # Unfortunately Button group has changing api between different Qt version
        # it albeit would be more elegant way TODO in future

        #for i, check_box in enumerate(self.radio_boxes):
        #    self.text_anchor_group.addButton(check_box, i)
        #self.text_anchor_group.buttonPressed.connect(self.change_anchor)
        self.radio_boxes[0].pressed.connect(self.emit_anchor_0)
        self.radio_boxes[1].pressed.connect(self.emit_anchor_1)
        self.radio_boxes[2].pressed.connect(self.emit_anchor_2)
        self.radio_boxes[3].pressed.connect(self.emit_anchor_3)
        self.radio_boxes[4].pressed.connect(self.emit_anchor_4)
        spacer = QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.annot_anch_layout.addItem(spacer, 2, 3, 1, 1)
        self.notation_font_cb.currentFontChanged.connect(
            self.annot_change_font_family)
        self.notation_font_size_cb.currentTextChanged.connect(
            self.annot_change_font_size)
        self.notation_font_color.sigColorChanged.connect(
            self.annot_change_color)
        self.notation_layout.addWidget(self.annot_sample_anchor, 2, 0, 1, 2)
        self.annot_sample_anchor.setToolTip(
            "annotation sample and direction of anchor"
            "\n(the top of line which is annotated)"
        )
        tab_idx = self.preview_tab_settings.addTab(
            self.notation_setup_group,
            QIcon(self.icon_provider.get_icon_path('gtk-select-font.svg')),
            "")
        self.preview_tab_settings.setTabToolTip(
            tab_idx, "annotation font settings (for preview)")

    def emit_anchor_0(self):
        self.annotAnchorChanged.emit(0)

    def emit_anchor_1(self):
        self.annotAnchorChanged.emit(1)

    def emit_anchor_2(self):
        self.annotAnchorChanged.emit(2)

    def emit_anchor_3(self):
        self.annotAnchorChanged.emit(3)

    def emit_anchor_4(self):
        self.annotAnchorChanged.emit(4)

    def annot_change_font_family(self, family_font):
        family_font = QFont(family_font)
        new_family = family_font.family()
        pt_font = self.preview_text.font()
        pt_font.setFamily(new_family)
        self.preview_text.setFont(pt_font)
        self.fontStyleChanged.emit(pt_font)

    def annot_change_font_size(self, size_str):
        pt_font = self.preview_text.font()
        new_size = int(size_str)
        pt_font.setPointSize(new_size)
        self.preview_text.setFont(pt_font)
        self.fontStyleChanged.emit(pt_font)

    def annot_change_color(self, pg_color_button):
        palette = self.preview_text.palette()
        qcolor = pg_color_button.color()
        palette.setColor(QPalette.WindowText, qcolor)
        self.preview_text.setPalette(palette)
        self.fontColorChanged.emit(qcolor)

    #def change_anchor(self, index):
    #    self.annotAnchorChanged.emit(index)

    def parseOrders(self):
        """curently up to 15 orders (more is not very practical)"""
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

    def set_notation_btn_text(self, state):
        if state:
            self.siegbahn.setText('Siegbahn')
            self.siegbahn.adjustSize()
        else:
            self.siegbahn.setText('IUPAC')
            self.siegbahn.adjustSize()


class DockableXRayElementTable(QtWidgets.QDockWidget):
    def __init__(self, parent=None, **kwargs):
        QtWidgets.QDockWidget.__init__(self, parent=parent, **kwargs)
        self.restricted = False
        self.pet = XRayElementTable(parent=self, disable_fancy=True)
        self.pet.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWindowTitle('Element Table')
        if parent is not None:
            self.set_new_title(self.parent().name)
            self.parent().sig_name_had_changed.connect(self.set_new_title)
        self.setWidget(self.pet)

    def set_new_title(self, new_text):
        self.setWindowTitle('Element Table of {}'.format(new_text))


class FramelessXRayElementTable(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent=parent, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.restricted = False
        self.pet = XRayElementTable(parent=self, disable_fancy=True)
        self.pet.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(QtWidgets.QVBoxLayout(self))
        self.label = QtWidgets.QLabel('Element Table')
        self.label.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)
        self.label.setAlignment(Qt.AlignHCenter)
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        if parent is not None:
            self.set_new_title(self.parent().name)
            self.parent().sig_name_had_changed.connect(self.set_new_title)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.pet)
        self.sizegrip = QSizeGrip(self)
        self.sizegrip.setAttribute(Qt.WA_NoMousePropagation)
        self.pet.layout().addWidget(self.sizegrip, 8, 18, 1, 1,
                                    Qt.AlignBottom | Qt.AlignRight)
        self.pet.layout()
        self.layout().setContentsMargins(0, 1, 0, 0)
        self.layout().setSpacing(0)
        parent.widgetFullscreened.connect(self.setEmbeddedMode)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setEmbeddedMode(self.isFullScreen())

    def set_new_title(self, new_text):
        self.label.setText('Element Table of {}'.format(new_text))

    def mousePressEvent(self, event):
        self._mouse_clicked_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.restricted:
            gp = self.parent().mapFromGlobal(event.globalPos())
            lt_pos = gp - self._mouse_clicked_pos
            x, y = self.x(), self.y()
            if (lt_pos.x() >= 0) and ((lt_pos.x() + self.width()) <= self.parent().width()):
                x = lt_pos.x()
            if (lt_pos.y() >= 0) and ((lt_pos.y() + self.height()) <= self.parent().height()):
                y = lt_pos.y()
            self.move(x, y)
        else:
            self.move(event.globalPos() - self._mouse_clicked_pos)

    def setEmbeddedMode(self, fullscreen):
        visible = self.isVisible()
        if fullscreen:
            self.setWindowFlags(Qt.SubWindow)
            self.setAutoFillBackground(True)
            self.restricted = True
            self._old_pos = self.pos()
            if not self.parent().rect().contains(self.geometry()):
                p_r = self.parent().rect()
                self.move(p_r.center().x(), p_r.top())
        else:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
            self.restricted = False
            if hasattr(self, "_old_pos"):
                self.move(self._old_pos)
            else:
                self.move(self.parent().rect().center())
        if visible:
            self.show()


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


class XrayCanvas(pg.PlotWidget):

    xAxisUnitsChanged = Signal(str)
    yAxisUnitsChanged = Signal()

    def __init__(self, kv=15, initial_mode='energy', dark_mode=False):
        plot_bkg_color = pg.mkColor(22, 33, 44) \
            if dark_mode else pg.mkColor(250, 250, 255)
        pg.PlotWidget.__init__(
            self,
            viewBox=CustomViewBox(),
            axisItems={'left': CustomAxisItem('left'),
                       'bottom': CustomAxisItem('bottom')},
            background=plot_bkg_color)
        self.hideButtons()
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
        self._original_K = None
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
        self.annot_anchor = (0., 1.)
        self.abs_annot_angle = 90.
        self.emi_annot_angle = 0.
        self.p1.vb.sigResized.connect(self.updateViews)
        self.prev_text_font = QFont()
        if self.dark_mode:
            prev_marker_col = pg.mkColor((255, 255, 200, 180))
            self.prev_edge_text_color = pg.mkColor((200, 200, 200))
            self.prev_edge_pen = mkPen((200, 200, 200, 200), width=2,
                                       dash=[0.5, 1.5])
            self.prev_text_color = pg.mkColor((200, 200, 200))
        else:
            prev_marker_col = pg.mkColor((35, 10, 20, 180))
            self.prev_edge_text_color = pg.mkColor((50, 50, 50))
            self.prev_edge_pen = pg.mkPen((50, 50, 75, 200), width=2,
                                          dash=[0.5, 1.5])
            self.prev_text_color = pg.mkColor((50, 50, 50))
        self.css_annot_color = color_to_css(self.prev_text_color)
        if self.dark_mode:
            self.dl_order_mode = "darken"
        else:
            self.dl_order_mode = "lighten"
        self.prev_marker_pen = [pg.mkPen(i, width=2) for i in
                                desaturate(prev_marker_col, 15,
                                           lighten_darken=self.dl_order_mode)]

        self.p1.setLimits(yMin=0)
        self.p2.setLimits(yMin=0)
        self.p2.setYRange(0, 1)
        self.orders = set([1])
        self.xray_line_cache = {}
        self.xray_edge_cache = {}
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.xtal_family_text_item.setPos(0, self.bottom_axis.height())

    def set_annot_anchor(self, anchor_index):
        anchors = {0: (0., 0.5),
                   1: (0., 1.),
                   2: (0.5, 1.),
                   3: (1., 1.),
                   4: (1., 0.5)}
        self.annot_anchor = anchors[anchor_index]

    def set_emi_annot_angle(self, angle):
        self.emi_annot_angle = angle

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
            x_mode = ['energy', 'cameca', 'wavelength'][i]
            self.set_x_mode(x_mode)
            y_mode = self.y_axis_mode
        else:
            x_mode = self.x_axis_mode
            j = self.y_actions.index(action)
            y_mode = ['cts', 'cps', 'cpsna'][j]
            self.y_axis_mode = y_mode
            self.yAxisUnitsChanged.emit()
        for item in self.p1.curves:
            if isinstance(item, SpectrumCurveItem):
                item.set_spectrum_data(x_mode=x_mode, y_mode=y_mode)
        self.autoRange()

    def init_x_axis(self):
        if self.x_axis_mode == 'cameca':
            self.x_actions[1].trigger()
        elif self.x_axis_mode == 'wavelength':
            self.x_actions[2].trigger()
        else:
            self.x_actions[0].trigger()

    def set_preview_pens(self, new_pen):
        colors = desaturate(new_pen.color(), 15,
                            lighten_darken=self.dl_order_mode)
        self.prev_marker_pen = [mkPen(new_pen) for i in range(15)]
        for i, pen in enumerate(self.prev_marker_pen):
            pen.setColor(colors[i])
        return colors

    def set_xtal(self, family_name, two_D, K, html=None):
        if html is not None:
            self.xtal_family_text_item.setHtml(html)
            self.xtal_family_text_item.setPos(0, self.bottom_axis.height())
            self.xtal_family_text_family.setPos(0, self.bottom_axis.height())
        self.xtal_family_name = family_name
        self.two_D = two_D
        self.K = K
        self._original_K = None
        self.axis_quotient = xu.calc_scale_to_sin_theta(two_D, K)

    def set_tweeked_K(self, new_val):
        if self._original_K is None:
            self._original_K = self.K
        self.K = new_val

    def restore_original_K(self):
        self.K = self._original_K
        self._original_K = None

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
        elif mode == 'wavelength':
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

    def previewEdges(self, element, order=1):
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
            lines = xu.xray_shells_for_keV(element)
        elif xam == 'cameca':
            lines = xu.xray_shells_for_sin_θ_100k(element,
                                                  two_D=self.two_D,
                                                  K=self.K,
                                                  order=order)
            if element in GAS_IN_COUNTER:
                higher_order = xu.xray_shells_for_sin_θ_100k(
                    element, two_D=self.two_D, K=self.K, order=2)
                for line in higher_order:
                    line[0] = string_with_order(line[0], 2)
                lines.extend(higher_order)
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
            text = pg.TextItem(html="{0} {1}".format(element, i[0]),
                               anchor=(1., 1.),
                               angle=self.abs_annot_angle)
            text.setFont(self.prev_text_font)
            self.p2.addItem(text)
            text.setPos(i[1], 1.10)
            if xam == 'energy':
                final_list = elem_dict[xam]
            elif xam == 'cameca':
                final_list = elem_dict[xam][xfn]
            else:
                return
            final_list.append(line)
            final_list.append(text)

    def previewSatLines(self, element, kv=None):
        if kv is None:
            kv = self.kv
        self.p2.setZValue(9999)
        if element not in xu.sattelite_lines:
            return
        if self.x_axis_mode == 'energy':
            lines = {1: xu.sat_lines_for_keV(element, kv)}
        elif self.x_axis_mode == 'cameca':
            min_x, max_x = self.getAxis('bottom').range
            orders = [o for o in self.orders if o < 4]
            lines = {o: xu.sat_lines_for_sin_θ_100k(
                element, two_D=self.two_D, K=self.K, xmax=max_x,
                xmin=min_x, hv=kv, order=o)
                     for o in orders}
        for o in lines:  # for order
            for i in lines[o]:
                self._show_line(i, order=o)
                self._show_annot(i[1], i[2], i[0].split(maxsplit=1)[1],
                                 order=o)

    def _show_line(self, line_list, order=1):
        line = pg.PlotCurveItem([line_list[1], line_list[1]],
                                [0, line_list[2]],
                                pen=self.prev_marker_pen[order-1])
        self.p2.addItem(line)

    def _show_annot(self, x, y, text, order=1,
                    anchor=None, angle=None):
        if angle is None:
            angle = self.emi_annot_angle
        if anchor is None:
            anchor = self.annot_anchor
        text = pg.TextItem(html="""<body style="color:{0};">
{1}</body>""".format(self.css_annot_color,
                     string_with_order(text, order)),
                           anchor=anchor,
                           angle=angle)
        text.setFont(self.prev_text_font)
        self.p2.addItem(text)
        text.setPos(x, y)

    def previewRaeLines(self, element, kv=None):
        if kv is None:
            kv = self.kv
        if element not in xu.rae_lines:
            return
        self.p2.setZValue(9999)
        if self.x_axis_mode == 'energy':
            lines = {1: xu.rae_line_for_keV(element, kv)}
            arrow_text = '⟵'
            arrow_anchor = (1., 0.5)
            annot_anchor = (1., 1.)
        elif self.x_axis_mode == 'cameca':
            min_x, max_x = self.getAxis('bottom').range
            orders = [o for o in self.orders if o < 4]
            lines = {o: xu.rae_line_for_sin_θ_100k(
                element, two_D=self.two_D, K=self.K, xmax=max_x,
                xmin=min_x, hv=kv, order=o)
                     for o in orders}
            arrow_text = '⟶'
            arrow_anchor = (0., 0.5)
            annot_anchor = (0., 1.0)
        for o in lines:  # for order
            i = lines[o]
            if i is not None:
                self._show_line(i, order=o)
                arrow = pg.TextItem(text=arrow_text,
                                    color=self.prev_marker_pen[o-1].color(),
                                    anchor=arrow_anchor)
                font = arrow.textItem.font()
                font.setPointSize(12)
                font.setBold(True)
                arrow.setFont(font)
                arrow.setPos(i[1], i[2] / 2)
                self.p2.addItem(arrow)
                self._show_annot(i[1],
                                 i[2],
                                 " ".join([element, "KLL"]),
                                 order=o,
                                 anchor=annot_anchor,
                                 angle=0)

    def previewLines(self, element, kv=None, lines=None, siegbahn=None):
        if kv is None:
            kv = self.kv
        if siegbahn is None:
            siegbahn = self.siegbahn
        # self.p2.clear()
        self.p2.setZValue(9999)
        if lines is None:
            if self.x_axis_mode == 'energy':
                lines = {1: xu.xray_lines_for_keV(element, kv)}
            elif self.x_axis_mode == 'cameca':
                min_x, max_x = self.getAxis('bottom').range
                lines = {o: xu.xray_lines_for_sin_θ_100k(
                    element, two_D=self.two_D, K=self.K, xmax=max_x,
                    xmin=min_x, hv=kv, order=o)
                         for o in self.orders}
        else:
            # TODO
            pass
        for o in lines:  # for order
            for i in lines[o]:
                self._show_line(i, order=o)
                txt = " ".join([element,
                                format_line_annotation(i[0], siegbahn)])
                self._show_annot(i[1], i[2], txt, order=o)

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
        # TODO do we need that?
        pass


class PositionMarkers(QObject):
    def __init__(self, canvas=None,
                 initial_values=None):
        """
        atrributes:
        canvas - the pyqtgraph scene where the markers will be placed on
        initial_values - the tuple with initial values for generation of
        marker set (name, peak_position, left_relative_position,
        right_relative_position, slope_val, background_modeling_mode)
        """
        QObject.__init__(self)
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
        self.m_text = None
        self.m_text_pos = 0.80
        self.bg1_text_pos = 0.75
        self.bg2_text_pos = 0.75
        if canvas is not None:
            self.canvas = canvas
            self.initiate_lines()

    def eventFilter(self, obj, event):
        if (obj in [self.bg1_text, self.bg2_text, self.m_text]
                and event.type() == QEvent.GraphicsSceneMouseDoubleClick):
            if self.x_axis_mode == "cameca":
                lin_min = 15000
                lin_max = 95000
                decimals = 0
            elif self.x_axis_mode == "energy":
                lin_min = -0.8
                lin_max = 50
                decimals = 5
            else:
                lin_min = 0
                lin_max = 1000
                decimals = 5
            if obj == self.m_text:
                new_val = QInputDialog.getDouble(
                    self.parent(), "enter new", "position",
                    self.m_line.pos().x(), lin_min, lin_max,
                    decimals)
                if new_val[1]:
                    self.m_line.setPos(new_val[0])
            elif obj == self.bg1_text:
                new_val = QInputDialog.getDouble(
                    self.parent(), "enter new", "position",
                    self.bg1_line.pos().x() - self.m_line.pos().x(), -90000,
                    90000, decimals)
                if new_val[1]:
                    self.bg1_line.setPos(self.m_line.pos().x() + new_val[0])
            elif obj == self.bg2_text:
                new_val = QInputDialog.getDouble(
                    self.parent(), "enter new", "position",
                    self.bg2_line.pos().x() - self.m_line.pos().x(), -90000,
                    90000, decimals)
                if new_val[1]:
                    self.bg2_line.setPos(self.m_line.pos().x() + new_val[0])
            return True
        return False

    def transform_to_other_axis_units(self, new_mode):
        if new_mode == self.x_axis_mode:
            return
        if "cameca" in [new_mode, self.x_axis_mode]:
            quotient_e_sin = xu.calc_scale_to_sin_theta(
                self.canvas.two_D, self.canvas.K)
        if "wavelength" in [new_mode, self.x_axis_mode]:
            quotient_e_wav = xu.X_RAY_CONST / 1000_000
        if all(e in [self.x_axis_mode, new_mode] for e in ["cameca",
                                                           "energy"]):
            self.move_by_funct(quotient_e_sin.__truediv__)
        elif all(e in [self.x_axis_mode, new_mode] for e in ["wavelength",
                                                             "energy"]):
            self.move_by_funct(quotient_e_wav.__truediv__)
        elif (self.x_axis_mode == "cameca") and (new_mode == "wavelength"):
            self.move_by_funct((quotient_e_wav/quotient_e_sin).__mul__)
        elif (self.x_axis_mode == "wavelength") and (new_mode == "cameca"):
            self.move_by_funct((quotient_e_sin/quotient_e_wav).__mul__)
        self.x_axis_mode = new_mode

    def move_by_funct(self, function):
        self.m_line.setPos(function(self.m_line.getXPos()))
        if self.bg1_line is not None:
            self.bg1_line.setPos(function(self.bg1_line.getXPos()))
        if self.bg2_line is not None:
            self.bg2_line.setPos(function(self.bg2_line.getXPos()))
        self.m_line.sigPositionChanged.emit(self.m_line)

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
            if self.mode == 'two_bkgd':
                lower = axis_range[0] + width * 0.25
            else:
                lower = None
            middle = axis_range[0] + width * 0.5
            if self.mode in ('two_bkgd', 'single_bkgd'):
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
            color = '#eff0f1'
        else:
            color = '232629'
        lower, middle, higher = self.gen_positions()
        self.m_line = InfiniteLine(middle, movable=True,
                                   pen=mkPen(color, width=3.),
                                   name='main',
                                   markers=[('^', 0.99, 6.0)])
        self.m_line.setZValue(3000)

        if lower is not None:
            self.bg1_line = InfiniteLine(lower, movable=True,
                                         pen=mkPen(color, width=1.5),
                                         name='bkgd1',
                                         markers=[('v', 0.01, 6.0)])
            self.bg1_text = pg.InfLineLabel(self.bg1_line, movable=True,
                                            color=color,
                                            position=self.bg1_text_pos)
            self.bg1_text.installEventFilter(self)
            self.bg1_line.sigPositionChanged.connect(self.update_marker_str)

        if higher is not None:
            self.bg2_line = InfiniteLine(higher, movable=True,
                                         pen=mkPen(color, width=1.5),
                                         name='bkgd2',
                                         markers=[('v', 0.01, 6.0)])
            self.bg2_text = pg.InfLineLabel(self.bg2_line, movable=True,
                                            color=color,
                                            position=self.bg2_text_pos)
            self.bg2_text.installEventFilter(self)
            self.bg2_line.sigPositionChanged.connect(self.update_marker_str)
        self.m_text = pg.InfLineLabel(self.m_line, movable=True, color=color,
                                      position=self.m_text_pos)
        self.m_text.installEventFilter(self)
        self.update_marker_str()
        self.m_line.sigPositionChanged.connect(self.update_marker_str)
        self.add_to_canvas()
        # set a record of mode in case it would change:
        # so that it would be clear how to convert and move
        # markers
        self.x_axis_mode = self.canvas.x_axis_mode
        self.canvas.xAxisUnitsChanged.connect(
            self.transform_to_other_axis_units)

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
        try:
            self.canvas.xAxisUnitsChanged.disconnect(
                self.transform_to_other_axis_units)
        except(TypeError):
            pass  # it is not connected
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
        self.remove_from_canvas()
        self.initiate_lines()


class TwoPointBackground(pg.PlotDataItem):
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
        self.bg1_avg_curve = pg.PlotDataItem(pen=mkPen(width=3,
                                                       color=color))
        self.bg2_avg_curve = pg.PlotDataItem(pen=mkPen(width=3,
                                                       color=color))
        self.pw.avg_poly_order_spin.valueChanged.connect(
            self.update_background)
        self.pw.avg_win_size_spin.valueChanged.connect(
            self.update_background)
        self.pw.canvas.addItem(self.bg1_avg_curve)
        self.pw.canvas.addItem(self.bg2_avg_curve)
        self.bg1_avg_curve.setZValue(3002)
        self.bg2_avg_curve.setZValue(3002)
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
        data_x, data_y = curve.x_ref, curve.y_ref
        idx1 = np.abs(data_x - bg1_pos).argmin()
        idx2 = np.abs(data_x - bg2_pos).argmin()
        avg_window = self.pw.avg_win_size_spin.value()
        order = self.pw.avg_poly_order_spin.value()
        if avg_window == 0:
            x_pos1 = data_x[idx1]
            y_pos1 = data_y[idx1]
            x_pos2 = data_x[idx2]
            y_pos2 = data_y[idx2]
            self.bg1_avg_curve.setData()
            self.bg2_avg_curve.setData()
        else:
            data_len = len(data_x)
            i1_min, i1_max = validate_idx_range(data_len, idx1,
                                                avg_window)
            i2_min, i2_max = validate_idx_range(data_len, idx2,
                                                avg_window)
            xses1 = data_x[i1_min:i1_max+1]
            xses2 = data_x[i2_min:i2_max+1]
            ys1 = data_y[i1_min:i1_max+1]
            ys2 = data_y[i2_min:i2_max+1]
            poly1 = np.polynomial.polynomial.polyfit(xses1, ys1, order)
            poly2 = np.polynomial.polynomial.polyfit(xses2, ys2, order)
            y_pos1 = np.polynomial.polynomial.polyval(bg1_pos, poly1)
            y_pos2 = np.polynomial.polynomial.polyval(bg2_pos, poly2)
            self.bg1_avg_curve.setData(
                xses1,
                np.polynomial.polynomial.polyval(xses1, poly1))
            self.bg2_avg_curve.setData(
                xses2,
                np.polynomial.polynomial.polyval(xses2, poly2))
            x_pos1 = bg1_pos
            x_pos2 = bg2_pos

        x_linespace = np.linspace(min_pos - 0.2 * width,
                                  max_pos + 0.2 * width,
                                  num=512)
        y = self.get_background(x_pos1, x_pos2, y_pos1, y_pos2, x_linespace)
        self.setData(x_linespace, y)

    def prepare_to_destroy(self):
        self.pm.bg1_line.sigPositionChanged.disconnect(self.update_background)
        self.pm.bg2_line.sigPositionChanged.disconnect(self.update_background)
        self.pw.avg_poly_order_spin.valueChanged.disconnect(
            self.update_background)
        self.pw.avg_win_size_spin.valueChanged.disconnect(
            self.update_background)
        self.pw.canvas.removeItem(self.bg1_avg_curve)
        self.pw.canvas.removeItem(self.bg2_avg_curve)
        self.pm.m_line.sigPositionChanged.disconnect(self.update_background)
        self.sm.currentChanged.disconnect(self.update_background)


class LinearBackground(TwoPointBackground):
    @staticmethod
    def get_background(x_pos1, x_pos2, y_pos1, y_pos2, x_linespace):
        m = (y_pos2 - y_pos1) / (x_pos2 - x_pos1)
        b = y_pos1 - x_pos1 * m
        return x_linespace * m + b


class ExponentialBackground(TwoPointBackground):
    @staticmethod
    def get_background(x_pos1, x_pos2, y_pos1, y_pos2, x_linespace):
        m = (y_pos2 - y_pos1) / (x_pos2 - x_pos1)
        if m <= 0.0:  # exponential
            f = log(y_pos1 / y_pos2) / log(x_pos2 / x_pos1)
            return y_pos2 * (x_pos2 / x_linespace) ** f
        else:
            b = y_pos1 - x_pos1 * m
            return x_linespace * m + b


class SloppedBackground(pg.PlotDataItem):
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
        self.bg_avg_curve = pg.PlotDataItem(pen=mkPen(width=3,
                                                      color=color))
        self.pw.avg_poly_order_spin.valueChanged.connect(
            self.update_background)
        self.pw.avg_win_size_spin.valueChanged.connect(
            self.update_background)
        self.pw.canvas.addItem(self.bg_avg_curve)
        self.bg_avg_curve.setZValue(3002)
        self.signal_header = spect_xtal
        self.pm.bg2_line.sigPositionChanged.connect(self.update_background)
        self.pm.m_line.sigPositionChanged.connect(self.update_background)
        self.sm = self.pw.wds_tree_selection_model
        self.sm.currentChanged.connect(self.update_background)
        self.pw.slope_spin_box.sigValueChanging.connect(
            self.slope_from_spin_box)
        self.slope_from_spin_box(self.pw.slope_spin_box)
        self.pw.canvas.xAxisUnitsChanged.connect(self.update_background)

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
        bg_pos = self.pm.bg2_line.getXPos()
        lenght = bg_pos - m_pos
        plot_curves = self.pw.wds_tree_model.data(self.sm.currentIndex(),
                                                  Qt.UserRole)
        if plot_curves is None:
            return
        filtered = list(filter(filter_curve, plot_curves))
        if len(filtered) == 1:
            curve = filtered[0]
        else:
            return
        data_x, data_y = curve.x_ref, curve.y_ref
        idx = np.abs(data_x - bg_pos).argmin()
        avg_window = self.pw.avg_win_size_spin.value()
        order = self.pw.avg_poly_order_spin.value()
        if avg_window == 0:
            x_pos = data_x[idx]
            y_pos = data_y[idx]
        else:
            data_len = len(data_x)
            i1_min, i1_max = validate_idx_range(data_len, idx,
                                                avg_window)
            xses1 = data_x[i1_min:i1_max+1]
            ys1 = data_y[i1_min:i1_max+1]
            poly1 = np.polynomial.polynomial.polyfit(xses1, ys1, order)
            y_pos = np.polynomial.polynomial.polyval(bg_pos, poly1)
            self.bg_avg_curve.setData(
                xses1,
                np.polynomial.polynomial.polyval(xses1, poly1))
            x_pos = bg_pos
        y_pos_main = y_pos * slope
        h = y_pos - y_pos_main
        m = h / lenght
        min_pos = min(bg_pos,  m_pos)
        max_pos = max(bg_pos,  m_pos)
        if self.pw.canvas.x_axis_mode == "cameca":  # sin_theta space
            extrusion = 10000
        else:  # rather keV or  space
            extrusion = max_pos - min_pos
        x_linespace = np.linspace(min_pos - extrusion,
                                  max_pos + extrusion,
                                  num=512)
        b = y_pos - x_pos * m
        self.setData(x_linespace, x_linespace * m + b)

    def prepare_to_destroy(self):
        self.pm.bg2_line.sigPositionChanged.disconnect(self.update_background)
        self.pm.m_line.sigPositionChanged.disconnect(self.update_background)
        self.pw.avg_poly_order_spin.valueChanged.disconnect(
            self.update_background)
        self.pw.avg_win_size_spin.valueChanged.disconnect(
            self.update_background)
        self.pw.canvas.removeItem(self.bg_avg_curve)
        self.sm.currentChanged.disconnect(self.update_background)
        self.pw.slope_spin_box.sigValueChanging.disconnect(
            self.slope_from_spin_box)


class XraySpectraGUI(cw.FullscreenableWidget):
    """this is glue-like GUI widget with plotting widget and controls
    including the periodic element table, and managing interaction between
    different controls and widgets (i.e. previewing lines when interacting
    with periodic element table)."""
    sig_name_had_changed = Signal(str)

    def __init__(self, parent=None, icon_size=None,
                 pet_opacity=None, initial_mode='energy',
                 name='Plot Widget',
                 pet_frameless=True):
        cw.FullscreenableWidget.__init__(self, parent, icon_size)
        self._name = name
        self.resize(550, 550)
        self._pet_opacity = pet_opacity
        self._pet_frameless = pet_frameless
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
            in case of changing x units to wavelength or energy - that
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

    @Slot(bool)
    def preview_satelite_toggle(self, state):
        if state:
            self.pet.elementConsidered.connect(self.canvas.previewSatLines)
        else:
            self.pet.elementConsidered.disconnect(self.canvas.previewSatLines)

    @Slot(bool)
    def preview_rae_toggle(self, state):
        if state:
            self.pet.elementConsidered.connect(self.canvas.previewRaeLines)
        else:
            self.pet.elementConsidered.disconnect(self.canvas.previewRaeLines)

    def _setup_toolbar(self):
        # add spacer:
        self._empty2 = QtWidgets.QWidget()
        self._empty2.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty2)
        self.action_element_table = QAction(self)
        self.action_element_table.setIcon(
            QIcon(self.icon_provider.get_icon_path('pt.svg')))
        self.action_element_table.setToolTip("show/hide element table")
        self.action_element_table.setWhatsThis("show/hide element table")
        self.action_element_table.triggered.connect(self.show_pet)
        self.toolbar.addAction(self.action_element_table)
        self.toolbar.addSeparator()
        self._setup_auto()
        self.toolbar.addActions([self.auto_all, self.auto_width,
                                 self.auto_height])  #, self.auto_custom])
        self._empty1 = QtWidgets.QWidget()
        self._empty1.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.toolbar.addWidget(self._empty1)

    def _setup_auto(self):
        self.auto_all = QAction(
            QIcon(self.icon_provider.get_icon_path('auto_all.svg')),
            'all',
            self)
        self.auto_width = QAction(
            QIcon(self.icon_provider.get_icon_path('auto_width.svg')),
            'width',
            self)
        self.auto_height = QAction(
            QIcon(self.icon_provider.get_icon_path('auto_height.svg')),
            'height',
            self)
        self.auto_custom = QAction(
            QIcon(self.icon_provider.get_icon_path('auto_custom.svg')),
            'custom',
            self)
        # TODO currently not implemented:
        self.auto_custom.setDisabled(True)

    def _setup_pet(self):
        self.dock_line_win = QtWidgets.QDockWidget('Line selection', self)
        if self._pet_frameless:
            self.pet_win = FramelessXRayElementTable(parent=self)
        else:
            self.pet_win = DockableXRayElementTable(parent=self)
        self.pet = self.pet_win.pet
        self.lineSelector = LineEnabler(self.dock_line_win)
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
        self.pet.hv_value.valueChanged.connect(self.canvas.set_kv)
        self.pet.elementRightClicked.connect(
            self.lineSelector.set_element_lines)
        self.lineSelector.lineView.entered.connect(
            self.preview_hovered_lines)
        self.lineSelector.lineView.mouseLeft.connect(
            self.canvas.clearPreview)
        self.pet.siegbahn.toggled.connect(self.canvas.set_siegbahn_state)
        self.pet.ordersChanged.connect(self.broker_orders_state_to_canvas)
        self.pet.preview_main_emission.toggled.connect(self.preview_toggle)
        self.pet.preview_edge.toggled.connect(self.preview_edges_toggle)
        self.pet.preview_sat.toggled.connect(self.preview_satelite_toggle)
        self.pet.preview_rae.toggled.connect(self.preview_rae_toggle)
        # set colors and connections:
        self.pet.prev_line_style_btn.setPen(self.canvas.prev_marker_pen[0])
        self.pet.abs_style_btn.setPen(self.canvas.prev_edge_pen)
        self.pet.fontStyleChanged.connect(self.set_notation_font)
        self.pet.fontColorChanged.connect(self.set_notation_font_color)
        self.pet.annotAnchorChanged.connect(self.canvas.set_annot_anchor)
        self.pet.emi_annot_rotator.valueChanged.connect(
            self.set_emi_annot_angle)
        self.pet.prev_line_style_btn.penChanged.connect(
            self.change_prev_marker_pen)
        self.pet.abs_style_btn.penChanged.connect(
            self.change_prev_edge_pen)

    def set_emi_annot_angle(self, value):
        self.canvas.emi_annot_angle = value

    def set_notation_font(self, qfont):
        self.canvas.prev_text_font = qfont
        self.clear_cache()

    def clear_cache(self):
        self.canvas.xray_line_cache = {}
        self.canvas.xray_edge_cache = {}

    def set_notation_font_color(self, qcolor):
        self.canvas.prev_text_color = qcolor
        self.canvas.css_annot_color = color_to_css(self.canvas.prev_text_color)
        self.clear_cache()

    def change_prev_marker_pen(self, pen):
        colors = self.canvas.set_preview_pens(pen)
        self.canvas.xray_line_cache = {}
        tool_tip = make_color_html_string(colors)
        self.pet.prev_line_style_btn.setToolTip(tool_tip)

    def change_prev_edge_pen(self, pen):
        self.canvas.prev_edge_pen = pen
        self.canvas.xray_edge_cache = {}

    def show_pet(self):
        if self.pet is None:
            self._setup_pet()
            if self.isFullScreen():
                self.pet_win.move(self.pos() + QPoint(self.width() // 2, 0))
            else:
                self.pet_win.move(self.mapToGlobal(self.pos() + QPoint(self.width() // 2, 0)))
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
        bkgd_layout.addWidget(QLabel("Bkgd. slope:"))
        bkgd_layout.setContentsMargins(2, 2, 2, 2)
        self.bkgd_helper_widget.setMaximumHeight(28)
        self.slope_spin_box = pg.SpinBox(
            value=1.0, dec=True, min=0.001, max=1000, decimals=6,
            compactHeight=False)
        bkgd_layout.addWidget(self.slope_spin_box)
        bkgd_layout.addWidget(QLabel("avg. size:"))
        self.avg_win_size_spin = QSpinBox()
        self.avg_win_size_spin.setValue(10)
        self.avg_win_size_spin.setRange(1, 100)
        self.avg_win_size_spin.setSingleStep(1)
        bkgd_layout.addWidget(self.avg_win_size_spin)
        bkgd_layout.addWidget(QLabel("poly. ord.:"))
        self.avg_poly_order_spin = QSpinBox()
        self.avg_poly_order_spin.setValue(1)
        self.avg_poly_order_spin.setRange(1, 15)
        self.avg_poly_order_spin.setSingleStep(1)
        bkgd_layout.addWidget(self.avg_poly_order_spin)
        self.bkgd_helper_widget.setSizePolicy(size_policy)
        self.bkgd_helper_widget.hide()
        self.splitter.addWidget(self.spect_xtal_combo_view)
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
        self._setup_markers()
        self.toolbar.addActions([self.action_marker_only,
                                 self.action_marker_and_1bkg,
                                 self.action_marker_bgx2])
        self.toolbar.addSeparator()
        self.action_linear_background = QAction(self)
        self.lin_bkd_icons = {
            "lin": QIcon(self.icon_provider.get_icon_path(
                'linear_bkd.svg')),
            "slopped": QIcon(self.icon_provider.get_icon_path(
                'slopped_bkd.svg'))}
        self.action_linear_background.setIcon(self.lin_bkd_icons["lin"])
        self.action_linear_background.setCheckable(True)
        self.action_linear_background.setEnabled(False)
        self.action_linear_background.setToolTip('linear background')
        # self.action_linear_background.setDisabled(True)
        self.toolbar.addAction(self.action_linear_background)
        self.action_linear_background.toggled.connect(
            self.set_background_model)
        self.action_exp_background = QAction(self)
        self.action_exp_background.setIcon(
            QIcon(self.icon_provider.get_icon_path("exp_bkd.svg")))
        self.action_exp_background.setCheckable(True)
        self.action_exp_background.setEnabled(False)
        self.action_exp_background.setToolTip(
            'exponential background\n(as in Quanti of Cameca Peaksight)')
        self.toolbar.addAction(self.action_exp_background)
        self.action_exp_background.toggled.connect(
            self.set_background_model)

    def _setup_marker_remove(self):
        menu = self.canvas.p1.getViewBox().menu
        self.actionClearMarker = menu.addAction('Remove markers')
        self.actionClearMarker.setIcon(
            QIcon(self.icon_provider.get_icon_path('lines_hide.svg')))
        self.actionClearMarker.triggered.connect(
            self.clear_background_models)
        self.actionClearMarker.triggered.connect(
            self.pos_markers.remove_from_canvas)

    def set_background_model(self, *args):
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
        self.update_bkgd_helper_box_visibility()

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
        self.action_linear_background.setIcon(self.lin_bkd_icons["lin"])
        self.slope_spin_box.setEnabled(False)
        self.set_background_model()

    def show_two_markers_on_canvas(self):
        self.clear_background_models()
        self.pos_markers.set_mode('single_bkgd')
        self.pos_markers.register_canvas(self.canvas)
        self.action_linear_background.setEnabled(True)
        self.action_linear_background.setIcon(
            self.lin_bkd_icons["slopped"])
        self.action_exp_background.setEnabled(False)
        self.action_exp_background.setChecked(False)
        self.slope_spin_box.setEnabled(True)
        self.set_background_model()

    def show_single_marker_on_canvas(self):
        self.clear_background_models()
        self.pos_markers.set_mode('solo')
        self.action_linear_background.setChecked(False)
        self.action_exp_background.setChecked(False)
        self.pos_markers.register_canvas(self.canvas)
        self.action_linear_background.setEnabled(False)
        self.action_exp_background.setEnabled(False)

    def update_bkgd_helper_box_visibility(self):
        if self.action_linear_background.isChecked() or \
                self.action_exp_background.isChecked():
            self.bkgd_helper_widget.show()
        else:
            self.bkgd_helper_widget.hide()

    def _setup_markers(self):
        self.action_marker_bgx2 = QAction(
            QIcon(self.icon_provider.get_icon_path('lines_bgx2.svg')),
            'peak and 2 background',
            self)
        self.action_marker_bgx2.triggered.connect(
            self.update_bkgd_helper_box_visibility)
        self.action_marker_and_1bkg = QAction(
            QIcon(self.icon_provider.get_icon_path('lines_pk_1xbkg.svg')),
            'peak and single background',
            self)
        self.action_marker_and_1bkg.triggered.connect(
            self.update_bkgd_helper_box_visibility)
        self.action_marker_only = QAction(
            QIcon(self.icon_provider.get_icon_path('lines_1x_only.svg')),
            'single marker only',
            self)
        self.action_marker_only.triggered.connect(self.bkgd_helper_widget.hide)
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
            self.set_background_model()

    def change_style_of_spect(self, index_u, index_d, roles=[]):
        if len(roles) != 1:
            return
        role = roles[0]
        if role in [self.xtal_model.LineWidthRole,
                    self.xtal_model.LineStyleRole]:
            xm = self.xtal_model
            spect_header = xm.data(index_u, xm.SpectXtalCombinationRole)
            curves = [i for i in self.canvas.p1.curves
                      if isinstance(i, WDSPlotItem) and
                      (i.signal_header == spect_header)]
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
        # we need a copy of list to iterate through:
        curves_list = [i for i in self.canvas.p1.curves
                       if isinstance(i, WDSPlotItem) and
                       (i.signal_header == spect_header)]
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
