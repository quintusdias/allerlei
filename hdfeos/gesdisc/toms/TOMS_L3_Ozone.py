"""
This example code illustrates how to access and visualize a GESDISC TOMS file
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
from netCDF4 import Dataset
import numpy as np

# Identify the HDF data file.
FILE_NAME = 'TOMS-EP_L3-TOMSEPL3_2000m0101_v8.HDF'
DATAFIELD_NAME = 'Ozone'

dset = Dataset(FILE_NAME)
data = dset.variables[DATAFIELD_NAME][:].astype(np.float64)

# Replace the missing values with NaN.  Must create a masked array where
# NaN is involved.
fill_value = dset.variables[DATAFIELD_NAME]._FillValue
data[data == fill_value] = np.nan
datam = np.ma.masked_where(np.isnan(data), data)

# Retrieve the geolocation data.
latitude = dset.variables['YDim:TOMS Level 3'][:]
longitude = dset.variables['XDim:TOMS Level 3'][:]

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
m.pcolormesh(x, y, datam, alpha=0.9)
m.colorbar()

plt.title('{0}\n{1} ({2})'.format(FILE_NAME,
    dset.variables[DATAFIELD_NAME].long_name,
    dset.variables[DATAFIELD_NAME].units))
plt.show()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
plt.savefig(filename)
