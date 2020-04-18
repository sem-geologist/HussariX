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

from PyQt5 import QtCore, Qt, QtWidgets
from os import path

main_path = path.join(path.dirname(__file__), path.pardir)
icon_path = path.join(main_path, 'icons')


class FullscreenableWidget(QtWidgets.QMainWindow):
    def __init__(self, parent=None, icon_size=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.toolbar = Qt.QToolBar('tools', parent=self)
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        pallete = self.palette()
        w_lightness = pallete.window().color().lightness()
        wt_lightness = pallete.windowText().color().lightness()
        self.dark_mode = True if wt_lightness > w_lightness else False
        if icon_size is not None:
            self.toolbar.setIconSize(QtCore.QSize(icon_size,
                                                  icon_size))
        self.addToolBar(QtCore.Qt.RightToolBarArea, self.toolbar)

        self.actionFullscreen = Qt.QAction(self)
        self.actionFullscreen.setIcon(
            Qt.QIcon(self.gen_ico_path('fullscreen.svg')))
        self.toolbar.addAction(self.actionFullscreen)
        self.actionWindowed = Qt.QAction(self)
        self.actionWindowed.setIcon(
            Qt.QIcon(self.gen_ico_path('fullscreen_exit.svg')))
        # signalling:
        self.actionFullscreen.triggered.connect(self.go_fullscreen)
        self.actionWindowed.triggered.connect(self.go_windowed)

    def gen_ico_path(self, icon_base_name):
        ic_basename = icon_base_name
        if self.dark_mode:
            ic_basename = ic_basename[:-4] + '_dark.svg'
        return path.join(icon_path, ic_basename)

    def go_fullscreen(self):
        self.windowed_flags = self.windowFlags()
        self.windowed_geometry = self.geometry()
        if self.parent() is not None:
            self.windowed_parent = self.parent()
            self.windowed_parent_layout = self.windowed_parent.layout()
            self.index_in_layout = self.windowed_parent_layout.indexOf(self)
            self.windowed_parent_layout.removeWidget(self)
        self.setParent(None)
        self.showFullScreen()
        self.toolbar.insertAction(self.actionFullscreen,
                                  self.actionWindowed)
        self.toolbar.removeAction(self.actionFullscreen)

    def go_windowed(self):
        self.showNormal()
        if 'windowed_parent' in self.__dict__:
            self.windowed_parent_layout.insertWidget(self.index_in_layout,
                                                     self)
            self.setParent(self.windowed_parent)
            del self.windowed_parent
        self.setGeometry(self.windowed_geometry)
        self.toolbar.insertAction(self.actionWindowed,
                                  self.actionFullscreen)
        self.toolbar.removeAction(self.actionWindowed)


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


class CustomToolButton(QtWidgets.QToolButton):

    def __init__(self, parent=None):
        QtWidgets.QToolButton.__init__(self, parent)
        self.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        # self.setPopupMode(QtWidgets.QToolButton.DelayedPopup)

    def set_action_to_default(self):
        action = self.sender()
        if action != self.defaultAction():
            self.setDefaultAction(action)
            self.setToolTip(action.text())
