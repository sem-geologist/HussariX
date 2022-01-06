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

import re
import json
import os
import warnings
from glob import glob
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QToolButton,
                             QAbstractButton,
                             QWidget,
                             QGridLayout,
                             QPushButton,
                             QLabel,
                             QCompleter,
                             QLineEdit,
                             QFrame,
                             QSizePolicy)

# the periodic table possitions in gui:
# row, column:
pt_indexes = {'H': (0, 0), 'He': (0, 17), 'Li': (1, 0),
              'Be': (1, 1), 'B': (1, 12), 'C': (1, 13),
              'N': (1, 14), 'O': (1, 15), 'F': (1, 16),
              'Ne': (1, 17), 'Na': (2, 0), 'Mg': (2, 1),
              'Al': (2, 12), 'Si': (2, 13), 'P': (2, 14),
              'S': (2, 15), 'Cl': (2, 16), 'Ar': (2, 17),
              'K': (3, 0), 'Ca': (3, 1), 'Sc': (3, 2),
              'Ti': (3, 3), 'V': (3, 4), 'Cr': (3, 5),
              'Mn': (3, 6), 'Fe': (3, 7), 'Co': (3, 8),
              'Ni': (3, 9), 'Cu': (3, 10), 'Zn': (3, 11),
              'Ga': (3, 12), 'Ge': (3, 13), 'As': (3, 14),
              'Se': (3, 15), 'Br': (3, 16), 'Kr': (3, 17),
              'Rb': (4, 0), 'Sr': (4, 1), 'Y': (4, 2),
              'Zr': (4, 3), 'Nb': (4, 4), 'Mo': (4, 5),
              'Tc': (4, 6), 'Ru': (4, 7), 'Rh': (4, 8),
              'Pd': (4, 9), 'Ag': (4, 10), 'Cd': (4, 11),
              'In': (4, 12), 'Sn': (4, 13), 'Sb': (4, 14),
              'Te': (4, 15), 'I': (4, 16), 'Xe': (4, 17),
              'Cs': (5, 0), 'Ba': (5, 1), 'La': (7, 3),
              'Ce': (7, 4), 'Pr': (7, 5), 'Nd': (7, 6),
              'Pm': (7, 7), 'Sm': (7, 8), 'Eu': (7, 9),
              'Gd': (7, 10), 'Tb': (7, 11), 'Dy': (7, 12),
              'Ho': (7, 13), 'Er': (7, 14), 'Tm': (7, 15),
              'Yb': (7, 16), 'Lu': (7, 17), 'Hf': (5, 3),
              'Ta': (5, 4), 'W': (5, 5), 'Re': (5, 6),
              'Os': (5, 7), 'Ir': (5, 8), 'Pt': (5, 9),
              'Au': (5, 10), 'Hg': (5, 11), 'Tl': (5, 12),
              'Pb': (5, 13), 'Bi': (5, 14), 'Po': (5, 15),
              'At': (5, 16), 'Rn': (5, 17), 'Fr': (6, 0),
              'Ra': (6, 1), 'Ac': (8, 3), 'Th': (8, 4),
              'Pa': (8, 5), 'U': (8, 6), 'Np': (8, 7),
              'Pu': (8, 8)}

# element groups:
geo_groups = {'ALL': list(pt_indexes.keys())}
# geo groups can be added by modifying geo_groups.json file
gg_path = os.path.join(os.path.dirname(__file__), 'geo_groups.json')
with open(gg_path) as fn:
    gg_json = json.load(fn)

geo_groups.update(gg_json)

names_abbrv = {}
names_path = os.path.join(os.path.dirname(__file__), 'names_abbrv_')
names_files = glob(names_path + '*.json')
for i in names_files:
    with open(i) as fn:
        names_abbrv.update(json.load(fn))

ELEMENT_REGEX = r"(C[laroudse]?|Os?|N[eaibdps]?|S[icernbm]?|" +\
        r"H[eofga]?|A[lrsgutc]|B[erai]?|Dy|E[ur]|F[er]?|G[aed]|" +\
        r"I[nr]?|Kr?|L[iau]|M[gno]|R[buhena]|T[icebmalh]|" +\
        r"U|V|W|Xe|Yb?|Z[nr]|P[drmtboau])(?![a-z])"

