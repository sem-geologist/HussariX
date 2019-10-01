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

from struct import unpack
import numpy as np
from io import BytesIO
import os
from PyQt5 import QtCore
from copy import deepcopy


from datetime import datetime, timedelta

from enum import IntEnum

from ..generic import spectra

# ---------------- #
# helper functions #
# ---------------- #


def filetime_to_datetime(filetime):
    """convert retarded windows filetime to python/unix time."""
    return datetime(1601, 1, 1) + timedelta(microseconds=filetime / 10)


def mod_date(filename):
    """Return datetime of file last moddification"""
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)


def get_xtal(full_xtal_name):
    """get basic crystal name.
       example: get_xtal('LLIF') -> 'LIF'
    """
    for i in ['PC0', 'PC1', 'PC2', 'PC3', 'PET', 'TAP', 'LIF']:
        if i in full_xtal_name:
            return i


def read_c_hash_string(stream):
    """read the C# string and return python string.
    Requires stream in byte mode (e.g. BytesIO, open(filename)),
    with pointer at string preceeding string-lenght counter.
    """
    str_len = unpack('<I', stream.read(4))[0]
    return stream.read(str_len).decode()


version_error_str = ' '.join(['{0} version {1} was encountered at address {2}',
                              'which is not supported.'
                              'Aborting parsing of the file...'])


def eval_struct_version(stream, accepted=[], item='struct'):
    position = stream.tell()
    version = unpack('<I', stream.read(4))[0]
    if version not in accepted:
        raise NotImplementedError(
            version_error_str.format(item, hex(version), hex(position)))
    return version


# ---------------------------- #
# known or partly known enums: #
# ---------------------------- #


class FileType(IntEnum):
    WDS_SETUP = 1
    IMAGE_MAPPING_SETUP = 2
    CALIBRATION_SETUP = 3
    QUANTI_SETUP = 4
    # what is 5?
    WDS_RESULTS = 6
    IMAGE_MAPPING_RESULT = 7
    CALIBRATION_RESULT = 8
    QUANTI_RESULT = 9
    PEAK_OVERLAP_TABLE = 10


class XRayLines(IntEnum):
    Kβ, Kα = 1, 2
    Lγ4, Lγ3, Lγ2, Lγ = 3, 4, 5, 6
    Lβ9, Lβ10, Lβ7, Lβ2, Lβ6, Lβ3, Lβ4, Lβ = range(7, 15)
    Lα, Lν, Ll = 15, 16, 17
    Mγ, Mβ, Mα, Mζ, Mζ2 = 18, 19, 20, 21, 22
    M1N2, M1N3, M2N1, M2N4, M2O4, M3N1, M3N4, M3O1, M3O4, M4O2 = range(23, 33)
    sKα1, sKα2, sKα3, sKα4, sKα5, sKα6, sKβ1 = range(100, 107)


class AtomicNumber(IntEnum):
    n, H, He, Li, Be, B, C, N, O = range(0, 9)
    F, Ne, Na, Mg, Al, Si, P, S, Cl = range(9, 18)
    Ar, K, Ca, Sc, Ti, V, Cr, Mn, Fe = range(18, 27)
    Co, Ni, Cu, Zn, Ga, Ge, As, Se, Br = range(27, 36)
    Kr, Rb, Sr,  Y, Zr, Nb, Mo, Tc, Ru = range(36, 45)
    Rh, Pd, Ag, Cd, In, Sn, Sb, Te, I = range(45, 54)
    Xe, Cs, Ba, La, Ce, Pr, Nd, Pm, Sm = range(54, 63)
    Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu = range(63, 72)
    Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg = range(72, 81)
    Tl, Pb, Bi, Po, At, Rn, Fr, Ra, Ac = range(81, 90)
    Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf = range(90, 99)
    Es, Fm, Md, No, Lr = range(99, 104)


class DatasetDefType(IntEnum):
    POINT, LINE_STAGE, LINE_BEAM = 0, 1, 2
    GRID_STAGE, GRID_BEAM, POLYGON_MASKED_STAGE_RASTER = 3, 4, 5
    POLYGON_MASKED_BEAM_RASTER, FREE_POINTS = 6, 7


