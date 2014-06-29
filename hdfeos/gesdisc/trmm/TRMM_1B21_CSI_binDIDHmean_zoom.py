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

# Identify the HDF-EOS2 swath data file.
FILE_NAME = '1B21_CSI.990906.10217.KORA.6.HDF'
DATAFIELD_NAME = 'binDIDHmean'

dset = Dataset(FILE_NAME)
data = dset.variables[DATAFIELD_NAME][:].astype(np.float64)

# Retrieve the geolocation data.
print(dset.variables['geolocation'].shape)
latitude = dset.variables['geolocation'][:,:,0]
longitude = dset.variables['geolocation'][:,:,1]

# Draw an equidistant cylindrical projection using the high resolution
# coastline database.
m = Basemap(projection='cyl', resolution='h',
            llcrnrlat=31, urcrnrlat = 36,
            llcrnrlon=122, urcrnrlon = 133)

m.drawcoastlines(linewidth=0.5)

# Label parallels on the left, meridians on bottom.
m.drawparallels(np.arange(31, 36), [True, False, False, False])
m.drawmeridians(np.arange(122, 133), [False, False, False, True])

# Render the image in the projected coordinate system.
x, y = m(longitude, latitude)
m.pcolor(x, y, data)
m.colorbar()

plt.title('{0}\n{1}'.format(FILE_NAME, DATAFIELD_NAME))
plt.show()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
plt.savefig(filename)