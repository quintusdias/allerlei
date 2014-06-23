Fedora 20
=========
The native netcdf RPM is built with hdf4 support, so therefore netcdf4-python
can read HDF4 files out of the box.  This is the ideal situation!  Yay Fedora!

Fedora 19
=========
The native netcdf RPM was not built with the --with-hdf4 option, so you must
rebuild the RPM as follows::

1. Download the netcdf SRPM with ``yumdownloader --source netcdf``
2. Install the SRPM with ``rpm -i netcdf-4.2.1.1-5.fc19.src.rpm``
3. Change directories into your rpmbuild directory, i.e. ``cd ~/rpmbuild/SPECS``
4. Edit the spec file.  Add these two lines just underneath the ``%build`` line::

    export CPPFLAGS="-I/usr/include/hdf"
    export LDFLAGS="-L/usr/lib64/hdf -lmfhdf -ldf -ljpeg"

5.  Under the ``%global configure_opts`` section, add the following two lines::

    --enable-hdf4 \\\ 
    --enable-hdf4-file-tests \\\ 

6. Rebuild the RPMs with ``rpmbuild -bb netcdf.spec``
7. Install the newly-built RPM(s).


Ubuntu 13.10
============
Solution not finalized.

From a base install, use apt-get to additionally install 

    * ipython
    * python-matplotlib
    * python-mpltoolkits.basemap-data
    * python-mpltoolkits.basemap
    * libnetcdf7
    * python-netcdf

Anaconda
========
Solution not finalized.

::

    $ conda install basemap

But the netcdf package was not compiled with hdf support.

Mac
===
If you use MacPorts, you should install the hdf variant of the netcdf port::

    $ sudo port install netcdf+hdf
