import numpy as np
import pyqtgraph as pg

from ..ui import CustomPGWidgets as cpg

# TODO read those vals from config files
HIGHLIGHT_PEN = pg.mkPen('r', width=2)
HIGHLIGHT_BRUSH = pg.mkBrush((255, 255, 75, 50))
SELECT_BRUSH = pg.mkBrush((255, 255, 75))
NO_BRUSH = pg.mkBrush(None)

class Spectra:
    #required attributes:
    #self.x_offset, self.data, self.x_res
    #produces:
    #self.marker, self.x_scale,
    def __init__(self):
        self.selected = False
    
    def gen_scale(self):
        max_channel = self.x_res * self.chnl_cnt + self.x_offset
        self.x_scale = np.arange(self.x_offset, max_channel, self.x_res)
    
    def channel_at_e(self, energy):
        return int((energy - self.x_offset) // self.x_res)
    
    def e_at_channel(self, channel):
        return channel * self.res + self.x_offset
    
    def gen_pg_curve(self, starting_pos=0.02, cutoff=15.):
        st_chan = self.channel_at_e(starting_pos)
        if (st_chan < min(self.x_scale)) or (st_chan > max(self.x_scale)):
            st_chan = 0
        end_chan = self.channel_at_e(cutoff)
        if (end_chan < min(self.x_scale)) or (end_chan > max(self.x_scale)):
            end_chan = -1
        self.pg_curve = pg.PlotDataItem(self.x_scale[st_chan:end_chan],
                                        self.data[st_chan:end_chan],
                                        pen=pg.mkPen(255, 255, 125),    # TODO custom color schemes
                                        fillLevel=0,                  # prepare to be filled
                                        fillBrush=pg.mkBrush(None))   # but fill not
    
    def gen_marker(self, *args, marker_type=None):
        if marker_type == 'translated_marker':
            self.marker = cpg.selectablePoint(self, *args)
        elif marker_type == 'rectangle':
            self.marker = cpg.selectableRectangle(self, *args)
        elif marker_type == 'ellipse':
            self.marker = cpg.selectableEllipse(self, *args)
        elif marker_type == 'free_polygon':
            self.marker = cpg.selectablePolygon(self, *args)

    def highlight_spectra(self):
        self.original_pen = self.pg_curve.opts['pen']
        self.pg_curve.setPen(HIGHLIGHT_PEN)
        if not self.selected:
            self.pg_curve.setBrush(HIGHLIGHT_BRUSH)

    def unlight_spectra(self):
        self.pg_curve.setPen(self.original_pen)
        if not self.selected:
            self.pg_curve.setBrush(NO_BRUSH)

    def select_spectra(self):
        if self.selected:
            self.pg_curve.setBrush(NO_BRUSH)
            self.selected = False
        else:
            self.pg_curve.setBrush(SELECT_BRUSH)
            self.selected = True
 
    def set_curve_color(self, *colors):
        pass
    
    def change_marker_color(self, color):
        pass
