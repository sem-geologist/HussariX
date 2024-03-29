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

# from xraydb import XrayDB
from math import log, e, sqrt
from functools import cached_property
from . elements import elements
from . sat_lines import sattelite_lines
from . rae_lines import lines as rae_lines


class Element:
    _el_list = (
          "n H He "
          "Li Be B C N O F Ne "
          "Na Mg Al Si P S Cl Ar "
          "K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr "
          "Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe "
          "Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu "
          "Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
          "Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm".split())

    def __init__(self, el):
        if type(el) == str:
            if el in self._el_list:
                self.atomic_number = self._el_list.index(el)
            else:
                raise TypeError(f'not possible to initialise element from '
                                f'given string {el}')
        elif type(el) == int and el <= 99:
            self.atomic_number = el
        else:
            raise TypeError(f'cant initiate Element from {el}')

    @cached_property
    def symbol(self):
        """element abbreviation"""
        return self._el_list[self.atomic_number]

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return self.symbol

    def __eq__(self, other):
        return self.atomic_number == other.atomic_number


iupac_siegbahn = {'K-L3': 'Kα1', 'K-L2': 'Kα2', 'K-M3': 'Kβ1',
                  'K-N3': 'Kβ2', 'K-M2': 'Kβ3', 'K-N5': 'Kβ4',
                  'K-M5': 'Kβ5', 'L3-M5': 'Lα1', 'L3-M4': 'Lα2',
                  'L3-N4': 'Lβ15', 'L3-N5': 'Lβ2', 'L3-O4': 'Lβ5',
                  'L3-N1': 'Lβ6', 'L3-O1': 'Lβ7', 'L3-M1': 'Lℓ',
                  'L3-M3': 'Ls', 'L3-M2': 'Lt', 'L3-N6': 'Lu',
                  'L2-M4': 'Lβ1', 'L2-M3': 'Lβ17', 'L2-N4': 'Lγ1',
                  'L2-N1': 'Lγ5', 'L2-O4': 'Lγ6', 'L2-O1': 'Lγ8',
                  'L2-M1': 'Lη', 'L2-N6': 'Lν', 'L1-M4': 'Lβ10',
                  'L1-M3': 'Lβ3', 'L1-M2': 'Lβ4', 'L1-M5': 'Lβ9',
                  'L1-N2': 'Lγ2', 'L1-N5': 'Lγ11', 'L1-N3': 'Lγ3',
                  'L1-O3': 'Lγ4', 'L1-O2': "Lγ'4", 'M3-N5': 'Mγ',
                  'M4-N6': 'Mβ', 'M4-N2': 'Mζ2', 'M5-N7': 'Mα1',
                  'M5-N6': 'Mα2', 'M5-N3': 'Mζ1', 'K-L1': 'Kα3'}

siegbahn_names = list(iupac_siegbahn.values())

# import scipy.constants as sc
# x_ray_const = sc.h * sc.c / sc.eV * 1E12
# it would be crazy to depend on whole scipy just for a few constants
# here the hardcoded value useful for energy <-> wavelenght/sin(theta)
# transitions""
X_RAY_CONST = 1239841.9843320027
# cached_xdb = {}
# xdb = XrayDB()


# def get_element_lines_cached(element):
#     try:
#         return cached_xdb[element]
#     except KeyError:
#         cached_xdb[element] = xdb.xray_lines(element)
#         return cached_xdb[element]

def get_element_lines(element):
    return elements[element]['emission_line']


def get_edges(element):
    return elements[element]['edge_line']


def get_excited_shells(element, kV):
    edges = elements[element]['edge_line']
    return [i for i in edges if edges[i] < kV]


def energy_to_sin_theta(energy, two_D, K, order=1):
    """return sinus theta for given energy (eV) and 2D parameter
    of diffracting crystal
    args:
    energy - energy in keV of the line
    two_D - 2D of diffracting crystal
    order - order of diffraction (default=1)
    """
    energy = energy / 1000
    return order * X_RAY_CONST / (two_D * energy * (1 - K / (order**2)))


def sin_theta_to_energy(sin_theta, two_D, K, order=1):
    "return energy (eV) for given cameca sin_theta*100k"
    st = order * X_RAY_CONST / (two_D * sin_theta * (1 - K / (order**2)))
    return st * 1000


def calc_scale_to_sin_theta(two_D, K, order=1):
    """ calc and return the quotient for recalculating energy
    axis to sin_theta (*100k; cameca units) axis or reverse:
    calculated quotient is intedend to be further used like:

    > sin_theta_axis = quotient / np.array([energies])
    > energy_axis = quotient / np.array([sin_theta])
    """
    return order * X_RAY_CONST / (two_D * (1 - K / (order**2)))


