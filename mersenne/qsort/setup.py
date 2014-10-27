from distutils.core import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "qsort_ext",
    sources=["qsort_ext.pyx"]
)

setup(
    name="pqsort",
    ext_modules = cythonize([ext])
)

                
