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

import logging
_logger = logging.getLogger(__name__)

from periodictable import elements

class BasicEDXSpectrum(object):
    def __init__(self, spectrum, name='noname'):
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
        
        try:
            self.name = str(spectrum.attrib['Name'])
            if self.name.endswith('.spx') or self.name.endswith('.xls'):
                self.name = self.name[:-4]
        except KeyError:
            _logger.warning('spectrum have no name...')
            self.name = name
        
        try:
            self.realTime = int(
                            spectrum.TRTHeaderedClass.ClassInstance.RealTime)
            self.lifeTime = int(
                            spectrum.TRTHeaderedClass.ClassInstance.LifeTime)
            self.deadTime = int(
                            spectrum.TRTHeaderedClass.ClassInstance.DeadTime)
        except AttributeError:
            _logger.warning('spectrum have no dead time records...')
        self.zeroPeakPosition = int(
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
        self.calibAbs = float(spectrum.ClassInstance[0].CalibAbs)
        self.calibLin = float(spectrum.ClassInstance[0].CalibLin)
        self.chnlCnt = int(spectrum.ClassInstance[0].ChannelCount)
        self.date = str(spectrum.ClassInstance[0].Date)
        self.time = str(spectrum.ClassInstance[0].Time)
        self.data = np.fromstring(str(spectrum.Channels), dtype='Q', sep=",")
        self.calc_energy_axis()
        self.elements = []

    def energy_to_channel(self, energy, kV=True):
        """ convert energy to channel index,
        optional kwarg 'kV' (default: True) should be set to False
        if given energy units is in V"""
        if not kV:
            en_temp = energy / 1000.
        else:
            en_temp = energy
        return int(round((en_temp - self.calibAbs) / self.calibLin))

    def channel_to_energy(self, channel, kV=True):
        """convert given channel index to energy,
        optional kwarg 'kV' (default: True) decides if returned value
        is in kV or V"""
        if not kV:
            kV = 1000
        else:
            kV = 1
        return (channel * self.calibLin + self.calibAbs) * kV
    
    def calc_energy_axis(self):
        """calc or re-calc and create energy axis (X axis) in the EDS
        plots"""
        self.energy = np.arange(self.calibAbs,
                                self.calibLin * self.chnlCnt + self.calibAbs,
                                self.calibLin)
        
    def set_elements(self, element_list):
        self.elements = element_list
        
    def add_element(self, element):
        self.elements.append(element)
    
    def remove_element(self, element):
        self.elements.remove(element)


class AnalysedEDXSpectrum(BasicEDXSpectrum):
    def __init__(self, spectrum):
        BasicEDXSpectrum.__init__(self, spectrum)
        self.elements = []
        self._parse_elements(spectrum)
        self.results = {}
        self._parse_results(spectrum)
        
    def _parse_results(self, spectrum):
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

