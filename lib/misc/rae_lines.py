"""Radiative auger effect (RAE) lines visible on high intensity WDS,
These depends from bondings and so intensity and possition can shift.
Values here are take from:
* H.Tkahashi, I.Harrowfield, C. MacRae, N. Wilson, K. Tsutsumi, 2001.
  Extended x-ray emission fine structure and high-energy satellite lines state
  measured by electron probe microanalysis. Surf.Interface Anal. 31: 118-125

All the lines are KLL, and as there is one per elmenet, the dictionary has
simple structure: key - element abbreviation, value - energy in eV"""

lines = {"B": 180,
         "C": 272,
         "N": 381,
         "O": 510,
         "F": 650,
         "Ne": 822,
         "Na": 990,
         "Mg": 1186,
         "Al": 1396,
         "Si": 1619,
         "P": 1865,
         "S": 2121,
         "Cl": 2381,
         "K": 3000,  # not precise, read from the graph
         "Ca": 3300}  # not precise, read from the graph
