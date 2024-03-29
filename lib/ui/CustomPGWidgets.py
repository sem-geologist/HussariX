"""Custom PyqtGraph widgets and functions"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import (QPixmap, QPen, QColor, QPainter, QPainterPath)
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QWidgetAction, QLabel, QMenu, QColorDialog
from PyQt5.QtCore import pyqtSignal as Signal

import pyqtgraph as pg

default_pen = pg.mkPen((255, 255, 75), width=2)
default_hover_pen = pg.mkPen((255, 50, 50), width=2)
default_select_pen = pg.mkPen((255, 255, 255), width=2)


def menu_linestyle_entry_generator(pen_style=Qt.SolidLine, width=2,
                                   parent=None, color=QColor(246, 116, 0)):
    """return QWidgetAction with QLabel widget as main widget where
    it is displaying sample line painted with provided pen_style and width"""
    menu_entry = QWidgetAction(parent)
    label = QLabel(parent)
    pix = QPixmap(74, 24)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    pen = QPen(color, width,
               pen_style)
    painter.setPen(pen)
    painter.drawLine(5, 12, 75, 12)  # ForegroundNeutral
    painter.end()
    label.setPixmap(pix)
    menu_entry.setDefaultWidget(label)
    menu_entry.pen = pen  # this attribute will hold the style
    return menu_entry


class LineStyleButton(pg.PathButton):
    penChanged = Signal(QPen)

    def __init__(self, *args, **kwargs):
        pg.PathButton.__init__(self, **kwargs)
        self.pressed.connect(self.change_pen_color)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.set_pen_from_menu)
        self.update_path()

    def resizeEvent(self, event):
        pg.PathButton.resizeEvent(self, event)
        self.update_path()

    def update_path(self):
        path = QPainterPath(QPointF(0, 0))
        path.lineTo(self.width() - 2, self.height() - 2)
        self.setPath(path)

    def setPen(self, *args, **kwargs):
        self.pen = pg.mkPen(*args, **kwargs)
        self.penChanged.emit(self.pen)

    def change_pen_color(self):
        init_color = self.pen.color()
        new_color = QColorDialog.getColor(init_color)
        if new_color.isValid():
            self.pen.setColor(new_color)
            self.setPen(self.pen)
            self.update()

    def set_pen_from_menu(self, pos):
        pos_glob = self.mapToGlobal(pos)
        color = self.pen.color()
        style = self.pen.style()
        width = self.pen.width()
        line_pattern_menu = QMenu("line pattern")
        for i in [Qt.SolidLine, Qt.DotLine, Qt.DashLine, Qt.DashDotLine,
                  Qt.DashDotDotLine]:
            action = menu_linestyle_entry_generator(width=width,
                                                    pen_style=i,
                                                    parent=line_pattern_menu,
                                                    color=color)
            line_pattern_menu.addAction(action)

            line_pattern_menu.addSeparator()
        line_width_menu = QMenu("line width")
        for j in [1, 2, 3, 4, 5]:
            action = menu_linestyle_entry_generator(width=j,
                                                    pen_style=style,
                                                    parent=line_width_menu,
                                                    color=color)
            line_width_menu.addAction(action)
            line_width_menu.addSeparator()
        line_style_menu = QMenu()
        line_style_menu.addMenu(line_pattern_menu)
        line_style_menu.addMenu(line_width_menu)
        selected_style = line_style_menu.exec(pos_glob)
        if selected_style is not None:
            selected_style.pen.setCosmetic(True)
            self.setPen(selected_style.pen)


class CustomScaleBar(pg.ScaleBar):
    def __init__(self, size, width=5, brush=None, pen=None, suffix='m',
                 offset=None):
        self.units = suffix
        pg.ScaleBar.__init__(self, size, width=5, brush=None, pen=None,
                             suffix='m', offset=None)
        self.text.setAnchor((0.5, 0))

    def change_scale(self, new_scale):
        self.size = new_scale
        self.text.setText(pg.functions.siFormat(new_scale, suffix=self.units))
        self.updateBar()


class CustomViewBox(pg.ViewBox):
    """overriden pyqtgraph.ViewBox class with scaleBy method
    allowing to bound y_min during zoom to 0.0"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def scaleBy(self, s=None, center=None, x=None, y=None):
        """copied from pyqtgraph, with minimal modification
        to bound low y at current low-y position;
        to change low y viewbox needs to be panned.
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
        current_top = vr.top()  # Qt is having top at the bottom
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
            # ??? Why needs to be Top, it is intended to bound Bottom:
            # old_rectangle.top() gives bottom coordinates...
            new_rect.moveTop(current_top)
            self.setRange(new_rect, padding=0)


class CustomAxisItem(pg.AxisItem):
    """
    This Customised AxisItem can be setup with actions,
    which appear in the menu after right click.
    actions are required to contain special attributes
    such as action._si_units
    and action._title -- which will be the text/units to be
    displayed on the Axis. Menu will show entry using
    action.text().
    """
    def __init__(self, *args, **kwargs):
        self.menu = None
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.actions = None

    def init_actions(self, actions, action_group):
        self.actions = actions
        self.action_group = action_group
        action_group.triggered.connect(self.changeUnits)

    def changeUnits(self, action):
        if action._si_units:
            units = action.text()
        else:
            units = None
        self.setLabel(text=action._title, units=units)

    # On right-click, raise the context menu
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            pos = ev.pos()
            if self.rect().contains(pos):
                self.raiseContextMenu(ev)
                ev.accept()
            else:  # prevent from raising axis menu on vb  with grid enabled
                ev.ignore()

    def raiseContextMenu(self, ev):
        menu = self.getContextMenus()

        # Let the scene add on to the end of our context menu
        # (this is optional)
        # menu = self.scene().addParentContextMenus(self, menu, ev)

        pos = ev.screenPos()
        menu.popup(QtCore.QPoint(int(pos.x()), int(pos.y())))
        return True

    # This method will be called when this item's _children_ want to raise
    # a context menu that includes their parents' menus.
    def getContextMenus(self, event=None):
        if self.menu is None:
            self.menu = QtWidgets.QMenu()
            self.menu.setTitle("axis options..")
            for i in self.actions:
                self.menu.addAction(i)
        return self.menu


class SelectableMarker:

    # sigClicked = QtCore.Signal(object)
    # sigHovered = QtCore.Signal()
    # sigLeft = QtCore.Signal()

    def __init__(self, data, *args, pen=default_pen):
        self.setAcceptHoverEvents(True)
        self.internal_pointer = data
        self.setPen(pen)
        self.original_pen = pen
        self.savedPen = pen
        self.selected = False

    def hoverEnterEvent(self, ev):
        if not self.selected:
            self.savedPen = self.pen()
        self.setPen(default_hover_pen)
        # self.sigHovered.emit()
        self.internal_pointer.highlight_spectra()
        ev.accept()

    def hoverLeaveEvent(self, ev):
        if self.selected:
            self.setPen(default_select_pen)
        else:
            self.setPen(self.savedPen)
        self.internal_pointer.unlight_spectra()
        # self.sigLeft.emit()
        ev.accept()

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            # self.sigClicked.emit(self.internal_pointer)
            if self.selected:
                self.selected = False
            else:
                self.selected = True
                self.setPen(default_select_pen)
                self.internal_pointer.select_spectra()

            ev.accept()
        else:
            ev.ignore()

# TODO implement the boundRect and shape for polygon:


class SelectablePolygon(SelectableMarker, QtWidgets.QGraphicsPolygonItem):
    """requires object for reference and QPolygonF"""

    def __init__(self, data, *args):
        QtGui.QGraphicsPolygonItem.__init__(self, *args)
        SelectableMarker.__init__(self, data, *args)


class SelectableRectangle(SelectableMarker, QtWidgets.QGraphicsRectItem):
    """requires object for reference and 4 points of bounding Rectangle:
     (left_top: x, y, width, height)"""

    def __init__(self, data, *args):
        self.geometry = QtCore.QRectF(*args)
        QtGui.QGraphicsRectItem.__init__(self, *args)
        SelectableMarker.__init__(self, data, *args)

    def boundingRect(self):
        return self.geometry

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path


class SelectableEllipse(SelectableMarker, QtWidgets.QGraphicsEllipseItem):
    """requires object for reference and 4 points of bounding Rectangle:
     (left_top: x, y, width, height)"""

    def __init__(self, data, *args):
        self.geometry = QtCore.QRectF(*args)
        QtGui.QGraphicsEllipseItem.__init__(self, *args)
        SelectableMarker.__init__(self, data, *args)

    def boundingRect(self):
        return self.geometry

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path


class SelectablePoint(SelectableMarker, QtWidgets.QGraphicsPathItem):
    # class selectablePoint(QtGui.QGraphicsPathItem):
    """requires object for reference and path item (the symbol):
     and QtGui.QPainterPath"""

    def __init__(self, data, *args):
        self.geometry = args[0]
        QtGui.QGraphicsPathItem.__init__(self, *args)
        SelectableMarker.__init__(self, data, *args)

    def boundingRect(self):
        return self.geometry.boundingRect()

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path
