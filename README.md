# ![Icon](./lib/icons/hussarix_64_icon.svg) HussariX 
(formely QSEM-viewer)

Work in progress...

This is going to be universal graphical program for openning and exploring the SEM projects and EPMA files (single spectra from Bruker, mappings, Esprit projects, Cameca Peaksight files) with some datetime tracking functionality.

Dependencies:
- `PyQt5` - for GUI (currently)
- `pyqtgraph` (at least 0.11.0rc, not 0.12.2) - for plotting and advanced GUI
- `numpy` - for everything array,
- `scipy` - ?, (trying to make sure it is not a hard dependancy, however pyqtgraph can be boosted with it in imaging.)
- `kaitaistruct` runtime (0.9) - for using cameca peaksight binary parser.

All these dependencies can be installed as `pip` or `conda` packages.

Some code included here is developed in other repositories:
- `qpet` periodic element table in Qt https://github.com/sem-geologist/qpet
- `peaksight-binary-parser` parser written in Kaitai Struct for cameca binary files https://github.com/sem-geologist/peaksight-binary-parser 

Maybe in the far/near future this will have a bundled version (with everything included), but currently it needs working python package environment (pip or conda).

WIP. Major redesign (moving from manual python-written experimental parser for Cameca files to kaitai_stuct based parser with semi-stable API)

Current state of (working) implementations:
- [x] Cameca WDS scan (wdsDat) loading and plotting. 
