"""
This example code illustrates how to access and visualize a GESDISC OMI file
in Python.  If you have any questions, suggestions, comments  on this example,
please use the HDF-EOS Forum (http://hdfeos.org/forums).  If you would like to
see an  example of any other NASA HDF/HDF-EOS data product that is not 
listed in the HDF-EOS Comprehensive Examples page (http://hdfeos.org/zoo),
feel free to contact us at eoshelp@hdfgroup.org or post it at the HDF-EOS Forum
(http://hdfeos.org/forums).
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

FILE_NAME = 'OMI-Aura_L3-OMTO3e_2005m1214_v002-2006m0929t143855.he5'

# Can do this using either netCDF4 or h5py.
USE_NETCDF4 = True

if USE_NETCDF4:

    from netCDF4 import Dataset

    DATAFIELD_NAME = 'ColumnAmountO3'
    dset = Dataset(FILE_NAME)
    grp = dset.groups['HDFEOS'].groups['GRIDS'].groups['OMI Column Amount O3']
    var = grp.groups['Data Fields'].variables[DATAFIELD_NAME]
    data = var[:].astype(np.float64)

    # Get attributes needed for the plot.
    title = var.Title
    units = var.Units
    dset.close()

else:

    import h5py

    DATAFIELD_NAME = '/HDFEOS/GRIDS/OMI Column Amount O3/Data Fields/ColumnAmountO3'
    with h5py.File(FILE_NAME, mode='r') as f:

        dset = f[DATAFIELD_NAME]
        data = dset[:]

        # Have to manually create a masked array due to the fill value.
        # No need to scale the data, as the scale factor and add offset are
        # 1.0 and 0.0 respectively.
        data[data == dset.fillvalue] = np.nan
        data = np.ma.masked_where(np.isnan(data), data)

        # Get attributes needed for the plot.
        title = dset.attrs['Title']
        units = dset.attrs['Units']

# There is no geolocation data, so construct it ourselves.
longitude = np.arange(0., 1440.0) * 0.25 - 180 + 0.125
latitude = np.arange(0., 720.0) * 0.25 - 90 + 0.125

# Draw an equidistant cylindrical projection using the low resolution
# coastline database.
m = Basemap(projection='cyl', resolution='l',
            llcrnrlat=-90, urcrnrlat = 90,
            llcrnrlon=-180, urcrnrlon = 180)

m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(-90., 90., 30.))
m.drawmeridians(np.arange(-180, 180., 45.))

# Render the image in the projected coordinate system.
x, y = m(longitude, latitude)
m.pcolormesh(x, y, data, alpha=0.9)
m.colorbar()
fig = plt.gcf()

plt.title('{0}\n{1} ({2})'.format(FILE_NAME, title, units))
plt.show()
plt.draw()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
fig.savefig(filename)
