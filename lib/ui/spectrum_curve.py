from pyqtgraph import PlotDataItem
from pyqtgraph import mkColor


class SpectrumCurveItem(PlotDataItem):
    """Abstract SpectralCurveItem, which need to be imlemented
    for given datastructure representing spectra"""
    def set_spectrum_data(self, x_mode=None, y_mode=None):
        """This function should do self.setData() and
           set self.x_ref and self.y_ref"""
        raise NotImplementedError(
            'function set_spectral_data needs to be reimplemented in '
            'subclass of SpectralCurveItem')
        # x = None
        # y = None
        # self.setData(x, y)
        # self.x_ref = x
        # self.y_ref = y

    def highlight(self):
        self._original_z = self.zValue()
        self.setZValue(100.)
        pen = self.opts['pen']
        p_color = pen.color()
        p_width = pen.width()
        p_color.setAlpha(150)
        self.setShadowPen(p_color, width=p_width + 4)
        p_color.setAlpha(255)
        pen.setColor(p_color)
        self.setPen(pen)

    def dehighlight(self, alpha=200):
        if hasattr(self, '_original_z'):
            self.setZValue(self._original_z)
        self.setShadowPen(None)
        self.set_curve_alpha(alpha)

    def set_curve_alpha(self, alpha):
        s_pen = self.opts['shadowPen']
        if (s_pen is not None) and (s_pen.style() != 0):
            return                  # if highlighted don't change alpha
        pen = self.opts['pen']
        color = pen.color()
        color.setAlpha(alpha)
        pen.setColor(color)
        self.setPen(pen)

    def set_curve_style(self, style):
        pen = self.opts['pen']
        pen.setStyle(style)
        self.setPen(pen)

    def set_curve_width(self, width):
        pen = self.opts['pen']
        pen.setWidth(width)
        self.setPen(pen)
        s_pen = self.opts['shadowPen']
        if (s_pen is not None) and (s_pen.style() != 0):
            s_pen.setWidth(width + 4)
            self.setShadowPen(s_pen)

    def set_curve_color(self, color):
        pen = self.opts['pen']
        alpha = pen.color().alpha()
        color.setAlpha(alpha)
        pen.setColor(color)
        self.setPen(pen)
        s_pen = self.opts['shadowPen']
        if (s_pen is not None) and (s_pen.style() != 0):
            s_color = mkColor(color)
            s_color.setAlpha(150)
            s_pen.setColor(s_color)
            self.setShadowPen(s_pen)
