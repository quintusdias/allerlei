import os
from setuptools import setup
import sys

from Cython.Build import cythonize
import numpy

import pygrideos


from distutils.extension import Extension
cythonize("pygrideos/_som.pyx")
sources = [os.path.join('pygrideos', '_som.c'),
           os.path.join('pygrideos', 'src', 'cproj.c'),
           os.path.join('pygrideos', 'src', 'report.c'),
           os.path.join('pygrideos', 'src', 'paksz.c'),
           os.path.join('pygrideos', 'src', 'sphdz.c'),
           os.path.join('pygrideos', 'src', 'sominv.c'),
           os.path.join('pygrideos', 'src', 'inv_init.c')]
include_dirs = ["pygrideos/src/include"]
e = Extension("pygrideos/_som", sources=sources, include_dirs=include_dirs)
ext_modules = [e]

install_requires = ['numpy>=1.8.0', 'cython>=0.20']
if sys.hexversion < 0x03000000:
    install_requires.append('mock>=1.0.1')

classifiers = ["Programming Language :: Python",
               "Programming Language :: Python :: 2.7",
               "Programming Language :: Python :: 3.4",
               "Programming Language :: Python :: Implementation :: CPython",
               "License :: OSI Approved :: MIT License",
               "Development Status :: 3 - Production/Alpha",
               "Operating System :: MacOS",
               "Operating System :: POSIX :: Linux",
               "Intended Audience :: Science/Research",
               "Intended Audience :: Information Technology",
               "Topic :: Software Development :: Libraries :: Python Modules"]

kwargs = {'name':             'pygrideos',
          'description':      'Tools for accessing HDF-EOS grids',
          'long_description': open('README.md').read(),
          'author':           'John Evans, Joe Lee',
          'author_email':     'john.g.evans.ne@gmail.com',
          'url':              'http://hdfeos.org',
          'packages':         ['pygrideos'],
          'version':          '0.0.1',
          'ext_modules':      ext_modules,
          'include_dirs':     [numpy.get_include()],
          'install_requires': install_requires,
          'license':          'MIT',
          'classifiers':      classifiers}
setup(**kwargs)