class ResElemSource(IntEnum):
    # Kudos to Cameca for exposing those through drop-down menu
    Undefined, WDS, EDS, VIDEO = 0, 1, 2, 3
    Other, QtiDiff, QtiStoch, QtiMatrix = 4, 5, 6, 7
    ImOve, ImPhcl, ImPhid, ImQtiWdsBkgdMeas = 8, 9, 10, 11
    ImQtiWdsBkgdComputed, ImQtiWt, ImQtiAt, ImQtiSum = 12, 13, 14, 15
    ImQtiAge, ImQtiOxy, ImXonVideo, Camera = 16, 17, 18, 19
    WdsComputed, EdsBkgd = 20, 21


class VideoSignalType(IntEnum):
    SE = 0
    Fara = 1
    BSE = 0x02  # 0x02 as BSE is on SX100, but not on SXFive
    Abs = 3
    # 4?
    CL = 5
    BSE_Z = 0x3F000002  # BSE Z on SxFive
    BSE_T = 0x38070002  # all signal types with lowest bits as 0x02 are BSE?
    # more BSE ?


class ArrayDataType(IntEnum):
    UINT8 = 0
    # 1-6 ??? dafck? int8, uint16, int16, uint32, int32 ?
    FLOAT32 = 7
    RGBX = 8


# ------------------------ #
# Basic cameca file class: #
# ------------------------ #


class CamecaDataFile(object):
    def open_the_file(self, filename):
        self.filename = filename
        with open(filename, 'br') as fn:
            # file bytes
            fbio = BytesIO()
            fbio.write(fn.read())
        self.file_basename = os.path.basename(filename).rsplit('.', 1)[0]
        fbio.seek(0)
        return fbio

    def _read_the_header(self, fbio):
        """parse the header data into base cameca object atributes
        arguments:
        fbio -- file BytesIO object
        """
        a, b = unpack('<B3s', fbio.read(4))
        if b != b'fxs':
            raise IOError('The file is not a cameca peaksight software file')
        self.cameca_bin_file_type = a
        self.file_type = FileType(a)
        self.file_version = eval_struct_version(fbio, [3, 4, 5], 'file')
        self.file_comment = read_c_hash_string(fbio)
        fbio.seek(0x1C, 1)  # some spacer with unknown values
        n_changes = unpack('<i', fbio.read(4))[0]
        self.changes = []
        for i in range(n_changes):
            filetime, change_len = unpack('<Qi', fbio.read(12))
            comment = fbio.read(change_len).decode()
            self.changes.append([filetime_to_datetime(filetime),
                                 comment])
        if self.file_version >= 4:
            fbio.seek(0x08, 1)  # some additional spacer
        if self.file_version >= 5:
            fbio.seek(0x08, 1)  # something, common value=40.0

    def check_the_dataset_container(self, fbio):
        self.dataset_container_version = eval_struct_version(
            fbio, accepted=[0x0B, 0x0D], item='dataset struct')
        keys = ['focus_freq', 'verify_xtal_after_flip',
                'verify_xtal_before_start', 'bgnd_meas_every_nth',
                'waiting_time']
        values = unpack('<i?3x?3x2i', fbio.read(20))
        self.global_opts = dict(zip(keys, values))

    def parse_datasets(self, fbio):
        # print('n_item_offset: ', fbio.tell())
        self.number_of_items = unpack('<i', fbio.read(4))[0]
        self.datasets = []
        for i in range(self.number_of_items):
            self.datasets.append(self._parse_data_set(fbio))

    def aggregate(self):
        unique_comment = set([i.comment for i in self.datasets])
        agg_data = [sum(filter(lambda x: x.comment == i, self.datasets))
                    for i in unique_comment]
        self.datasets = agg_data

    def _parse_data_set(self, fbio):
        "Abstract method"
        raise NotImplementedError("This is an abstract method")


# --------------------------  #
# Derived data file classes:  #
# --------------------------  #


class CamecaWDS(CamecaDataFile):
    def __init__(self, filename):
        fbio = self.open_the_file(filename)
        self._read_the_header(fbio)
        if self.cameca_bin_file_type != FileType.WDS_RESULTS:
            raise IOError(' '.join(['The file header shows it is not WDS',
                                    'file, but',
                                    self.file_type]))
        self.check_the_dataset_container(fbio)
        self.parse_datasets(fbio)

    def _parse_data_set(self, fbio):
        return WDSDatasetItem(fbio, self)


class CamecaImage(CamecaDataFile):

    def __init__(self, filename):
        fbio = self.open_the_file(filename)
        self._read_the_header(fbio)
        if self.cameca_bin_file_type != FileType.IMAGE_MAPPING_RESULT:
            raise IOError(' '.join(['The file header shows it is not',
                                    'Cameca Image file, but',
                                    str(self.file_type)]))
        self.check_the_dataset_container(fbio)
        self.parse_datasets(fbio)

    def _parse_data_set(self, fbio):
        return ImageDatasetItem(fbio, self)


