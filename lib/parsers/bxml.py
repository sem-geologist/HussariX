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
# This python library subset provides wraper classes for reading and using
# objects parsed from bruker xml (mainly by lxml objectifying them).
# At the moment EDS, SEM images and mapping results based on static images
# are supported.

import numpy as np
from scipy.interpolate import UnivariateSpline

import logging

from periodictable import elements

from math import log

from .. misc import xray_util as xu
from ..generic import spectra, image

_logger = logging.getLogger(__name__)

class Container(object):  #TODO: Boo
    pass


class EDXSpectrumMeta(object):
    def __init__(self, spectrum):
        self.zero_position = int(
                      spectrum.TRTHeaderedClass.ClassInstance.ZeroPeakPosition)
        self.amplification = int(
                      spectrum.TRTHeaderedClass.ClassInstance.Amplification)
        self.shapingTime = int(
                      spectrum.TRTHeaderedClass.ClassInstance.ShapingTime)
        self.detectorType = str(spectrum.TRTHeaderedClass.ClassInstance[1].Type)
        self.hv = float(
                      spectrum.TRTHeaderedClass.ClassInstance[2].PrimaryEnergy)
        self.elevationAngle = float(
                      spectrum.TRTHeaderedClass.ClassInstance[2].ElevationAngle)
        self.azimutAngle = float(
                      spectrum.TRTHeaderedClass.ClassInstance[2].AzimutAngle)
        self.x_offset = float(spectrum.ClassInstance[0].CalibAbs)
        self.x_res = float(spectrum.ClassInstance[0].CalibLin)
        self.chnlCnt = int(spectrum.ClassInstance[0].ChannelCount)
        self.date = str(spectrum.ClassInstance[0].Date)
        self.time = str(spectrum.ClassInstance[0].Time)
        self.calc_energy_axis()

    def energy_to_channel(self, energy, kV=True):
        """ convert energy to channel index,
        optional kwarg 'kV' (default: True) should be set to False
        if given energy units is in V"""
        if not kV:
            en_temp = energy / 1000
        else:
            en_temp = energy
        return int(round((en_temp - self.offset) / self.scale))

    def channel_to_energy(self, channel, kV=True):
        """convert given channel index to energy,
        optional kwarg 'kV' (default: True) decides if returned value
        is in kV or V"""
        if not kV:
            kV = 1000
        else:
            kV = 1
        return (channel * self.scale + self.offset) * kV

    def calc_energy_axis(self):
        """calc or re-calc and create energy axis (X axis) in the EDS
        plots"""
        self.energy = np.arange(self.offset,
                                self.scale * self.chnlCnt + self.offset,
                                self.scale)

