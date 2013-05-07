from distutils.core import setup
setup(name='allerlei',
      version='0.0.1',
      description='various tools that no one would find useful',
      long_description=open('README.md').read(),
      author='John Evans',
      author_email='john.g.evans.ne@gmail.com',
      url='https://github.com/quintusdias/allerlei',
      packages=['allerlei', 'allerlei.hdf5', 'allerlei.hdf5.test', 'allerlei.test'],
      package_data={'allerlei': ['data/*.jpg', 'data/*.h5']},
      license='MIT',
      platforms=['darwin'],
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.2",
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
