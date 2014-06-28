"""
This example code illustrates how to access and visualize GESDISC_TRMM file in
Python.  If you have any questions, suggestions, comments  on this example,
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
FILE_NAME = '2A12.100402.70512.6.HDF'
DATAFIELD_NAME = 'cldWater'

dset = Dataset(FILE_NAME)
data = dset.variables[DATAFIELD_NAME][:,:,9].astype(np.float64)

# There is no listed fill value, but it would appear to be -9999000
data[data == -9999000] = np.nan

# Scale the data appropriately.
scale_factor = dset.variables[DATAFIELD_NAME].scale_factor
add_offset = dset.variables[DATAFIELD_NAME].add_offset
units = dset.variables[DATAFIELD_NAME].units
data = data / scale_factor + add_offset

# Retrieve the geolocation data.
latitude = dset.variables['geolocation'][:,:,0]
longitude = dset.variables['geolocation'][:,:,1]

# There is a wrap-around effect to deal with.
longitude[longitude < 0] += 360
longitude[longitude > 310] -= 360

# Draw an equidistant cylindrical projection using the low resolution
# coastline database.
m = Basemap(projection='cyl', resolution='l',
            llcrnrlat=-90, urcrnrlat = 90,
            llcrnrlon=-50, urcrnrlon = 310)

m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(-90., 90., 30.))
m.drawmeridians(np.arange(-45, 315., 45.))

# Render the image in the projected coordinate system.
# More than 99% of the pixel values are less than 10.
x, y = m(longitude, latitude)
m.pcolormesh(x, y, data, vmin=0, vmax=10)
m.colorbar()

plt.title('{0}\n{1}'.format(FILE_NAME, DATAFIELD_NAME))
plt.show()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
plt.savefig(filename)
