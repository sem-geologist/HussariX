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

from math import log, e
import periodictable as pt
import scipy.constants as sc
from . elements import elements


x_ray_const = sc.h * sc.c / sc.eV * 1E12


def energy_to_sin_theta(energy, two_D, K, order=1):
    """return sinus theta for given energy and 2D parameter
    of diffracting crystal
    args:
    energy - energy in ekV of the line
    two_D - 2D of diffracting crystal
    order - order of diffraction (default=1)
    """
    return (order * x_ray_const) / (two_D * energy * (1 - K / (order**2)))


def sin_theta_to_energy(sin_theta, two_D, K, order=1):
    "return energy for given sin_theta"
    return (order * x_ray_const) / (two_D * sin_theta * (1 - K / (order**2)))


def calc_scale_to_sin_theta(two_D, K, order=1):
    """ calc and return the quotient for recalculating energy
    axis to sin_theta axis or reverse:
    calculated quotient is intedend to be further used like:
    
    > sin_theta_axis = quotient / np.array([energies])
    > energies_axis = quotient / np.array([sin_theta_vals])
    """
    return order * x_ray_const / (two_D * (1 - K / (order**2)))


def overvoltage(energy, hv):
    """
    return reduced xray line hight using
    very oversimplified model for HV -> Xray intensity
    which is fast and coarse approximation but not the
    real model.
    it gives maximum peak at 2.7 or (number e) ratio of
    aceleration voltage"""
    return log(hv / energy) / (hv / energy) * e


def xray_lines_for_plot(element, hv=15):
    """
    return list of lists with x-ray line, energy and weight
    for given element at known acceleration voltage
    ---------
    Atributes:
    element -- abbrevation of element
    hv -- acceleration voltage used during measurement

    ---------
    Returns:
    list of lists i.e.:

    """
    x_lines = elements[element]['Atomic_properties']['Xray_lines']
    lines = [[i, x_lines[i]['energy (keV)'],
              x_lines[i]['weight'] * overvoltage(x_lines[i]['energy (keV)'], hv)
            ] for i in x_lines]
    return [x for x in lines if (x[2] > 0)]

def xray_lines_for_plot_wds(element, two_D, K, order=1, kv=15):
    """
    return list of lists with x-ray line, energy and weight
    for given element at known acceleration voltage
    ---------
    Atributes:
    element -- abbrevation of element
    hv -- acceleration voltage used during measurement

    ---------
    Returns:
    list of lists i.e.:

    """
    quotient = calc_scale_to_sin_theta(two_D=two_D, K=K, order=order)
    x_lines = elements[element]['Atomic_properties']['Xray_lines']
    lines = [[i, quotient / x_lines[i]['energy (keV)'],
              x_lines[i]['weight'] * overvoltage(x_lines[i]['energy (keV)'], kv)
            ] for i in x_lines]
    return [x for x in lines if (x[2] > 0)]

def energy_to_lines(energy, tolerance=0.025):
    """return lines in the range of given tolerance of xray energy"""
    sim_lines = {}
    for atom in elements:
        x_l = elements[atom]['Atomic_properties']['Xray_lines']
        for line in x_l:
            if -tolerance < (x_l[line]['energy (keV)'] - energy) < tolerance:
                sim_lines[atom] = line
    return sim_lines


def xray_energy(elem, ln):
    """return the energy by gining element (abbrevation) and line"""
    return elements[elem]['Atomic_properties']['Xray_lines'][ln]['energy (keV)']


def xray_weight(elem, ln):
    """return xray line weight from given abbrevation and line"""
    return elements[elem]['Atomic_properties']['Xray_lines'][ln]['weight']


def to_oxide_mass(self, elem, compound, mass):
        comp = pt.formula(compound)
        return mass / comp.mass_fraction[pt.elements.symbol(elem)]
