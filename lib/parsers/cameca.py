"""
copyright 2016 Petras Jokubauskas <klavishas@gmail.com>

This library reads data produced by Cameca(TM) Peaksight(TM) software.

It is developed independantly from Cameca or Ametek inc.
Development is based on the RE of binary data formats which
is legaly considered Fair Use in the EU, particularly for
interoperability; see EU Directive 2009/24.

LICENSE:

This library is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with source code of this program,
or see <http://www.gnu.org/licenses/>.
"""

from enum import IntEnum
from functools import cached_property
import os
import numpy as np
from .cameca_ks.cameca import Cameca, KaitaiStream
from copy import copy

# import scipy.constants as sc
# x_ray_const = sc.h * sc.c / sc.eV * 1E12
# it would be crazy to depend on whole scipy just for a few constants
# here the hardcoded value useful for energy <-> wavelenght/sin(theta)
# transitions
# where 2d is given in Å (Cameca) and decimal is at that position
# for conversion to and from keV (for eV it would be 123.984...;
# for ev and 2d in nm it would be 12.3984...)
X_RAY_CONST = 1239841.9843320027

# ----------------------------------------------- #
# Type and Enum Overrides for Cameca sub-classes: #
# ----------------------------------------------- #


class XrayLine(IntEnum):
    "Cameca Xray Line enum"
    unknown = 0  # noqa
    Kβ, Kα = 1, 2
    Lγ4, Lγ3, Lγ2, Lγ = 3, 4, 5, 6
    Lβ9, Lβ10, Lβ7, Lβ2, Lβ6, Lβ3, Lβ4, Lβ = range(7, 15)
    Lα, Lν, Ll = 15, 16, 17  # noqa
    Mγ, Mβ, Mα, Mζ, Mζ2 = 18, 19, 20, 21, 22
    M1N2, M1N3, M2N1, M2N4, M2O4, M3N1, M3N4, M3O1, M3O4, M4O2 = range(23, 33)
    sKα1, sKα2, sKα3, sKα4, sKα5, sKα6, sKβ1 = range(100, 107)  # noqa

    @classmethod
    def _missing_(cls, _number):
        return cls(cls.unknown)


Cameca.XrayLine = XrayLine


class ElementT(Cameca.ElementT):
    _el_list = (
          "n H He "
          "Li Be B C N O F Ne "
          "Na Mg Al Si P S Cl Ar "
          "K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr "
          "Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe "
          "Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu "
          "Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
          "Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm".split())

    @cached_property
    def name(self):
        """element abbreviation"""
        return self._el_list[self.atomic_number]

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.atomic_number == other.atomic_number


Cameca.ElementT = ElementT


