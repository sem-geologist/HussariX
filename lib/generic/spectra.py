import numpy as np
import pyqtgraph as pg

#TODO read those vals from config files
HIGHLIGHT_PEN = pg.mkPen('r', width=2)
HIGHLIGHT_BRUSH = pg.mkBrush((255,255,75,50))
SELECT_BRUSH = pg.mkBrush((255,255,75))
NO_BRUSH = pg.mkBrush(None)

class Spectra:
    #required attributes:
    #self.x_scale, self.x_offset, self.data
    #self.marker,
    def __init__(self):
        self.selected = False
    
    def _gen_scale(self, channels):
        max_channel = self.x_res * channels + self.x_offset
        self.x_scale = np.arange(self.x_offset, max_channel, self.x_res)
    
    def get_channel(self, energy):
        return int((energy - self.x_offset) // self.x_res)
    
    def gen_pg_curve(self, starting_pos=0.02, cuttof=15.):
        st_chan = self.get_channel(starting_pos)
        end_chan = self.get_channel(cuttof)
        self.pg_curve = pg.PlotDataItem(self.x_scale[st_chan:end_chan],
                                        self.data[st_chan:end_chan],
                                        pen=pg.mkPen(255,255,125),    # TODO custom color schemes
                                        fillLevel=0,                  # prepare to be filled
                                        fillBrush=pg.mkBrush(None))   # but fill not
    
    #def _setup_connections(self):
    #    self.sigHovered.connect(self.highlight_eds)
    #    self.sigLeft.connect(self.unlight_eds)
        
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
