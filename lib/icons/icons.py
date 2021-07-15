# -*- coding: utf-8 -*-
#
# it can be discussed that qrc could do better. but this
# handles the different themes (dark, light) and that logic would need
# anyway to be coded. Python can solve problems with absolute/relative paths on its own.

from os import path


class IconProvider:
    def __init__(self, widget):
        dark_mode = self.get_theme_mode(widget)
        self.dark_mode = None
        self.main_icon_path = path.dirname(__file__)
        self.icon_path = None
        self.set_dark_mode(dark_mode)

    def set_dark_mode(self, mode):
        if mode:
            self.dark_mode = True
            self.icon_path = path.join(self.main_icon_path, 'dark')
        else:
            self.dark_mode = False
            self.icon_path = path.join(self.main_icon_path, 'light')

    @staticmethod
    def get_theme_mode(qt_widget):
        """peak into pallete of given qt_widget and return
        True if text is lighter than background (dark_mode);
        False if reverse"""
        pallete = qt_widget.palette()
        w_lightness = pallete.window().color().lightness()
        wt_lightness = pallete.windowText().color().lightness()
        return wt_lightness > w_lightness

    def get_icon_path(self, filename, neutral=False):
        if neutral:
            return path.join(self.main_icon_path, filename)
        return path.join(self.icon_path, filename)
