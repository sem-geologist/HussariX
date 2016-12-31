# -*- coding: utf-8 -*-
#
# Copyright 2016 Petras Jokubauskas
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any project and source this library is coupled.
# If not, see <http://www.gnu.org/licenses/>.
#
# This python library subset provides read functionality of
#  Bruker bcf files.


from lxml import objectify
from .unsfs import SFS_reader
import codecs
from datetime import datetime
import numpy as np

import logging
_logger = logging.getLogger(__name__)

from . import unbcf_fast
from .bxml import BasicEDXSpectrum

import psutil
#import tables as tb


class Container(object):
    pass


class HyperHeader(object):
    """Wrap Bruker HyperMaping xml header into python object.

    Arguments:
    xml_str -- the uncompressed to be provided with extracted Header xml
    from bcf.

    Methods:
    estimate_map_channels, estimate_map_depth

    If Bcf is version 2, the bcf can contain stacks
    of hypermaps - thus header part  can contain multiply sum eds spectras
    and it's metadata per hypermap slice which can be selected using index.
    Bcf can record number of imagery from different
    imagining detectors (BSE, SEI, ARGUS, etc...): access to imagery
    is throught image index.
    """
    def __init__(self, xml_str):
        # Due to Delphi(TM) xml implementation literaly shits into xml,
        # we need lxml parser to be more forgiving (recover=True):
        oparser = objectify.makeparser(recover=True)
        root = objectify.fromstring(xml_str, parser=oparser).ClassInstance
        try:
            self.name = str(root.attrib['Name'])
        except KeyError:
            self.name = 'Undefinded'
            _logger.info("hypermap have no name. Giving it 'Undefined' name")
        self.datetime = datetime.strptime(' '.join([str(root.Header.Date),
                                                    str(root.Header.Time)]),
                                          "%d.%m.%Y %H:%M:%S")
        self.version = int(root.Header.FileVersion)
        #create containers:
        self.sem = Container()
        self.stage = Container()
        self.image = Container()
        #fill the sem and stage attributes:
        self._set_sem(root)
        self._set_image(root)
        self.elements = {}
        self._set_elements(root)
        self.line_counter = np.fromstring(str(root.LineCounter),
                                          dtype=np.uint16, sep=',')
        self.channel_count = int(root.ChCount)
        self.mapping_count = int(root.DetectorCount)
        self.channel_factors = {}
        self.spectra_data = {}
        self._set_sum_edx(root)

    def _set_sem(self, root):
        """wrap objectified xml part to class attributes for self.sem,
        self.stage and self.image.*_res
        """
        semData = root.xpath("ClassInstance[@Type='TRTSEMData']")[0]
        # sem acceleration voltage, working distance, magnification:
        self.sem.hv = float(semData.HV)  # in kV
        self.sem.wd = float(semData.WD)  # in mm
        self.sem.mag = float(semData.Mag)  # in times
        # image/hypermap resolution in um/pixel:
        self.image.x_res = float(semData.DX) / 1.0e6  # in meters
        self.image.y_res = float(semData.DY) / 1.0e6  # in meters
        semStageData = root.xpath("ClassInstance[@Type='TRTSEMStageData']")[0]
        # stage position data in um cast to m (that data anyway is not used
        # by hyperspy):
        try:
            self.stage.x = float(semStageData.X) / 1.0e6  # in meters
            self.stage.y = float(semStageData.Y) / 1.0e6  # in meters
        except AttributeError:
            self.stage.x = self.stage.y = None
        try:
            self.stage.z = float(semStageData.Z) / 1.0e6  # in meters
        except AttributeError:
            self.stage.z = None
        try:
            self.stage.rotation = float(semStageData.Rotation)  # in degrees
        except AttributeError:
            self.stage.rotation = None
        DSPConf = root.xpath("ClassInstance[@Type='TRTDSPConfiguration']")[0]
        self.stage.tilt_angle = float(DSPConf.TiltAngle)

    def _set_image(self, root):
        """Wrap objectified xml part with image to class attributes
        for self.image.
        """
        imageData = root.xpath("ClassInstance[@Type='TRTImageData']")[0]
        self.image.width = int(imageData.Width)  # in pixels
        self.image.height = int(imageData.Height)  # # in pixels
        self.image.plane_count = int(imageData.PlaneCount)
        self.multi_image = int(imageData.MultiImage)
        self.image.images = []
        for i in range(self.image.plane_count):
            img = imageData.xpath("Plane" + str(i))[0]
            raw = codecs.decode((img.Data.text).encode('ascii'), 'base64')
            array1 = np.fromstring(raw, dtype=np.uint16)
            if any(array1):
                temp_img = Container()
                temp_img.data = array1.reshape((self.image.height,
                                                self.image.width))
                temp_img.detector_name = str(img.Description.text)
                self.image.images.append(temp_img)

    def _set_elements(self, root):
        """wrap objectified xml part with selection of elements to
        self.elements list
        """
        try:
            elements = root.xpath("".join([
               "ClassInstance[@Type='TRTContainerClass']/ChildClassInstances",
               "/ClassInstance[@Type='TRTElementInformationList']",
               "/ClassInstance[@Type='TRTSpectrumRegionList']",
               "/ChildClassInstances"]))[0]
            for j in elements.xpath("ClassInstance[@Type='TRTSpectrumRegion']"):
                self.elements[j.attrib['Name']] = {'line': j.Line.pyval,
                                                   'energy': j.Energy.pyval,
                                                   'width': j.Width.pyval}
        except IndexError:
            _logger.info('no element selection present in the hypermap..')

    def _set_sum_edx(self, root):
        for i in range(self.mapping_count):
            self.channel_factors[i] = int(root.xpath("ChannelFactor" +
                                                                    str(i))[0])
            self.spectra_data[i] = BasicEDXSpectrum(root.xpath("SpectrumData" +
                                                       str(i))[0].ClassInstance)

    def estimate_map_channels(self, index=0):
        """estimate minimal size of energy axis so any spectra from any pixel
        would not be truncated.

        Arguments:
        index -- index of the map if multiply hypermaps are present
        in the same bcf.

        Returns:
        optimal channel number
        """
        bruker_hv_range = self.spectra_data[index].meta.amplification / 1000
        if self.sem.hv >= bruker_hv_range:
            return self.spectra_data[index].data.shape[0]
        else:
            return self.spectra_data[index].meta.energy_to_channel(self.sem.hv)

    def estimate_map_depth(self, index=0, downsample=1):
        """estimate minimal dtype of array using cumulative spectra
        of the all pixels so that no data would be truncated.

        Arguments:
        index -- index of the hypermap if multiply hypermaps are
        present in the same bcf. (default 0)
        downsample -- downsample factor (should be integer; default 1)
        for_numpy -- if estimation will be used in parsing using oure python
            and numpy inplace integer addition will be used, so the dtype
            should be signed; if cython implementation will be used (default),
            then any returned dtypes can be safely unsigned. (default False)

        Returns:
        numpy dtype large enought to use in final hypermap numpy array.

        The method estimates the value from sum eds spectra, dividing
        the maximum  energy pulse value from raster x and y and to be on the
        safe side multiplying by 2.
        """
        sum_eds = self.spectra_data[index].data
        #the most intensive peak is Bruker reference peak at 0kV:
        roof = np.max(sum_eds) // self.image.width // self.image.height * 2 *\
                                          downsample * downsample
        if roof > 0xFF:
            if roof > 0xFFFF:
                depth = np.uint32
            else:
                depth = np.uint16
        else:
            depth = np.uint8
        return depth

    def get_spectra_metadata(self, index=0):
        """return objectified xml with spectra metadata
        Arguments:
        index -- index of hypermap/spectra (default 0)
        """
        return self.spectra_data[index]


