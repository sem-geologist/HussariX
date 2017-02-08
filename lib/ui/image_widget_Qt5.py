
#from PyQt5 import QtCore, Qt, QtGui, QtWidgets
import pyqtgraph as pg

from . import CustomWidgets as cw
from . import CustomPGWidgets as cpgw

BACKGROUND_COLOR = pg.mkColor(15,25,25)


class SEMImageGUI(cw.FullscreenableWidget):
    def __init__(self, parent=None, icon_size=None):
        cw.FullscreenableWidget.__init__(self, parent, icon_size)
        self.resize(550,550)
        self.pg_graphics_layout = pg.GraphicsLayoutWidget(self)
        self.setCentralWidget(self.pg_graphics_layout)
        self.canvas = self.pg_graphics_layout.addPlot()
        self.canvas.hideAxis('left')
        self.canvas.hideAxis('bottom')
        #self.canvas = self.pg_graphics_layout.addViewBox()
        self.pg_graphics_layout.setBackground(BACKGROUND_COLOR)
        #self.canvas.setBackgroundColor(BACKGROUND_COLOR)
        self.canvas.setAspectLocked(True)
        self.scale_bar = cpgw.CustomScaleBar(0.0001)
        self.scale_bar.setParentItem(self.canvas.vb)
        self.scale_bar.anchor((1, 1), (1, 1), offset=(-20, -20))
