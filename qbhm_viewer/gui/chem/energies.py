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

from math import log, exp
import periodictable as pt
from .misc.elements import elements as el


class Elements(object):
    def __init__(self):
        self.elements = el

    def overvoltage(self, energy, kv):
        """
        return reduced xray line hight using
        very oversimplified model for HV -> Xray intensity
        which is fast"""
        return log(kv / energy) / (kv / energy) * exp(1)

    def xray_lines_for_plot(self, element, kv=15):
        """
        return list of lists with x-ray line, energy and weight
        ---------
        Atributes:
        element -- abbrevation of element
        kv -- acceleration voltage used during measurement

        ---------
        Returns:
        list of lists i.e.:

        """
        x_lines = self.elements[element]['Atomic_properties']['Xray_lines']
        lines = [[i, x_lines[i]['energy (keV)'],
                   x_lines[i]['weight'] * self.overvoltage(
                                                x_lines[i]['energy (keV)'], kv
                                                          )
                   ] for i in x_lines]
        return [x for x in lines if (x[2] > 0)]

    def nuber_to_atom(self, atom_number):
        """number to atom abbrevation"""
        for k in list(self.elements.keys()):
            if self.elements[k]['General_properties']['Z'] == atom_number:
                return k

    def xRayEnergy(self, el_abrv, line):
        return self.elements[el_abrv]['Atomic_properties']['Xray_lines'][line]['energy (keV)']

    def xRayWeight(self, el_abrv, line):
        return self.elements[el_abrv]['Atomic_properties']['Xray_lines'][line]['weight']

    def energy_to_lines(self, energy, tolerance=0.025):
        sim_lines = {}
        for atom in self.elements:
            x_lines = self.elements[atom]['Atomic_properties']['Xray_lines']
            for line in x_lines:
                if -tolerance < (x_lines[line]['energy (keV)'] - energy) < tolerance:
                    sim_lines[atom] = line
        return sim_lines

    def to_oxide_mass(self, elem, compound, mass):
        comp = pt.formula(compound)
        return mass / comp.mass_fraction[pt.elements.symbol(elem)]