class CamecaQuanti(CamecaDataFile):

    def __init__(self, filename):
        fbio = self.open_the_file(filename)
        self._read_the_header(fbio)
        if self.cameca_bin_file_type != FileType.QUANTI_RESULT:
            raise IOError(
                ' '.join(['The file header shows it is not Quanti',
                          'file, but',
                          self.file_type]))
        self.check_the_dataset_container(fbio)
        self.parse_datasets(fbio)

    def _parse_data_set(self, fbio):
        return QuantiDatasetItem(fbio, self)


# ---------------- #
# Dataset classes: #
# ---------------- #


class DatasetItem(object):
    """Basic Dataset Item class"""
    # keys and struct str for first 68 bytes:
    item_structs = {ResElemSource.WDS.value: [[
                        'atom_number', 'line', 'order', 'spect_no',
                        'xtal4', '2D', 'K', 'unkwn4',
                        'HV', 'current', 'peak_pos',
                        'bias', 'gain', 'dtime', 'blin',
                        'window', 'mode'], '<4I4s2fi2f7i'],
                    ResElemSource.ImQtiWdsBkgdMeas.value: [[
                        'atom_number', 'line', 'order', 'spect_no',
                        'xtal4', '2D', 'K', 'unkwn4',
                        'HV', 'current', 'peak_pos',
                        'bias', 'gain', 'dtime', 'blin',
                        'window', 'mode'], '<4I4s2fi2f7i'],
                    ResElemSource.EDS.value: [[
                        'atom_number', 'line', 'HV', 'current'],
                            '<2I24x2f28x'],
                    ResElemSource.EdsBkgd.value: [[
                        'atom_number', 'line', 'HV', 'current'],
                            '<2I24x2f28x'],
                    ResElemSource.VIDEO.value: [[
                        'channel', 'signal', 'HV', 'current'],
                              '<2I24x2f28x'],
                    ResElemSource.QtiStoch.value: [['atom_number'],
                                                   '<I64x'],
                    ResElemSource.QtiMatrix.value: [['atom_number'],
                                                    '<I64x'],
                    'etc': [['par1', 'par2', 'par3', 'par4', 'par5',
                             'par6', 'par6', 'par7', 'HV', 'current',
                             'par10', 'par11', 'par11', 'par12', 'par13',
                             'pra14', 'par15', 'par16', 'par17'],
                            '<4I4s2fi2f7i']}

    def __init__(self, fbio, parent):
        self.parent = parent
        self.dataset_struct_version = eval_struct_version(
            fbio, accepted=[0x11, 0x12])
        field_names = ['definition_node', 'x_axis', 'y_axis', 'beam_x',
                       'beam_y', 'resolution_x', 'resolution_y', 'width',
                       'height']
        values = unpack('<5i2f2i', fbio.read(36))
        self.metadata = dict(zip(field_names, values))
        fbio.seek(12, 1)  # skip some unknown values
        field_names = ['accumulation_times', 'dwell_time', 'unkn_val1']
        values = unpack('<ifi', fbio.read(12))
        self.metadata.update(dict(zip(field_names, values)))
        self.metadata['z_axis'] = list(unpack('<49i', fbio.read(49*4)))
        fbio.seek(40, 1)  # skip dataset config flags:
        """ TODO:
        4bytes - unknown
        4bytes - unknown
        uint32 - beam_measurement_freq
        4bytes - unknown
        4bytes - unknown
        4bytes - unknown
        4bytes - unknown
        uint32 - focus_freq
        uint32 - load_setup_every_nth
        4bytes - unknown
        """
        self.metadata['condition_file'] = read_c_hash_string(fbio)
        self.n_of_items = unpack('<i', fbio.read(4))[0]
        self.items = [self.read_item(fbio) for i in range(self.n_of_items)]
        self.comment = read_c_hash_string(fbio)

    @classmethod
    def read_start_of_item(cls, fbio):
        """begining of data item is very similar in-between data types"""
        # print('start_of_item at:', fbio.tell())
        item = {}
        item['struct_v'] = eval_struct_version(fbio, accepted=[3, ])
        stype = eval_struct_version(fbio, accepted=list(ResElemSource),
                                    item='source type')
        item['source_type'] = stype
        if stype in cls.item_structs:
            field_names, fmt_struct = cls.item_structs[stype]
        else:
            field_names, fmt_struct = cls.item_structs['etc']
        values = unpack(fmt_struct, fbio.read(68))
        item.update(dict(zip(field_names, values)))
        fbio.seek(16, 1)  # skip junk; TODO Is this shit of dynamic lenght?
        for i in range(unpack('<i', fbio.read(4))[0]):
            fbio.seek(12, 1)  # skip more junk
        return item

    @staticmethod
    def parse_outer_metadata(fbio, coordinates=False):
        version = eval_struct_version(fbio, [5, 6])
        dt = unpack('<Q', fbio.read(8))[0]
        item = {'version': version,
                'datetime': filetime_to_datetime(dt)}
        if coordinates:
            keys = ['x_axis', 'y_axis', 'z_axis']
            values = unpack('<3f', fbio.read(12))
            item.update(dict(zip(keys, values)))
        else:
            fbio.seek(12, 1)
        if version == 5:
            fbio.seek(76, 1)
        elif version == 6:
            fbio.seek(100, 1)
        return item

    def read_item(self, fbio):
        "Abstract method"
        raise NotImplementedError("This is abstract method")