#TODO: revamp the thing
class BasicEDXSpectrum(object):
    def __init__(self, spectrum):
        """
        Wrap the objectified bruker EDS spectrum xml part
        to the python object, leaving all the xml and bruker clutter behind

        Arguments:
        spectrum -- lxml objectified xml where spectrum.attrib['Type'] should
            be 'TRTSpectrum'
        """
        if str(spectrum.attrib['Type']) != 'TRTSpectrum':
            raise IOError('Not valid objectified xml passed',
                          ' to Bruker EDXSpectrum class')

        self.name =  spectrum.attrib.get('Name', 'noname')
            if self.name.endswith('.spx') or self.name.endswith('.xls'):
                self.name = self.name[:-4]
        self.metadata = {}
        self._parse_header(spectrum)
        self._parse_spectra(spectrum)
        
        self._estimate_zero_peak_fwhm()
        self._estimate_abc_for_2_sigmas()
        self.elements = []
    
    def _parse_header(self, spectrum):
        TRTHeader = spectrum.TRTHeaderedClass
        hardware_header = TRTHeader.xpath(
            "ClassInstance[@Type='TRTSpectrumHardwareHeader']")[0]
        detector_header = TRTHeader.xpath(
            "ClassInstance[@Type='TRTDetectorHeader']")[0]
        esma_header = TRTHeader.xpath(
            "ClassInstance[@Type='TRTESMAHeader']")[0]
        
        #set and parse hardware:
        self.metadata['hardware'] = dictionarize(hardware_header)
        self.real_time = self.metadata['hardware'].get('RealTime')
        self.live_time = self.metadata['hardware'].get('LifeTime')
        self.zero_position = self.metadata['hardware']['ZeroPeakPosition']
        
        self.metadata['detector'] = dictionarize(detector_header)
        
         # decode silly hidden detector layer info:
        det_l_str = self.detector_metadata['DetLayers']
        dec_det_l_str = codecs.decode(det_l_str.encode('ascii'), 'base64')
        mini_xml = objectify.fromstring(unzip_block(dec_det_l_str))
        self.detector_metadata['DetLayers'] = {}  # Overwrite with dict
        for i in mini_xml.getchildren():
            self.detector_metadata['DetLayers'][i.tag] = dict(i.attrib)
            
         # map stuff from esma xml branch:
        self.esma_metadata = dictionarize(esma_header)
        self.hv = self.esma_metadata.get('PrimaryEnergy')
        
    def _parse_spectra(self, spectra):
        spectrum_header = spectrum.xpath(
            "ClassInstance[@Type='TRTSpectrumHeader']")[0]
        self.metadata['spectrum'] = dictionarize(spectrum_header)
        self.x_offest = self.metadata['spectrum']['CalibAbs']
        self.x_res = self.metadata['spectrum']['CalibLin']
        self.chnl_cnt = self.metadata['spectrum']['ChannelCount']
        self.gen_scale()
        self.data = np.fromstring(spectrum.Channels.text, dtype='Q', sep=",")
        
    def _estimate_zero_peak_fwhm(self):
        """estimate full width at half maximum for bruker reference 0.0kV peak"""
        zpp = self.zero_position  # zero peak position
        zero_peak = UnivariateSpline(self.scale[:2 * zpp],
                                     self.data[:2 * zpp] -
                                         np.max(self.data[zpp - 3:zpp + 3]) / 2)
        self.fwhm_zero = np.diff(zero_peak.roots())[0]

    def _estimate_abc_for_2_sigmas(self):
        """estimation is based on RE testing of bruker eds spectras behaviour.
        estimated a, b, c parameters are meant to be used to calculate
        2sigma width of the peak at given energy [en]:
            sigma_2_width = a + b * log(en + c)

        THIS MODEL SHOULD GET MORE PRECISE IN FUTURE
        """
        self._w_par = Container()
        self._w_par.a = 0.780977 + 0.609263 * log(0.277366 - self.fwhm_zero)
        self._w_par.b = -0.167433 - 0.259091 * log(0.360115 - self.fwhm_zero)
        self._w_par.c = -26.0497 - 17.1639 * log(0.219774 - self.fwhm_zero)

    def calc_width(self, energy):
        """estimate 2 sigma of peak for given energy"""
        return self._w_par.a + self._w_par.b * log(energy + self._w_par.c)

    def calc_sigma1(self, energy):
        """estimate one sigma of the peak at given energy"""
        width = self.calc_width(energy)
        return width / 4

    def make_roi(self, energy):
        """make 2 sigma ROI (list of min and max energy)"""
        width = self.calc_width(energy)
        ### TODO: everything goes below to universal spectra class
        return [energy - width / 2, energy + width / 2]

    def set_elements(self, element_list):
        self.elements = element_list

    def add_element(self, element):
        self.elements.append(element)

    def remove_element(self, element):
        self.elements.remove(element)

#TODO rewrite below:
class AnalysedEDXSpectrum(BasicEDXSpectrum):
    def __init__(self, spectrum):
        BasicEDXSpectrum.__init__(self, spectrum)
        self._parse_elements(spectrum)
        self._parse_results(spectrum)
        self._parse_roi_results(spectrum)

    def _parse_results(self, spectrum):
        self.results = {}
        try:
            for j in spectrum.xpath("ClassInstance[@Type='TRTResult']/Result"):
                children = j.getchildren()
                elem = str(elements[children[0].pyval])
                self.results[elem] = {}
                for i in children[1:]:
                    self.results[elem][str(i.tag)] = i.pyval
        except IndexError:
            _logger.info('no results present..')

    def _parse_elements(self, spectrum):
        try:
            for k in spectrum.xpath(
                    "ClassInstance[@Type='TRTPSEElementList']/*/ClassInstance"):
                self.elements.append(str(k.attrib['Name']))
        except IndexError:
            _logger.info('no element selection present in the spectra..')

    def _parse_roi_results(self, spectrum):
        self.roi_results = {}
        try:
            for j in spectrum.xpath(
                                 "ClassInstance[@Type='TRTResult']/RoiResults"):
                children = j.getchildren()
                elem = str(children[1].pyval)
                self.roi_results[elem] = {}
                for i in children[2:]:
                    self.roi_results[elem][str(i.tag)] = i.pyval
        except IndexError:
            _logger.info('no ROI results present..')

        if len(self.roi_results.keys()) > 0:
            for k in self.roi_results:
                try:
                    bounds = self.make_roi(self.roi_results[k]['Energy'])
                    self.roi_results[k]['ROI'] = bounds
                except KeyError:
                    line = max(xu.xray_lines_for_plot(k), key=lambda x: x[2])
                    self.roi_results[k]['Line'] = line[0]
                    self.roi_results[k]['Energy'] = line[1]
                    bounds = self.make_roi(self.roi_results[k]['Energy'])
                    self.roi_results[k]['ROI'] = bounds


class ImageMeta(object):
    def __init__(self,  xml_image):
        pass
