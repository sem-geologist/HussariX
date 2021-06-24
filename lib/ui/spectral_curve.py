from pyqtgraph import PlotCurveItem


class SpectralCurveItem(PlotCurveItem):
    """Abstract SpectralCurveItem, which need to be imlemented
    for given datastructure representing spectra"""
    def set_spectral_data(self, x_mode=None, y_mode=None):
        """This function should do self.setData()"""
        raise NotImplementedError(
            'function set_spectral_data needs to be reimplemented in '
            'subclass of SpectralCurveItem')
        # x = None
        # y = None
        # self.setData(x, y)