class ImageDatasetItem(DatasetItem):
    img_data_t = {ArrayDataType.UINT8: np.dtype('u1'),      # uint8
                  # uint16?, int16?, uint32?, int32?
                  # what can fill 1-6 positions?
                  ArrayDataType.FLOAT32: np.dtype('f4'),    # float32
                  ArrayDataType.RGBX: np.dtype('4u1')       # RGB(X) -> RGBA
                  # other uint64, float64??
                  }

    def __init__(self, fbio, parent=None):
        DatasetItem.__init__(self, fbio, parent)
        # skip unknown data
        if self.dataset_struct_version == 0x11:
            fbio.seek(164, 1)
        elif self.dataset_struct_version == 0x12:
            fbio.seek(168, 1)
        self.ref_data = self.parse_outer_metadata(fbio)
        fbio.seek(52, 1)
        # skip additional junk for image:
        fbio.seek(28, 1)
        read_c_hash_string(fbio)  # some crap
        fbio.seek(309, 1)

    def read_item(self, fbio):
        item = self.read_start_of_item(fbio)
        data_struct_version = eval_struct_version(fbio, accepted=[5])
        field_names = ['definition_node', 'x_axis', 'y_axis', 'beam_x',
                       'beam_y', 'resolution_x', 'resolution_y', 'width',
                       'height', 'z_axis', 'img_cameca_dtype', 'dwell_time']
        print('item_definition starts at:', fbio.tell())
        values = unpack('<5i2f2I2if', fbio.read(48))
        item.update(dict(zip(field_names, values)))
        # skip section of three values 0,255.0,0 or 0,0, 255.0;
        # as dtype=3f? grey levels?
        if item['definition_node'] not in [DatasetDefType.LINE_BEAM,
                                           DatasetDefType.LINE_STAGE]:
            item['accumulation_n'], item['data_size'] = unpack('<I4xI12x',
                                                               fbio.read(24))
            item['data_size'] -= 12
        else:
            item['data_size'] = unpack('<4xI', fbio.read(8))[0]
        print('array starts at:', fbio.tell())
        self.read_array(fbio, item)
        print('position after data:', fbio.tell())
        fbio.seek(56, 1)  # skip unknown
        item['lut_name'] = read_c_hash_string(fbio)
        item['signal_name'] = read_c_hash_string(fbio)
        fbio.seek(52, 1)  # skip unknown
        item['img_rotation'] = unpack('<f', fbio.read(4))[0]
        fbio.seek(8, 1)  # skip unknown junk
        return item

    def read_array(self, fbio, item):
        data_size = item['data_size']
        print('array_size:', data_size)
        pixels = item['width'] * item['height']
        dtype = self.img_data_t[item['img_cameca_dtype']]
        print('estimated size of one slice: ', pixels * dtype.itemsize)
        print(item['width'], item['height'], dtype.itemsize)
        if item['definition_node'] in [DatasetDefType.LINE_BEAM,
                                       DatasetDefType.LINE_STAGE]:
            item['data'] = np.fromstring(fbio.read(pixels * dtype.itemsize),
                                         dtype=dtype)
        else:
            item['data'] = np.fromstring(fbio.read(pixels * dtype.itemsize),
                                         dtype=dtype * item['width'])
            if item['img_cameca_dtype'] == ArrayDataType.FLOAT32:
                print('reading subsets: ', item['accumulation_n'])
                imgs = []
                # When signal is Video, it fills much more subsets
                # than declared with accumulation_n!;
                # the only safe way is deduce number of  arrays
                # programaticaly
                for i in range(data_size // (pixels * dtype.itemsize) - 1):
                    imgs.append(
                        np.fromstring(fbio.read(pixels * dtype.itemsize),
                                      dtype=dtype * item['width']))
                item['subcounting_data'] = imgs
            if item['img_cameca_dtype'] == ArrayDataType.RGBX:
                item['data'][:, :, 3] = 255  # set X into A - an alpha channel


class WDSDatasetItem(DatasetItem):
    def __init__(self, fbio, parent=None):
        DatasetItem.__init__(self, fbio, parent)
        # skip unknown:
        if self.dataset_struct_version == 0x11:
            fbio.seek(164, 1)
        elif self.dataset_struct_version == 0x12:
            fbio.seek(168, 1)
        self.ref_data = self.parse_outer_metadata(fbio)
        fbio.seek(52, 1)
        self.enabled = 0

    def read_item(self, fbio):
        item = self.read_start_of_item(fbio)
        field_names = ['data_struct_version', 'wds_start_pos',
                       'steps', 'step_size', 'dwell_time',
                       'beam_size?', 'data_array_size']
        values = unpack('<3I2f2I', fbio.read(28))
        item.update(dict(zip(field_names, values)))
        size = item['data_array_size']
        item['data'] = np.fromstring(fbio.read(size), dtype=np.float32)
        fbio.seek(4, 1)  # skip some unknown value/flag
        item['signal_name'] = read_c_hash_string(fbio)
        fbio.seek(104, 1)  # skip some unknown values/flags
        item['annotated_lines'] = self.read_line_table(fbio)
        fbio.seek(8, 1)  # skip some unknown values/flags
        return item

    def __add__(self, other):
        if len(self.items) != len(other.items):
            raise TypeError("Can't add those itmes, as they have different number of spectras")
        new = deepcopy(self)
        n_items = len(self.items)
        for i in range(n_items):
            new.items[i]['data'] = self.items[i]['data'] + other.items[i]['data']
        return new

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __repr__(self):
        return 'WDSDataItem; comment: {}'.format(self.comment)

    @staticmethod
    def read_line_table(fbio):
        n_lines = unpack('<I', fbio.read(4))[0]
        lines = [list(unpack('<5I', fbio.read(20))) for i in range(n_lines)]
        return lines


class QuantiDatasetItem(DatasetItem):
    # TODO:
    quanti_keys = {0x0A: ['fara_meas', 'peak_cnt', 'peak_time',
                          'bkg_cnt', 'bkg1_cnt', 'bkg2_cnt',
                          'Ix/Istd', 'Ix/Ipure', 'weight',
                          'n_weight', 'atomic', 'oxides',
                          'det_lim', 'std_dev', 'Z', 'A', 'F',  # ...<17f
                          'non_def1', 'non_def2', 'non_def3',   # IfI
                          'peak_pulses', 'bkg1_pulses', 'bkg2_pulses']}  # 3I
    quanti_structs = {0x0A: '<17fIfI3I'}

    def __init__(self, fbio, parent=None):
        DatasetItem.__init__(self, fbio, parent)

    def read_item(self, fbio):
        item = self.read_start_of_item(fbio)
        item['item_container_v'] = eval_struct_version(fbio, [0x0E, 0x0F])
        fbio.seek(4, 1)  # skip some unknown value/flag
        item['dts_data_size'] = unpack('<I', fbio.read(4))[0]
        item['intern_cont_v'] = eval_struct_version(fbio, [0x0A, 0x0B])


class CamecaWDSListModel(QtCore.QAbstractListModel):
    def __init__(self, cameca_wds, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.collection = cameca_wds

    def rowCount(self, parent):
        try:
            return len(self.collection.datasets)
        except AttributeError:   # empty sample container
            return 0

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.collection.datasets[index.row()].comment
        if role == QtCore.Qt.CheckStateRole:
            return self.collection.datasets[index.row()].enabled

    def setData(self, index, value, role):
        if not index.isValid() or role != QtCore.Qt.CheckStateRole:
            return False
        self.collection.datasets[index.row()].enabled = value
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable |\
            QtCore.Qt.ItemIsUserCheckable
