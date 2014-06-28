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

FILE_NAME = '2B31_CSI.990911.10296.KORA.6.HDF'
DATAFIELD_NAME = 'dHat'

dset = Dataset(FILE_NAME)
data = dset.variables[DATAFIELD_NAME][:].astype(np.float64)

# Scale the data appropriately.
scale_factor = dset.variables[DATAFIELD_NAME].scale_factor
add_offset = dset.variables[DATAFIELD_NAME].add_offset
data = data / scale_factor + add_offset

# Retrieve the geolocation data.
latitude = dset.variables['geolocation'][:,:,0]
longitude = dset.variables['geolocation'][:,:,1]

# Draw an equidistant cylindrical projection using the high resolution
# coastline database.
m = Basemap(projection='cyl', resolution='h',
            llcrnrlat=30, urcrnrlat = 36,
            llcrnrlon=121, urcrnrlon = 133)

m.drawcoastlines(linewidth=0.5)

m.drawparallels(np.arange(30, 36))
m.drawmeridians(np.arange(121, 133))

# Render the image in the projected coordinate system.
x, y = m(longitude, latitude)
m.pcolormesh(x, y, data, alpha=0.9)
m.colorbar()

plt.title('{0}\n{1})'.format(FILE_NAME, DATAFIELD_NAME))
plt.show()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
plt.savefig(filename)
