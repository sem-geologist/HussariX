import csv
from os import path
from PyQt5.QtGui import QColor

__all__ = ['glasbey_light', 'glasbey_dark']


assets_path = path.join(path.dirname(__file__),
                        'glasbey_assets')

light_glasbey_path = path.join(assets_path,
                               'glasbey_bw_minc_20_maxl_70_n256.csv')
dark_glasbey_path = path.join(assets_path,
                              'glasbey_bw_minc_20_minl_30_n256.csv')

with open(light_glasbey_path, 'r') as l_fn:
    l_reader = csv.reader(l_fn, delimiter=",",
                          quoting=csv.QUOTE_NONNUMERIC)
    glasbey_dark = [QColor.fromRgbF(*i) for i in l_reader]

with open(dark_glasbey_path, 'r') as d_fn:
    d_reader = csv.reader(d_fn, delimiter=",",
                          quoting=csv.QUOTE_NONNUMERIC)
    glasbey_light = [QColor.fromRgbF(*i) for i in d_reader]
