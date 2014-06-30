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

FILE_NAME = '3B43.070901.6A.HDF'
DATAFIELD_NAME = 'precipitation'

# Ignore the leading singleton dimension.
dset = Dataset(FILE_NAME)
data = dset.variables[DATAFIELD_NAME][0,:,:].astype(np.float64)

# Consider 0 to be the fill value.
# Must create a masked array where nan is involved.
data[data == 0] = np.nan
datam = np.ma.masked_where(np.isnan(data), data)


# The lat and lon should be calculated manually.
# More information can be found at:
# http://disc.sci.gsfc.nasa.gov/additional/faq/precipitation_faq.shtml#lat_lon
latitude = np.arange(-49.875, 49.875, 0.025)
longitude = np.arange(-179.875, 179.875, 0.25)

# Draw an equidistant cylindrical projection using the low resolution
# coastline database.
m = Basemap(projection='cyl', resolution='l',
            llcrnrlat=-90, urcrnrlat = 90,
            llcrnrlon=-180, urcrnrlon = 180)

m.drawcoastlines(linewidth=0.5)

m.drawparallels(np.arange(-50, 50, 10))
m.drawmeridians(np.arange(-180, 180, 45))

# Render the image in the projected coordinate system.
x, y = m(longitude, latitude)
m.pcolormesh(x, y, datam, alpha=0.9)
m.colorbar()
fig = plt.gcf()

plt.title('{0}\n{1}'.format(FILE_NAME, DATAFIELD_NAME))
plt.show()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
fig.savefig(filename)