GEO_REGEX = r'(?:%s)' % '|'.join(geo_groups.keys())

NAMES_REGEX = r'(?<![a-zA-Z])({})(?![a-z])'.format(
    '|'.join(names_abbrv.keys()))


def separate_text(ptext):
    """Separate text into positive and negative (prefixed with minus '-')"""
    if '-' in ptext:
        first_level = re.findall(r"[-]|[A-Z a-z,;]*", ptext)
        if first_level.index('-') == 0:
            positive_text = ''
            negative_text = first_level[1]
        else:
            positive_text = first_level[0]
            negative_text = first_level[first_level.index('-') + 1]
    else:
        positive_text = ptext
        negative_text = ''
    return positive_text, negative_text


def parse_elements(text):
    """parse element abreviations from given text"""
    parsed = []
    geo_list = re.findall(GEO_REGEX, text)
    for i in geo_list:
        parsed.extend(geo_groups[i])
        # to prevent situation where 'HFSE' would return ['H', 'F', 'S']
        # we replace parsed text with spaces. It is expensive
        # hopefully some alternative could be found
        text = text.replace(i, '')
    names_list = re.findall(NAMES_REGEX, text, re.I)
    for i in names_list:
        parsed.append(names_abbrv[i.lower()])
        text = text.replace(i, '')  # the same trick as with geo list
    parsed.extend(re.findall(ELEMENT_REGEX, text))
    return set(parsed)


