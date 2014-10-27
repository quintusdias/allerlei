from distutils.core import setup, Extension
from Cython.Build import cythonize

ext = Extension(
    "qsort",
    sources=["qsort.pyx"]
)

setup(
    name="pqsort",
    ext_modules = cythonize([ext])
)

                