class WdsScanSignal(Cameca.WdsScanSignal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._y_recalc_cps = None
        self._y_orig_cps = None
        # Unfortunately this crap happens quite too often...
        # thus needs be checked (as it is always float32, thus multiple by 4).
        self.corrupted = self.steps * 4 != self.data_array_size

    @cached_property
    def x_100k_sin_theta(self):
        return self.wds_start_pos + np.arange(self.steps) * self.step_size

    @property
    def y_cps(self):
        if self._y_recalc_cps is not None:
            return self._y_recalc_cps
        if self._y_orig_cps is None:
            self._y_orig_cps = np.frombuffer(self.data, dtype=np.float32)
        return self._y_orig_cps

    @cached_property
    def y_cts(self):
        return self.y_cps / (
            self.y_cps *
            self._parent.signal_header.counter_setting.dead_time / 1E6 + 1)\
            / self.dwell_time

    @cached_property
    def y_cps_per_nA(self):
        return self.y_cps / self._parent.signal_header.beam_current

    def recalc_y_cps(self, function):
        """
        apply provided 'function' to alter cps for pile-up correction, so that
        calling .y_cps or .y_cps_per_nA would return pile-up corrected counts.

        Historically gas proportional counters are often interfaced with
        inadequately designed electronics, which is incapable to handle
        very high pulse rates and so called peak-pileup makes only a fraction
        of pulses be counted.
        Classical correction for dead-time is not enough and
        additional correction for pile-ups is needed.
        """
        if self._y_orig_cps is None:
            self.y_cps  # initialize
        self._y_recalc_cps = function(self._y_orig_cps)

    @cached_property
    def x_keV(self):
        head = self._parent.signal_header
        return X_RAY_CONST / head.two_d / (1 - head.k) / self.x_100k_sin_theta

    @cached_property
    def x_Å(self):
        head = self._parent.signal_header
        return self.x_100k_sin_theta * head.two_d * (1 - head.k) / 100000

    @cached_property
    def x_nm(self):
        return self.x_Å / 10


Cameca.WdsScanSignal = WdsScanSignal


class XraySignalHeader(Cameca.XraySignalHeader):
    def __eq__(self, other):
        return self.combi_string == other.combi_string

    def __hash__(self):
        return hash(self.combi_string)

    def __repr__(self):
        if self.element.atomic_number != 0:
            return '<{} {} on spect {}>'.format(self.element, self.xray_line,
                                                self.combi_string)
        return '<spect {}>'.format(self.combi_string)


Cameca.XraySignalHeader = XraySignalHeader

# --------------------------  #
# Customised File classes:    #
# --------------------------  #


class CamecaBase(Cameca):
    """Wrapper class of main Kaitai Parsing Class;
    The instance at instantiation loads provided file and
    use inherited parser."""

    def __init__(self, filename):
        self.mod_ts = os.path.getmtime(filename)
        with open(filename, "rb") as file_handle:
            kaitai_stream = KaitaiStream(file_handle)
            Cameca.__init__(self, kaitai_stream)
        self.file_basename = os.path.basename(filename).rsplit('.', 1)[0]
        # inject q_scruff for easy generation of Tree like QAbstractItemModel
        # without wrapper class.
        # and plotting interactions
        # add check_states for recursivly checkable object tree:
        self.q_checked_state = 0
        self.q_children = self.content.datasets
        self.q_row_count = self.content.n_of_datasets
        for i, dataset in enumerate(self.q_children):
            dataset.dts_number = i + 1
            dataset.q_row = i
            dataset.q_checked_state = 0
            dataset.q_parent = self
            dataset.q_row_count = 0
            dataset.q_children = []
            dataset.plot_items = []

    def min_max_timestamps(self):
        """traverse the struct and return min and max unix timestamps
        of datasets"""
        time_stamps = [dttspos.datetime.unix_timestamp
                       for dts in self.content.datasets
                       for dttspos in dts.extras.datetime_and_pos]
        return min(time_stamps), max(time_stamps)

    def get_used_setup_filenames(self):
        """return list with setup files, which marks different methods
        used during acquisition, albeit the results could methodologically
        differ if setup file was modified and overwritten in between
        datasets with same setup"""
        setups = [dts.header.setup_file_name.text
                  for dts in self.content.datasets]
        return list(set(setups))

    def get_datasets_by_setup(self, setup_fn):
        """return datasets which were acquired with provided setup name"""
        return [dts
                for dts in self.content.datasets
                if dts.header.setup_file_name.text == setup_fn]


class CamecaWDS(CamecaBase):
    """This class extends CamecaBase for WDS type of files
    Additionally it injects the object tree with some hierarchical
    references, so that construction of Qt (or other framework)
    hierarchical models would be easier (attributes with 'q_' prefix)"""

    @property
    def spect_xtal_unique_combinations(self):
        """get set of spectrometer/XTAL combinations used at least for one
        WDS spectra in the file"""
        # deepcopy would be better, but won't work here
        # due to circular references and kaitai stuff
        return {copy(i.signal_header)
                for dts in self.content.datasets
                for i in dts.items
                if i.signal_type == self.SignalSource.wds}


class CamecaImage(CamecaBase):
    pass


class CamecaQuanti(CamecaBase):
    pass


# class ImageDatasetItem(DatasetItem):
#    img_data_t = {ArrayDataType.UINT8: np.dtype('u1'),      # uint8
#                  # uint16?, int16?, uint32?, int32?
#                  # what can fill 1-6 positions?
#                  ArrayDataType.FLOAT32: np.dtype('f4'),    # float32
#                  ArrayDataType.RGBX: np.dtype('4u1')       # RGB(X) -> RGBA
#                  # other uint64, float64??
#                  }
#
#    def __init__(self, fbio, parent=None):
#        DatasetItem.__init__(self, fbio, parent)
#        # skip unknown data
#        if self.dataset_struct_version == 0x11:
#            fbio.seek(164, 1)
#        elif self.dataset_struct_version == 0x12:
#            fbio.seek(168, 1)
#        self.ref_data = self.parse_outer_metadata(fbio)
#        fbio.seek(52, 1)
#        # skip additional junk for image:
#        fbio.seek(28, 1)
#        read_c_hash_string(fbio)  # some crap
#        fbio.seek(309, 1)
#
#    def read_item(self, fbio):
#        item = self.read_start_of_item(fbio)
#        data_struct_version = eval_struct_version(fbio, accepted=[5])
#        field_names = ['definition_node', 'x_axis', 'y_axis', 'beam_x',
#                       'beam_y', 'resolution_x', 'resolution_y', 'width',
#                       'height', 'z_axis', 'img_cameca_dtype', 'dwell_time']
#        print('item_definition starts at:', fbio.tell())
#        values = unpack('<5i2f2I2if', fbio.read(48))
#        item.update(dict(zip(field_names, values)))
#        # skip section of three values 0,255.0,0 or 0,0, 255.0;
#        # as dtype=3f? grey levels?
#        if item['definition_node'] not in [DatasetDefType.LINE_BEAM,
#                                           DatasetDefType.LINE_STAGE]:
#            item['accumulation_n'], item['data_size'] = unpack('<I4xI12x',
#                                                               fbio.read(24))
#            item['data_size'] -= 12
#        else:
#            item['data_size'] = unpack('<4xI', fbio.read(8))[0]
#        print('array starts at:', fbio.tell())
#        self.read_array(fbio, item)
#        print('position after data:', fbio.tell())
#        fbio.seek(56, 1)  # skip unknown
#        item['lut_name'] = read_c_hash_string(fbio)
#        item['signal_name'] = read_c_hash_string(fbio)
#        fbio.seek(52, 1)  # skip unknown
#        item['img_rotation'] = unpack('<f', fbio.read(4))[0]
#        fbio.seek(8, 1)  # skip unknown junk
#        return item
#
#    def read_array(self, fbio, item):
#        data_size = item['data_size']
#        print('array_size:', data_size)
#        pixels = item['width'] * item['height']
#        dtype = self.img_data_t[item['img_cameca_dtype']]
#        print('estimated size of one slice: ', pixels * dtype.itemsize)
#        print(item['width'], item['height'], dtype.itemsize)
#        if item['definition_node'] in [DatasetDefType.LINE_BEAM,
#                                       DatasetDefType.LINE_STAGE]:
#            item['data'] = np.fromstring(fbio.read(pixels * dtype.itemsize),
#                                         dtype=dtype)
#        else:
#            item['data'] = np.fromstring(fbio.read(pixels * dtype.itemsize),
#                                         dtype=dtype * item['width'])
#            if item['img_cameca_dtype'] == ArrayDataType.FLOAT32:
#                print('reading subsets: ', item['accumulation_n'])
#                imgs = []
#                # When signal is Video, it fills much more subsets
#                # than declared with accumulation_n!;
#                # the only safe way is deduce number of  arrays
#                # programaticaly
#                for i in range(data_size // (pixels * dtype.itemsize) - 1):
#                    imgs.append(
#                        np.fromstring(fbio.read(pixels * dtype.itemsize),
#                                      dtype=dtype * item['width']))
#                item['subcounting_data'] = imgs
#            if item['img_cameca_dtype'] == ArrayDataType.RGBX:
#                item['data'][:, :, 3] = 255  # set X into A - an alpha channel
#