class BCF_reader(SFS_reader):

    """Class to read bcf (Bruker hypermapping) file.

    Inherits SFS_reader and all its attributes and methods.

    Attributes:
    filename

    Methods:
    print_the_metadata, persistent_parse_hypermap, parse_hypermap,
    py_parse_hypermap
    (Inherited from SFS_reader: print_file_tree, get_file)

    The class instantiates HyperHeader class as self.header attribute
    where all metadata, sum eds spectras, (SEM) imagery are stored.
    if persistent_parse_hypermap is called, the hypermap is stored
    as instance of HyperMap inside the self.hypermap dictionary,
    where index of the hypermap (default 0) is the key to the instance.
    """

    def __init__(self, filename):
        SFS_reader.__init__(self, filename)
        header_file = self.get_file('EDSDatabase/HeaderData')
        header_byte_str = header_file.get_as_BytesIO_string().getvalue()
        self.header = HyperHeader(header_byte_str)
        self.hypermap = {}

    def __repr__(self):
        return '<Bruker HyperMap BCF file>'

    def print_the_metadata(self):
        print('selected bcf contains:\n * imagery from detectors:')
        for i in self.header.image.images:
            print("\t*", i.detector_name)
        ed = self.header.get_spectra_metadata()
        print(' *', len(self.header.spectra_data), ' spectral cube(s)',
            'with', ed.meta.chnlCnt,
            'channels recorded, corresponding to {0:.2f}kV'.format(
            ed.meta.channel_to_energy(ed.meta.chnlCnt)))
        print('image size (width x height):',
              self.header.image.width, 'x', self.header.image.height)

    def persistent_parse_hypermap(self, index=0, downsample=1,
                                  cutoff_at_kV=None):
        """Parse and assign the hypermap to the HyperMap instance.

        Arguments:
        index -- index of hypermap in bcf if v2 (default 0)
        downsample -- downsampling factor of hypermap (default None)
        cutoff_at_kV -- low pass cutoff value at keV (default None)

        Method does not return anything, it adds the HyperMap instance to
        self.hypermap dictionary.

        See also:
        HyperMap, parse_hypermap
        """
        hypermap = self.parse_hypermap(index=index, downsample=downsample,
                                       cutoff_at_kV=cutoff_at_kV)
        self.hypermap[index] = HyperMap(hypermap, self, index=index,
                                        downsample=downsample)

    def parse_hypermap(self, index=0, downsample=1, cutoff_at_kV=None):
        """Unpack the Delphi/Bruker binary spectral map and return
        numpy array in memory efficient way.

        Pure python/numpy implimentation -- slow, or
        cython/memoryview/numpy implimentation if compilied and present
        (fast) is used.

        Arguments:
        index -- the index of hypermap in bcf if there is more than one
            hyper map in file.
        downsample -- downsampling factor (integer). Diferently than
            block_reduce from skimage.measure, the parser populates
            reduced array by suming results of pixels, thus having lower
            memory requiriments. (default 1)
        cutoff_at_kV -- value in keV to truncate the array at. Helps reducing
          size of array. (default None)

        Returns:
        numpy array of bruker hypermap, with (y,x,E) shape.
        """

        if type(cutoff_at_kV) in (int, float):
            eds = self.header.get_spectra_metadata()
            cutoff_chan = eds.meta.energy_to_channel(cutoff_at_kV)
        else:
            cutoff_chan = None

        spectrum_file = self.get_file('EDSDatabase/SpectrumData' + str(index))
        memory_available = psutil.virtual_memory().available
        map_depth = self.header.estimate_map_channels()
        if type(cutoff_chan) == int:
            map_depth = cutoff_chan
        dtype = self.header.estimate_map_depth(downsample=downsample)
        pixel_size = np.dtype(dtype).itemsize
        width = self.header.image.width
        height = self.header.image.height
        array_size = width * height * pixel_size * map_depth
        if array_size < memory_available * 0.9:
            return unbcf_fast.parse_to_numpy(spectrum_file,
                                             downsample=downsample,
                                             cutoff=cutoff_chan)
        else:
            print(array_size / memory_available)


class HyperMap(object):

    """Container class to hold the parsed bruker hypermap
    and its scale calibrations"""

    def __init__(self, nparray, parent, index=0, downsample=1):
        sp_meta = parent.header.get_spectra_metadata(index=index)
        self.e_offset = sp_meta.meta.offset    # keV -> eV
        self.e_scale = sp_meta.meta.scale
        self.xcalib = parent.header.image.x_res * downsample
        self.ycalib = parent.header.image.y_res * downsample
        self.hypermap = nparray
        self.energy_scale = sp_meta.meta.energy[:self.hypermap.shape[0]]

    def calc_max_peak_spectrum(self):
        return np.max(self.hypermap, axis=(1,2))
