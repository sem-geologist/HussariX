import numpy as np
import pyqtgraph as pg

HIGHLIGHT_PEN = pg.mkPen('y', width=2)
HIGHLIGHT_BRUSH = pg.mkBrush((75,255,255,75))
SELECT_BRUSH = pg.mkBrush((75,255,255))
NO_BRUSH = pg.mkBrush(None)

class Spectra:
    #required attributes:
    #self.x_scale, self.x_offset, self.data
    #self.marker,
    
    
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
                                        pen=pg.mkPen(125,255,255),    # TODO custom color schemes
                                        fillLevel=0,
                                        fillBrush=pg.mkBrush(None))
    
    def _setup_connections(self):
        self.sigHovered.connect(highlight_eds)
        self.sigLeft.connect(unlight_eds)
        
    def highlight_eds(self):
        self.original_pen = self.pg_curve.opts['pen']
        self.pg_curve.setPen(HIGHLIGHT_PEN)
        self.pg_curve.setBrush(HIGHLIGHT_BRUSH)
    
    def unlight_eds(self):
        self.pg_curve.setPen(self.original_pen)
        self.pg_curve.setBrush(NO_BRUSH)
        
    def select_eds(self):
        self.pg_curve.setBrush(SELECT_BRUSH)
            
    def set_curve_color(self, *colors):
        pass
    
    def change_marker_color(self, color):
        pass
