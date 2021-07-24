# QSEM-Viewer
(This will be renamed to HussariX in the near future)

Work in progress...

This is going to be universal graphical program for openning and exploring the SEM projects (At least Bruker Esprit ~~and Jeol Analytic Station formats~~[that is not any more for me relevant, albeit it could change in the future]) and EPMA files (single spectra from Bruker, mappings, Cameca Peaksight files) with some datetime tracking functionality.

Dependencies:
- `PyQt5` - for GUI
- `pyqtgraph` (at least 0.11.0rc) - for plotting and advanced GUI
- `numpy` - for everything array,
- `scipy` - ?, (trying to make sure it is not hard dependecy, however pyqtgraph can be boosted with it in imaging.)
- `kaitaistruct` runtime (0.9) - for using cameca peaksight binary parser.

all these depndencies can be installed as `pip` or `conda` packages.

some code included here is developed in other repositories:
- `qpet` periodic element table in Qt https://github.com/sem-geologist/qpet
- `peaksight-binary-parser` parser written in Kaitai Struct for cameca binary files https://github.com/sem-geologist/peaksight-binary-parser 

Maybe in far future this will have bundled version (with everything included), but currently it needs working python package envirnment (pip or conda).

WIP. Major redesign.

Done and functional:
- [x] Cameca WDS scan (wdsDat).
