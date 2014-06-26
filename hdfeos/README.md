Fedora 20
=========
The native netcdf RPM was not build with the --with-hdf4 option, so you must
rebuild the RPM::

    $ yumdownloader --source netcdf
    $ rpm -i netcdf-4.2.1.1-5.fc19.src.rpm 
    $ cd ~/rpmbuild/SPECS



Mac
===
If you use MacPorts, you should install the hdf variant of the netcdf port::

    $ sudo port install netcdf+hdf