class HoverableButton(QToolButton):
    """A Customised QToolButton, which emit
    additional signals when hovered over/off, right clicked
    or focuse changed with Tabulator
    ----------------
    initialisation arguments:

    name -- text which will be shown on button
    partly_disabled = True (default) -- controls behaviour,
       when set to True, the button when disabled, still
       emit custom signals and if fancy is enabled, react to
       mouse over events.
    disable_fancy = False --if set to True, then does not do
    the graphic geometric changes when hovered over/off.
    is_checkable = True (default) -- controls if button stays
       pushed when clicked, utill depressed by next click.
    """
    hoverChanged = QtCore.pyqtSignal()
    gainedFocus = QtCore.pyqtSignal()
    lostFocus = QtCore.pyqtSignal()
    rightClicked = QtCore.pyqtSignal()

    def __init__(self, name, partly_disabled=True,
                 disable_fancy=False, is_checkable=True):
        QAbstractButton.__init__(self)
        self.partly_disabled = partly_disabled
        self.fancy = not disable_fancy
        self.setMouseTracking(1)
        self.setText(name)
        if is_checkable:
            self.setCheckable(True)
        #if not self.fancy:
        #    self.setAutoRaise(True)
        self.hover_state = False
        self.orig_size = self.geometry()
        self.installEventFilter(self)

    def change_mode(self, mode):
        if mode == "single":
            self.setCheckable(False)
        elif mode == "multi":
            self.setCheckable(True)

    def focusInEvent(self, event):
        self.gainedFocus.emit()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.lostFocus.emit()
        super().focusOutEvent(event)

    def enterEvent(self, event):
        # signaling
        if self.isEnabled() or self.partly_disabled:
            self.hover_state = True
            self.hoverChanged.emit()
        # graphics
        if self.fancy and (self.isEnabled() or self.partly_disabled):
            self.orig_size = self.geometry()
            # some fancy graphic effects (inspired by KDE kalzium):
            self.setGeometry(self.orig_size.x() - self.orig_size.width() / 5,
                             self.orig_size.y() - self.orig_size.height() / 5,
                             self.orig_size.width() * 1.4,
                             self.orig_size.height() * 1.4)
            self.raise_()

    def leaveEvent(self, event):
        if self.isEnabled() or self.partly_disabled:
            self.hover_state = False
            self.hoverChanged.emit()
        if self.fancy and (self.isEnabled() or self.partly_disabled):
            self.setGeometry(self.orig_size)

    def eventFilter(self, QObject, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton:
                self.rightClicked.emit()
        return False


class ElementTableGUI(QWidget):
    """Create the periodic element gui with toggleble buttons
    for element selection and preview signal triggered with
    mouse hover events and right click for optional menu/ window.

    Initialisation can take python list with elements
    for which buttons is pre-toggled:
    -----------
    args:
    prechecked -- python list with elements (abbrevations), the
        buttons which should be initially pushed.
    state_list = python list -- list of elements (abbrevations) for buttons
        which should be disabled (by default) or enabled (if state_list_enables
        is True.
    state_list_enables = False (default) -- set interpretation of state_list
    silent_disabled = False (default) -- controls the behaviour of disabled
        element buttons if True, then disabled buttons do not emit any signal
    disable_fancy = False (default) -- controls if do button geometry changes
        with hover over/off events
    buttons_auto_depress = False (Default) -- controls if element buttons hold
    its state or only triggers when pushed (and automatically depresses).
    -----------

    additionally to native QtGui.QWidget provides
    such signals:

    elementConsidered -- signal which emits element abbrevation
        when mouse hovers over the button, or the coresponding
        button gets focus, or is emitted by text input interface.
    elementUnconsidered -- emits element abrevation at moment mouse
        leaves the button area
    elementChecked -- emits the element abbrevation when button
        changes to checked possition.
    elementUnchecked -- emits the element abbrevation when button
        changes to unchecked possition.
    elementRightClicked -- emits the element abbrevation when
        button gets right clicked.
    elementTriggered -- emits the element abbrevation when button gets
        triggered (intended to be used with buttons_auto_depress=True)

    allElementsCleared -- emits, when the clear all button clicked.
        Alternatively the element by element could be dissabled,
        however this signal can be much faster.
    """

    # preview slots:
    elementConsidered = QtCore.pyqtSignal(str)
    elementUnconsidered = QtCore.pyqtSignal(str)
    # button press slots:
    elementChecked = QtCore.pyqtSignal(str)
    elementUnchecked = QtCore.pyqtSignal(str)
    elementTriggered = QtCore.pyqtSignal(str)
    # right_mouse_button_press_slot:
    elementRightClicked = QtCore.pyqtSignal(str)
    allElementsCleared = QtCore.pyqtSignal()

    def __init__(self, parent=None,
                 prechecked=[], state_list=[],
                 state_list_enables=False, silent_disabled=False,
                 disable_fancy=False, buttons_auto_depress=False):
        super().__init__()
        if type(state_list) == str:
            state_list = parse_elements(state_list)
        if (len(prechecked) > 0) and buttons_auto_depress:
            warnings.warn(
                "element table is initialised with opposite"
                " arguements - seting buttons to auto depress rules out"
                " using prechecked element list. The list is ignored")
            prechecked = []
        self.setWindowTitle('Element Table')
        layout = QGridLayout(self)
        self.setLayout(layout)
        layout.setSpacing(0)
        layout.setContentsMargins(4, 4, 4, 4)
        partly_disabled = not silent_disabled
        self._setup_table(prechecked, state_list, state_list_enables,
                          partly_disabled, disable_fancy, buttons_auto_depress)
        self._setup_text_interface()
        self._setup_clear_all()
        if not buttons_auto_depress:
            self.set_table_mode('multi')  # default
        else:
            self.set_table_mode('single')
        self.resize(400, 250)

    def _setup_clear_all(self):
        self.clear_all_button = QPushButton('Clear all')
        self.layout().addWidget(self.clear_all_button, 7, 0, 2, 3)
        self.clear_all_button.pressed.connect(self.clear_all)
        self.clear_all_button.setMinimumSize(32, 32)
        self.clear_all_button.setMaximumSize(512, 512)

    def _setup_text_interface(self):
        self.textInterface = QLineEdit()
        self.textInterface.setMinimumSize(16, 16)
        self.layout().addWidget(self.textInterface, 8, 9, 1, 9)
        self.textInterface.returnPressed.connect(self.toggle_elements)
        self.textInterface.textChanged.connect(self.consider_element)
        self.textInterface.setMaximumSize(512, 1024)

    def set_extended_completer(self):
        completer = QCompleter(list(pt_indexes.keys()) +
                               list(geo_groups.keys()) +
                               list(names_abbrv.keys()))
        self.textInterface.setCompleter(completer)

    def set_simple_completer(self):
        completer = QCompleter(list(pt_indexes.keys()))
        self.textInterface.setCompleter(completer)

    def set_table_mode(self, mode):
        if mode == 'multi':
            self.textInterface.setEnabled(True)
            self.set_extended_completer()
            self.textInterface.setToolTip(
                "text interface.\n"
                "Input abbrevations of elements:\n"
                "    without any space:\n"
                "        AlSiNaK\n"
                "    with any separators like comma/space:\n"
                "        Al;Br K,La\n"
                "abbrevations of element groups (in all caps):\n"
                "    HFSE, REE, REE_SEM, LILE, MAJOR\n"
                "Use '-' (minus) sign to disable elements:\n"
                "    -AlCa, K; P -> toggles off Al, Ca, K, P\n"
                "HFSE - Nb -> toggles on HFSE elements, but switches off Nb")
            self.clear_all_button.setEnabled(True)
            self.textInterface.setInputMask("")
        elif mode == 'single':
            self.textInterface.setEnabled(False)
            # self.set_simple_completer()
            # self.textInterface.setToolTip(
            #    "Enter a single element abbreviation")
            self.clear_all_button.setEnabled(False)
            # self.textInterface.setInputMask(">A<a")
        for i in geo_groups['ALL']:
            self.getButton_by_name(i).change_mode(mode)

    def getButton(self, index):
        """helper function to get button by position
        index - tuple (row, column)"""
        item = self.layout().itemAtPosition(*index)
        return item.widget()

    def getButton_by_name(self, name):
        """helper function to get button by abbrevation of
        the element"""
        item = self.layout().itemAtPosition(*pt_indexes[name])
        return item.widget()

    def toggle_elements(self):
        ptext = self.textInterface.text()
        positive_text, negative_text = separate_text(ptext)
        # clear text interface:
        self.textInterface.clear()
        # parse what to add first:
        positive_list = parse_elements(positive_text)
        self.toggle_on(positive_list)
        # parse what to remove:
        negative_list = parse_elements(negative_text)
        self.toggle_off(negative_list)

    def consider_element(self, text):
        positive_text = separate_text(text)[0]
        positive_list = parse_elements(positive_text)
        self.elementUnconsidered.emit('')
        for i in positive_list:
            self.elementConsidered.emit(i)

    def toggle_on(self, toggle_list):
        for i in toggle_list:
            button = self.getButton(pt_indexes[i])
            if button.isEnabled():
                button.setChecked(True)

    def toggle_off(self, toggle_list):
        for i in toggle_list:
            button = self.getButton(pt_indexes[i])
            if button.isEnabled():
                button.setChecked(False)

    def clear_all(self):
        """uncheck all buttons, and send single signal instead of
           many per button, which allows to do related action in
           more snappy maner."""
        self.blockSignals(True)
        self.toggle_off(geo_groups['ALL'])
        self.blockSignals(False)
        self.allElementsCleared.emit()

    def _setup_table(self, prechecked_elements, state_list,
                     state_list_enables, partly_disabled, disable_fancy,
                     auto_depresso):
        self.signalMapper = QtCore.QSignalMapper(self)
        self.signalMapper.mapped[QWidget].connect(self.previewToggler)
        self.signalMapper2 = QtCore.QSignalMapper(self)
        self.signalMapper2.mapped[QWidget].connect(self.elementToggler)
        self.signalMapper3 = QtCore.QSignalMapper(self)
        self.signalMapper3.mapped[QWidget].connect(self.emit_right_clicked)
        self.signalMapper4 = QtCore.QSignalMapper(self)
        self.signalMapper4.mapped[QWidget].connect(self.focus_on_toggler)
        self.signalMapper5 = QtCore.QSignalMapper(self)
        self.signalMapper5.mapped[QWidget].connect(self.focus_off_toggler)
        self.signalMapper6 = QtCore.QSignalMapper(self)
        self.signalMapper6.mapped[QWidget].connect(self.emit_triggered)
        is_checkable = not auto_depresso
        for i in pt_indexes:
            pt_button = HoverableButton(i, partly_disabled=partly_disabled,
                                        disable_fancy=disable_fancy,
                                        is_checkable=is_checkable)
            pt_button.setMinimumSize(16, 16)
            pt_button.setMaximumSize(512, 512)
            if i in prechecked_elements:
                pt_button.setChecked(True)
            self.layout().addWidget(pt_button,
                                    pt_indexes[i][0],
                                    pt_indexes[i][1])
            # pt_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            pt_button.hoverChanged.connect(self.signalMapper.map)
            pt_button.toggled.connect(self.signalMapper2.map)
            pt_button.rightClicked.connect(self.signalMapper3.map)
            pt_button.gainedFocus.connect(self.signalMapper4.map)
            pt_button.lostFocus.connect(self.signalMapper5.map)
            pt_button.pressed.connect(self.signalMapper6.map)
            self.signalMapper.setMapping(pt_button, pt_button)
            self.signalMapper2.setMapping(pt_button, pt_button)
            self.signalMapper3.setMapping(pt_button, pt_button)
            self.signalMapper4.setMapping(pt_button, pt_button)
            self.signalMapper5.setMapping(pt_button, pt_button)
            self.signalMapper6.setMapping(pt_button, pt_button)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.layout().addWidget(line, 6, 3, 1, 15)
        # dissable elements/buttons for provided list:
        if state_list_enables:
            disabled_elements = set(pt_indexes).difference(state_list)
        else:
            disabled_elements = state_list
        for i in disabled_elements:
            self.getButton(pt_indexes[i]).setEnabled(False)
        lant_text = QLabel('Lan')
        act_text = QLabel('Act')
        lant_text.setAlignment(QtCore.Qt.AlignCenter)
        act_text.setAlignment(QtCore.Qt.AlignCenter)
        self.layout().addWidget(lant_text, 5, 2)
        self.layout().addWidget(act_text, 6, 2)
        lant_text.setEnabled(False)
        act_text.setEnabled(False)

    def update_state(self, element, enable=True):
        """update state of button for given element
        (enable, disable); this method is intended to
        be used when model containing element list is
        updated (new element added or removed)"""
        self.signalMapper2.blockSignals(True)
        button = self.getButton_by_name(element)
        if not enable and button.isChecked():
            button.setChecked(False)
        button.setEnabled(enable)
        self.signalMapper2.blockSignals(False)

    def keyPressEvent(self, event):
        """Jump to text interface at shift key press"""
        if (event.modifiers() == QtCore.Qt.ShiftModifier) and \
                (not self.textInterface.hasFocus())and \
                (QtCore.Qt.Key_A <= event.key() <= QtCore.Qt.Key_Z):
            self.textInterface.setFocus()
            self.textInterface.clear()
            self.textInterface.insert(event.key().to_bytes(1, 'big').decode())
        else:
            super().keyPressEvent(event)

    # @QtCore.pyqtSlot(QtCore.QObject)  # NOTE decorators are commented out
    # as pyQt5.7 made regression with using QObject or QWidget in signals
    # or is it the problem with mapping of signals?
    def previewToggler(self, button):
        # if button.isEnabled():
        if button.hover_state:
            self.elementConsidered.emit(button.text())
        else:
            self.elementUnconsidered.emit(button.text())

    def focus_on_toggler(self, button):
        """this is for sending same signal as with hovering, but by
        "Tab" jumping through buttons"""
        self.elementConsidered.emit(button.text())

    def focus_off_toggler(self, button):
        """this is for sending same signal as with hovering, but by
        "Tab" jumping through buttons"""
        self.elementUnconsidered.emit(button.text())

    # @QtCore.pyqtSlot(QtCore.QObject)
    def elementToggler(self, button):
        if button.isChecked():
            self.elementChecked.emit(button.text())
            if button.hover_state and button.fancy:
                button.setGeometry(button.orig_size)
        else:
            self.elementUnchecked.emit(button.text())

    # @QtCore.pyqtSlot(QtCore.QObject)
    def emit_right_clicked(self,  button):
        self.elementRightClicked.emit(button.text())

    def emit_triggered(self, button):
        self.elementTriggered.emit(button.text())

    def switch_button_wo_trigger(self, elements, press=True):
        """This method is intended to be connected with list model signal;
        it blocks signal so that there would be no loop of triggering
        back and forth between button and list model if state of checkbox
        in list is bined with state of button."""
        self.signalMapper2.blockSignals(True)
        if press:
            self.toggle_on(elements)
        else:
            self.toggle_off(elements)
        self.signalMapper2.blockSignals(False)
