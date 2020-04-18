
from PyQt5 import QtCore, QtGui

import pyqtgraph as pg

default_pen = pg.mkPen((255, 255, 75), width=2)
default_hover_pen = pg.mkPen((255, 50, 50), width=2)
default_select_pen = pg.mkPen((255, 255, 255), width=2)


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
            # ??? Why needs to be Top, it is intended to bound Bottom:
            new_rect.moveTop(0.0)
            self.setRange(new_rect, padding=0)


class CustomAxisItem(pg.AxisItem):
    """
    This class draws a rectangular area. Right-clicking inside the area will
    raise a custom context menu which also includes the context menus of
    its parents.
    """
    def __init__(self, *args, **kwargs):
        # menu creation is deferred because it is expensive and often
        # the user will never see the menu anyway.
        self.menu = None

        # note that the use of super() is often avoided because Qt does not
        # allow to inherit from multiple QObject subclasses.
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.energyButton = QtGui.QRadioButton('Energy')
        self.thetaButton = QtGui.QRadioButton('sin(θ)')

    # On right-click, raise the context menu
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            if self.raiseContextMenu(ev):
                ev.accept()

    def raiseContextMenu(self, ev):
        menu = self.getContextMenus()

        # Let the scene add on to the end of our context menu
        # (this is optional)
        # menu = self.scene().addParentContextMenus(self, menu, ev)

        pos = ev.screenPos()
        menu.popup(QtCore.QPoint(pos.x(), pos.y()))
        return True

    # This method will be called when this item's _children_ want to raise
    # a context menu that includes their parents' menus.
    def getContextMenus(self, event=None):
        if self.menu is None:
            self.menu = QtGui.QMenu()
            self.menu.setTitle("axis options..")

            scale = QtGui.QWidgetAction(self.menu)
            groupBox = QtGui.QGroupBox()
            verticalLayout = QtGui.QVBoxLayout(groupBox)
            self.energyButton.setParent(groupBox)
            verticalLayout.addWidget(self.energyButton)
            self.thetaButton.setParent(groupBox)
            verticalLayout.addWidget(self.thetaButton)
            scale.setDefaultWidget(groupBox)
            self.menu.addAction(scale)
            self.menu.scale = scale
            self.menu.groupBox = groupBox
        return self.menu


class selectableMarker:

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


class selectablePolygon(selectableMarker, QtGui.QGraphicsPolygonItem):
    """requires object for reference and QPolygonF"""

    def __init__(self, data, *args):
        QtGui.QGraphicsPolygonItem.__init__(self, *args)
        selectableMarker.__init__(self, data, *args)


class selectableRectangle(selectableMarker, QtGui.QGraphicsRectItem):
    """requires object for reference and 4 points of bounding Rectangle:
     (left_top: x, y, width, height)"""

    def __init__(self, data, *args):
        self.geometry = QtCore.QRectF(*args)
        QtGui.QGraphicsRectItem.__init__(self, *args)
        selectableMarker.__init__(self, data, *args)

    def boundingRect(self):
        return self.geometry

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path


class selectableEllipse(selectableMarker, QtGui.QGraphicsEllipseItem):
    """requires object for reference and 4 points of bounding Rectangle:
     (left_top: x, y, width, height)"""

    def __init__(self, data, *args):
        self.geometry = QtCore.QRectF(*args)
        QtGui.QGraphicsEllipseItem.__init__(self, *args)
        selectableMarker.__init__(self, data, *args)

    def boundingRect(self):
        return self.geometry

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path


class selectablePoint(selectableMarker, QtGui.QGraphicsPathItem):
    # class selectablePoint(QtGui.QGraphicsPathItem):
    """requires object for reference and path item (the symbol):
     and QtGui.QPainterPath"""

    def __init__(self, data, *args):
        self.geometry = args[0]
        QtGui.QGraphicsPathItem.__init__(self, *args)
        selectableMarker.__init__(self, data, *args)

    def boundingRect(self):
        return self.geometry.boundingRect()

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path