def overvoltage(energy, hv):
    """
    return reduced xray line hight using
    very oversimplified model for HV -> Xray intensity
    which is fast and coarse approximation but not the
    real model.
    it gives maximum peak at 2.7 or (number e) ratio of
    aceleration voltage"""
    return log(hv / (energy)) / (hv / energy) * e


def rae_line_for_keV(element, hv=15):
    """its only single line per element"""
    shells = get_excited_shells(element, hv * 1000)
    if 'K' not in shells:  # as those are only KLL lines
        return None
    rae_energy = rae_lines[element]
    rael = ["{} KLL".format(element), rae_energy / 1000, 0.03]
    return rael


def rae_line_for_sin_θ_100k(element, two_D, K, xmin=17000, xmax=85000,
                            order=1, hv=15, filter_orders=True):
    if order < 4:
        quotient = calc_scale_to_sin_theta(two_D=two_D, K=K, order=order)
        rael = rae_line_for_keV(element, hv=hv)
        rael[1] = quotient / rael[1]
        if xmin < rael[1] < xmax:
            rael[2] = rael[2] * 0.95 / sqrt(order)
            return rael
    return None


def sat_lines_for_keV(element, hv=15):
    shells = get_excited_shells(element, hv * 1000)
    shells = [shell[0] for shell in shells]  # take only family
    sat_lines = sattelite_lines[element]
    lines = [[line['full_html_str'],
              line['energy'] / 1000,
              line["weight"],
              line['family']]
             for line in sat_lines]
    lines = [x for x in lines if x[3] in shells]
    return lines


def sat_lines_for_sin_θ_100k(element, two_D, K, xmin=17000, xmax=85000,
                             order=1, hv=15, filter_orders=True):
    quotient = calc_scale_to_sin_theta(two_D=two_D, K=K, order=order)
    min_energy = quotient * 1000 / xmax
    max_energy = quotient * 1000 / xmin
    sat_lines = sattelite_lines[element]
    shells = get_excited_shells(element, hv * 1000)
    shells = [shell[0] for shell in shells]  # take only family
    lines = [[line['full_html_str'],
              quotient * 1000 / line['energy'],
              line["weight"] * 0.95 / sqrt(order),
              line['family']]
             for line in sat_lines
             if ((min_energy < line['energy'] < max_energy)
             and line['family'] in shells)]
    if filter_orders and order > 1:
        cutoff_limit = 0.04 + 0.004 * sqrt(order)
        lines = [x for x in lines if x[2] > cutoff_limit]
    return lines


def xray_lines_for_keV(element, hv=15):
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
    x_lines = get_element_lines(element)
    lines = [[i,
              x_lines[i]['energy'] / 1000,
              x_lines[i]['weight'] * 0.95 * overvoltage(
                  x_lines[i]['energy'] / 1000, hv) + 0.05]
             for i in x_lines]
    shells = get_excited_shells(element, hv * 1000)
    lines = [x for x in lines if (x[0].split('-')[0] in shells)]
    return lines


def xray_shells_for_keV(element):
    shells = get_edges(element)
    lines = [[i, shells[i] / 1000] for i in shells]
    return lines


def xray_shells_for_sin_θ_100k(element, two_D, K, order=1):
    shells = get_edges(element)
    quotient = calc_scale_to_sin_theta(two_D=two_D, K=K, order=order)
    lines = [[i, quotient * 1000 / shells[i]] for i in shells]
    return lines


def xray_lines_for_sin_θ_100k(element, two_D, K, xmin=17000, xmax=85000,
                              order=1, hv=15, filter_orders=True):
    """
    return list of lists with x-ray line, sin(theta)*10^5 (cameca wds units)
    and weight for given element at known acceleration voltage
    ---------
    Atributes:
    element -- abbrevation of element
    hv -- acceleration voltage used during measurement

    ---------
    Returns:
    list of lists i.e.:

    """
    quotient = calc_scale_to_sin_theta(two_D=two_D, K=K, order=order)
    min_energy = quotient * 1000 / xmax
    max_energy = quotient * 1000 / xmin
    x_lines = get_element_lines(element)
    shells = get_excited_shells(element, hv * 1000)
    lines = [[i, quotient * 1000 / x_lines[i]['energy'],
              x_lines[i]['weight'] * 0.95 / sqrt(order) + 0.05]
             for i in x_lines
             if (min_energy < x_lines[i]['energy'] < max_energy)
             and (i.split('-')[0] in shells)]
    if filter_orders and order > 2:
        cutoff_limit = 0.04 + 0.004 * sqrt(order)
        lines = [x for x in lines if x[2] > cutoff_limit]
    return lines
