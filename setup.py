from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='fast_bcf_parser',
    ext_modules=cythonize("lib/parsers/unbcf_fast.pyx",
                          #gdb_debug=True
                          ),
)
