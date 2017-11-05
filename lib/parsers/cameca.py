"""
copyright 2016 Petras Jokubauskas <klavishas@gmail.com>

This library reads data produced by Cameca(TM) Peaksight(TM) software.

It is developed independantly from Cameca or Ametek inc.
Development is based on the RE of binary data formats which
is legaly considered Fair Use in the EU.

LICENSE:

Cameca SX parser library is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cameca SX parser library is distributed in the hope that it will be useful,
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

from datetime import datetime, timedelta


def filetime_to_datetime(filetime):
    """Return recalculated windows filetime to unix time."""
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
    str_len = unpack('<i', stream.read(4))[0]
    return stream.read(str_len).decode()


class CamecaBase(object):
    cam_file_types = {1: 'WDS setup',
                      2: 'Image/maping setup',
                      3: 'Calibration setup',
                      4: 'Quanti setup',
                      5: 'unknown',  # What is this???
                      6: 'WDS results',
                      7: 'Image/maping results',
                      8: 'Calibration results',
                      9: 'Quanti results',
                      10: 'Peak overlap table'}
    
    cameca_lines = {1: 'Kβ', 2: 'Kα',
                    3: 'Lγ4', 4:'Lγ3', 5: 'Lγ2', 6: 'Lγ',
                    7: 'Lβ9', 8: 'Lβ10', 9: 'Lβ7', 10: 'Lβ2',
                    11: 'Lβ6', 12: 'Lβ3', 13: 'Lβ4', 14: 'Lβ',
                    15: 'Lα', 16: 'Lν', 17: 'Ll',
                    18: 'Mγ', 19: 'Mβ', 20: 'Mα', 21: 'Mζ', 22: 'Mζ2',
                    23: 'M1N2', 24: 'M1N3', 25: 'M2N1', 26: 'M2N4',
                    27: 'M2O4', 28: 'M3N1', 29: 'M3N4', 30: 'M3O1',
                    31: 'M3O4', 32: 'M4O2',
                    100: 'sKα1', 101: 'sKα2', 102: 'sKα3', 103: 'sKα4',
                    104: 'sKα5', 105: 'sKα6', 106: 'sKβ1'}
    
    #it could be used lists, however, dict is much faster to lookup
    cam_elements = {0: 'n', 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B',
                    6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne', 11: 'Na',
                    12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S',
                    17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca', 21: 'Sc',
                    22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe',
                    27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn', 31: 'Ga',
                    32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr',
                    37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb',
                    42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd',
                    47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn', 51: 'Sb',
                    52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba',
                    57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd', 61: 'Pm',
                    62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy',
                    67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', 71: 'Lu',
                    72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os',
                    77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg', 81: 'Tl',
                    82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn',
                    87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th', 91: 'Pa',
                    92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm',
                    97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm', 101: 'Md',
                    102: 'No', 103: 'Lr'}
    
    dts_def_types = {0: 'point', 1: 'line stage', 2: 'line beam',
                     3: 'grid stage', 4: 'grid beam', 5: 'polygon stage',
                     6: 'polygon beam', 7: 'free points'}

    @classmethod
    def to_definition_type(cls, node_type):
        """return the string representation of cameca aquisition definition"""
        return cls.dts_def_types[node_type]
    
    @classmethod
    def to_type(cls, sx_type):
        """return the string representation of cameca file type
        from given integer code"""
        return cls.cam_file_types[sx_type]
        
    @classmethod
    def to_element(cls, number):
        """return atom name for given atom number"""
        return cls.cam_elements[number]
  
    @classmethod
    def to_line(cls, number):
        """ return stringof x-ray line from given cameca int code"""
        return cls.cameca_lines[number]
    
    def open_the_file(self, filename):
        self.filename = filename
        with open(filename, 'br') as fn:
            #file bytes 
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
        a, b, c, d = unpack('<B3sii', fbio.read(12))
        if b != b'fxs':
            raise IOError('The file is not a cameca peaksight software file')
        self.cameca_bin_file_type = a
        self.file_type = self.to_type(a)
        self.file_version = c
        self.file_comment = fbio.read(d).decode()
        fbio.seek(0x1C, 1)  # some spacer with unknown values
        n_changes = unpack('<i', fbio.read(4))[0]
        self.changes = []
        for i in range(n_changes):
            filetime, change_len = unpack('<Qi',fbio.read(12))
            comment = fbio.read(change_len).decode()
            self.changes.append([filetime_to_datetime(filetime),
                                 comment])
        if self.file_version not in [3, 4]:  # not supported version:
            raise IOError(''.join(['Only file versions of 3 and 4',
                                   'is supported, this file is version ',
                                   str(self.file_version)]))
        if self.file_version == 4:
            fbio.seek(0x08, 1)  # some additional spacer


class CamecaDataFile(CamecaBase):

    def check_the_dataset_container(self, fbio):
        container_version = unpack('<i', fbio.read(4))[0]
        if container_version not in  [0x0B, 0x0D]:
            raise RuntimeError(' '.join([
                'unrecognised dataset structure version:',
                'instead of expected 0x0B or 0x0D, the value',
                str(container_version),
                'was encountered at address: ',
                str(fbio.tell() - 4)]))
        self.dataset_container_version = container_version
        fbio.seek(20, 1)  # skip some unknown junk

    def parse_datasets(self, fbio):
        print('n_item_offset: ', fbio.tell())
        self.number_of_items = unpack('<i', fbio.read(4))[0]
        self.datasets = []
        for i in range(self.number_of_items):
            self.datasets.append(self.parse_data_item(fbio))
            
    def parse_data_item(self, fbio):
        "Abstract method"
        raise NotImplementedError("This is abstract method")


class CamecaImage(CamecaDataFile):
    
    def __init__(self, filename):
        fbio = self.open_the_file(filename)
        self._read_the_header(fbio)
        if self.cameca_bin_file_type != 7:
            raise IOError(' '.join(['The file header shows it is not',
                                    'Cameca Image file, but',
                                    str(self.file_type)]))
        #fbio.seek(36, 1)  # skip junk
        #self.stage_x, self.stage_y, self.beam_x, self.beam_y,\
        #self.res, _, self.width, self.height = unpack('iiiiffII',fbio.read(8*4))
        #fbio.seek(552)
        #img_str = fbio.read(self.width*self.height)
        #self.img = np.fromstring(img_str, dtype=np.uint8).reshape(self.height, self.width)
        self.check_the_dataset_container(fbio)
        self.parse_datasets(fbio)
        
        def parse_data_item(self, fbio):
            return ImageDatasetItem(fbio, self)


class CamecaWDS(CamecaDataFile):
    def __init__(self, filename):
        fbio = self.open_the_file(filename)
        self._read_the_header(fbio)
        if self.cameca_bin_file_type != 6:
            raise IOError(' '.join(['The file header shows it is not WDS',
                                    'file, but',
                                    self.file_type]))
        self.check_the_dataset_container(fbio)
        self.parse_datasets(fbio)

    def parse_data_item(self, fbio):
        return WDSDatasetItem(fbio, self)


class DatasetItem(CamecaBase):
    
    result_source = {1: 'WDS',
                     2: 'EDS',
                     3: 'Video',
                     6: 'Stochiometry',
                     7: 'Matrix',
                     0x13: 'Camera'}
    
    """keys and struct str for first 68 bytes:"""
    item_structs = {'WDS' : [['atom_number',
                       'line', 'order', 'spect_no',
                       'xtal4', '2D', 'K', 'unkwn4',
                       'kV', 'current', 'peak_pos',
                       'bias', 'gain', 'dtime', 'blin',
                       'window', 'mode'], '<4I4s2fi2f7i'],
                    'EDS': [['atom_number', 'line', 'kV', 'current'],
                            '<2I24x2f28x'],
                    'Video': [['channel', 'signal', 'kV', 'current'],
                              '<2I24x2f28x'],
                    'Stochiometry': [['atom_number'], '<I64x'],
                    'Matrix': [['atom_number'], '<I64x']}
    
    def __init__(self, fbio, parent):
        self.parent = parent
        struct_type = unpack('<i', fbio.read(4))[0]
        if struct_type not in  [0x11, 0x12]:
            raise IOError(' '.join(['The file reader expected the item with',
                                    'struct 0x11 or 0x12, not',
                                    str(struct_type),
                                    'at address:',
                                    str(fbio.tell()-4)]))
        self.struct_head = struct_type
        field_names = ['definition_node','x_axis', 'y_axis', 'beam_x', 'beam_y',
                       'resolution_x', 'resolution_y', 'width', 'height']
        values = unpack('<5i2f2i', fbio.read(36))
        self.metadata = dict(zip(field_names, values))
        fbio.seek(12, 1) # skip some unknown values
        field_names = ['accumulation_times', 'dwell_time']
        values = unpack('<if', fbio.read(8))
        self.metadata.update(dict(zip(field_names, values)))
        fbio.seek(4, 1) # skip some unknown values
        self.metadata['z_axis'] = list(unpack('<49i', fbio.read(49*4)))
        fbio.seek(40, 1) # skip some unknown flags
        self.metadata['condition_file'] = read_c_hash_string(fbio)

    @classmethod
    def to_result_source(cls, num_repr):
        """return the the string representation of cameca result source"""
        return cls.result_source[num_repr]

    @classmethod
    def read_start_of_item(cls, fbio):
        """begining of data item is very similar in-between data types"""
        field_names = ['struct_version', 'source_type']
        values = unpack('<2i', fbio.read(8))
        if values[0] != 3:
            raise NotImplementedError(' '.join(['Parsing item struct of vers.',
                                    str(values[0]),
                                    'is not implemented. ']))
        if values[1] not in cls.result_source:
            raise NotImplementedError(' '.join(['Item of source type:',
                                    str(values[1]),
                                    'is not implemented. ',
                                    'The error encountered at address: ',
                                    str(fbio.tell()-4)]))
        item = dict(zip(field_names, values))
        if values[1] != 0x13:
            field_names, fmt_struct = cls.item_structs[cls.to_result_source(values[1])]
            values = unpack(fmt_struct, fbio.read(68))
            item.update(dict(zip(field_names, values)))
        else:
            fbio.seek(68, 1)
        fbio.seek(16, 1)  # skip junk
        for i in range(unpack('<i', fbio.read(4))[0]):
            fbio.seek(12, 1)  # skip more junk
        return item


class ImageDatasetItem(DatasetItem):
    
    img_data_t = {0: np.uint8,  # uint16?, int16?, uint32?, int32?
                  7: np.float32,  # 32bit double
                  8: np.uint8}   # RGB; other uint64, float64?? 
    
    def __init__(self, fbio, parent=None):
        DatasetItem.__init__(self, fbio, parent)
        n_of_items = unpack('<i', fbio.read(4))[0]
        self.data = []
        for i in range(n_of_items):
            self.data.append(self.read_item(fbio))
        self.comment = read_c_hash_string(fbio)
        #TODO skip unknown data
    
    def read_item(self, fbio):
        item = self.read_start_of_item(fbio)
        #TODO
    

class WDSDatasetItem(DatasetItem):
    def __init__(self, fbio, parent=None):
        DatasetItem.__init__(self, fbio, parent)
        n_of_items = unpack('<i', fbio.read(4))[0]
        self.data = []
        for i in range(n_of_items):
            self.data.append(self.read_item(fbio))
        self.comment = read_c_hash_string(fbio)
        if self.struct_head == 0x12:
            fbio.seek(344, 1)  # skip unknown flags v4
        elif self.struct_head == 0x11:
            fbio.seek(316, 1)  # skip unknown flags v3
    
    def read_item(self, fbio):
        item = self.read_start_of_item(fbio)
        field_names = ['data_struct_version', 'wds_start_pos',
                       'steps', 'step_size', 'dwell_time',
                       'beam_size?', 'data_array_size']
        values = unpack('<3I2f2i', fbio.read(28))
        item.update(dict(zip(field_names, values)))
        size = item['data_array_size']
        item['data'] = np.fromstring(fbio.read(size), dtype=np.float32)
        fbio.seek(124, 1)  # skip some unknown values/flags
        return item


