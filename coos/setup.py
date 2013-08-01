from distutils.core import setup
setup(name='coos',
      version='0.0.1',
      description='COOS Utilities',
      long_description=open('README.md').read(),
      author='John Evans',
      author_email='john.g.evans.ne@gmail.com',
      url='https://github.com/quintusdias/allerlei',
      packages=['coos', 'coos.tests'],
      package_data={'coos': ['data/*.ruv']},
      scripts=['bin/process_radials'],
      install_requires=['netcdf4', 'pandas'],
      license='MIT',
      platforms=['darwin'],
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: Implementation :: CPython",
          "License :: OSI Approved :: MIT License",
          "Development Status :: 1 - Alpha",
          "Operating System :: MacOS",
          "Operating System :: POSIX :: Linux",
          "Intended Audience :: Scientific/Research",
          "Intended Audience :: Information Technology",
          "Topic :: Software Development :: Libraries :: Python Modules"
          ]
      )
