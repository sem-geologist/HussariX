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

from PyQt5.QtWidgets import (QMainWindow, QToolBar, QAction,
                             QBoxLayout, QSplitter, QGridLayout,
                             QToolButton, QTreeView)
from PyQt5.QtGui import (QIcon, )
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import pyqtSignal as Signal

from ..icons.icons import IconProvider


class FullscreenableWidget(QMainWindow):
    attachedToParentWidget = Signal(bool)

    def __init__(self, parent=None, icon_size=None):
        QMainWindow.__init__(self, parent)
        self.toolbar = QToolBar('tools', parent=self)
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        self.icon_provider = IconProvider(self)
        self.dark_mode = self.icon_provider.get_theme_mode(self)
        if icon_size is not None:
            self.toolbar.setIconSize(QSize(icon_size, icon_size))
        self.addToolBar(Qt.RightToolBarArea, self.toolbar)

        self.action_fullscreen = QAction(self)
        self.action_fullscreen.setIcon(
            QIcon(self.icon_provider.get_icon_path('fullscreen.svg')))
        self.toolbar.addAction(self.action_fullscreen)
        self.action_windowed = QAction(self)
        self.action_windowed.setIcon(
            QIcon(self.icon_provider.get_icon_path('fullscreen_exit.svg')))
        # signalling:
        self.action_fullscreen.triggered.connect(self.go_fullscreen)
        self.action_windowed.triggered.connect(self.go_windowed)
        self.windowed_parent = None
        self.win_parent_layout = None
        self.index_in_layout = None
        self.windowed_flags = None
        self.windowed_geometry = None
        self.position_in_grid = None

    def go_fullscreen(self):
        self.windowed_flags = self.windowFlags()
        self.windowed_geometry = self.geometry()
        if self.parent() is not None:
            self.windowed_parent = self.parent()
            self.win_parent_layout = self.windowed_parent.layout()
            self.index_in_layout = self.win_parent_layout.indexOf(self)
            if isinstance(self.win_parent_layout, QGridLayout):
                self.position_in_grid = \
                    self.win_parent_layout.getItemPosition(
                        self.index_in_layout)
            self.win_parent_layout.removeWidget(self)
        self.setParent(None)
        self.attachedToParentWidget.emit(False)
        self.showFullScreen()
        self.toolbar.insertAction(self.action_fullscreen,
                                  self.action_windowed)
        self.toolbar.removeAction(self.action_fullscreen)

    def go_windowed(self):
        self.showNormal()
        if self.windowed_parent is not None:
            if isinstance(self.win_parent_layout, (QBoxLayout, QSplitter)):
                self.win_parent_layout.insertWidget(self.index_in_layout, self)
            elif isinstance(self.win_parent_layout, QGridLayout):
                self.win_parent_layout.addWidget(self, *self.position_in_grid)
            self.setParent(self.windowed_parent)
            self.attachedToParentWidget.emit(True)
            self.windowed_parent = None
        self.setGeometry(self.windowed_geometry)
        self.toolbar.insertAction(self.action_windowed,
                                  self.action_fullscreen)
        self.toolbar.removeAction(self.action_windowed)


class LeavableTreeView(QTreeView):
    """Customised QTreeView to emit signal when mouse leaves
    emits mouseLeft signal
    """
    mouseLeft = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def leaveEvent(self, event):
        self.mouseLeft.emit()
        super().leaveEvent(event)


class CustomToolButton(QToolButton):

    def __init__(self, parent=None):
        QToolButton.__init__(self, parent)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        # self.setPopupMode(QtWidgets.QToolButton.DelayedPopup)

    def set_action_to_default(self):
        action = self.sender()
        if action != self.defaultAction():
            self.setDefaultAction(action)
            self.setToolTip(action.text())
