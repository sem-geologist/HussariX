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
import periodictable as pt
import scipy.constants as sc
from . elements import elements

# atom_num = {1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C',
#             7: 'N', 8: 'O', 9: 'F', 10: 'Ne', 11: 'Na', 12: 'Mg',
#             13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar',
#             19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr',
#             25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn',
#             31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr',
#             37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo',
#             43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd',
#             49: 'In', 50: 'Sn', 51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe',
#             55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd',
#             61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy',
#             67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', 71: 'Lu', 72: 'Hf',
#             73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt',
#             79: 'Au', 80: 'Hg', 81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po',
#             85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th',
#             91: 'Pa', 92: 'U'}
#

iupac_siegbahn = {'K-L3': 'Kα1', 'K-L2': 'Kα2', 'K-M3': 'Kβ1',
                  'K-N3': 'Kβ2', 'K-M2': 'Kβ3', 'K-N5': 'Kβ4',
                  'K-M5': 'Kβ5', 'L3-M5': 'Lα1', 'L3-M4': 'Lα2',
                  'L3-N4': 'Lβ15', 'L3-N5': 'Lβ2', 'L3-O4': 'Lβ5',
                  'L3-N1': 'Lβ6', 'L3-O1': 'Lβ7', 'L3-M1': 'Ll',
                  'L3-M3': 'Ls', 'L3-M2': 'Lt', 'L3-N6': 'Lu',
                  'L2-M4': 'Lβ1', 'L2-M3': 'Lβ17', 'L2-N4': 'Lγ1',
                  'L2-N1': 'Lγ5', 'L2-O4': 'Lγ6', 'L2-O1': 'Lγ8',
                  'L2-M1': 'Ln', 'L2-N6': 'Lv', 'L1-M4': 'Lβ10',
                  'L1-M3': 'Lβ3', 'L1-M2': 'Lβ4', 'L1-M5': 'Lβ9',
                  'L1-N2': 'Lγ2', 'L1-N5': 'Lγ11', 'L1-N3': 'Lγ3',
                  'L1-O3': 'Lγ4', 'L1-O2': "Lγ'4", 'M3-N5': 'Mγ',
                  'M4-N6': 'Mβ', 'M4-N2': 'Mζ2', 'M5-N7': 'Mα1',
                  'M5-N6': 'Mα2', 'M5-N3': 'Mζ1'}

siegbahn_names = list(iupac_siegbahn.values())

x_ray_const = sc.h * sc.c / sc.eV * 1E12
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
    """return sinus theta for given energy and 2D parameter
    of diffracting crystal
    args:
    energy - energy in keV of the line
    two_D - 2D of diffracting crystal
    order - order of diffraction (default=1)
    """
    energy = energy / 1000
    return order * x_ray_const / (two_D * energy * (1 - K / (order**2)))


def sin_theta_to_energy(sin_theta, two_D, K, order=1):
    "return energy for given sin_theta"
    st = order * x_ray_const / (two_D * sin_theta * (1 - K / (order**2)))
    return st * 1000


def calc_scale_to_sin_theta(two_D, K, order=1):
    """ calc and return the quotient for recalculating energy
    axis to sin_theta axis or reverse:
    calculated quotient is intedend to be further used like:

    > sin_theta_axis = quotient / np.array([energies])
    > energy_axis = quotient / np.array([sin_theta])
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
    return log(hv / (energy)) / (hv / energy) * e


def xray_lines_for_plot(element, hv=15, siegbahn=True):
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
    if siegbahn:
        lines = [[iupac_siegbahn[x[0]], x[1], x[2]]
                 for x in lines if x[0] in iupac_siegbahn]
    return lines


def xray_shells_for_plot(element):
    shells = get_edges(element)
    lines = [[i, shells[i] / 1000] for i in shells]
    return lines


def xray_shells_for_plot_wds(element, two_D, K):
    shells = get_edges(element)
    quotient = calc_scale_to_sin_theta(two_D=two_D, K=K, order=1)
    lines = [[i, quotient * 1000 / shells[i]] for i in shells]
    return lines


def xray_lines_for_plot_wds(element, two_D, K, xmin=17000, xmax=85000,
                            order=1, hv=15, siegbahn=True, filter_orders=True):
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
    min_energy = quotient * 1000 / xmax
    max_energy = quotient * 1000 / xmin
    x_lines = get_element_lines(element)
    shells = get_excited_shells(element, hv * 1000)
    lines = [[i, quotient * 1000 / x_lines[i]['energy'],
              x_lines[i]['weight'] * 0.95 / sqrt(order) + 0.05]
             for i in x_lines
             if (min_energy < x_lines[i]['energy'] < max_energy)
             and (i.split('-')[0] in shells)]
    if filter_orders and order > 1:
        cutoff_limit = 0.05 + 0.004 * sqrt(order)
        lines = [x for x in lines if x[2] > cutoff_limit]
    if siegbahn:
        lines = [[iupac_siegbahn[x[0]], x[1], x[2]]
                 for x in lines if x[0] in iupac_siegbahn]
    return lines


def energy_to_lines(energy, tolerance=0.025):
    """return lines in the range of given tolerance of xray energy"""
    # TODO: rewrite it in SQL, this is where SQL will shine!!!
    sim_lines = {}
    for atom in xdb.atomic_symbols:
        x_l = get_element_lines_cached(atom)
        for line in x_l:
            if -tolerance < (x_l[line][0] - energy / 1000) < tolerance:
                sim_lines[atom] = line
    return sim_lines


def xray_energy(elem, ln):
    """return the energy by giving element (abbrevation) and line"""
    return get_element_lines_cached(elem)[ln][0]


def xray_weight(elem, ln):
    """return xray line weight from given abbrevation and line"""
    return get_element_lines_cached(elem)[ln][1]


def to_oxide_mass(elem, compound, mass):
    comp = pt.formula(compound)
    return mass / comp.mass_fraction[pt.elements.symbol(elem)]
