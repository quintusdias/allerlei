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
from netCDF4 import Dataset
import numpy as np

FILE_NAME = 'OMI-Aura_L2G-OMCLDO2G_2007m0129_v002-2007m0130t174603.he5'
DATAFIELD_NAME = 'CloudPressure'

dset = Dataset(FILE_NAME)
grp = dset.groups['HDFEOS'].groups['GRIDS'].groups['CloudFractionAndPressure']
var = grp.groups['Data Fields'].variables[DATAFIELD_NAME]
data = var[0,:,:].astype(np.float64)

# Scale the data appropriatedy.
scale = var.ScaleFactor
offset = var.Offset
data = scale * (data - offset)

# Replace the missing values with NaN.
missing_value = var.MissingValue
data[data == missing_value] = np.nan
fill_value = var._FillValue
data[data == fill_value] = np.nan

# Retrieve the geolocation data.
latitude = grp.groups['Data Fields'].variables['Latitude'][0,:,:]
longitude = grp.groups['Data Fields'].variables['Longitude'][0,:,:]

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

plt.title('{0}\n{1} ({2})'.format(FILE_NAME, var.Title, var.Units))
plt.show()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
plt.savefig(filename)
