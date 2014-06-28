import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset
import numpy as np

# Identify the HDF-EOS2 swath data file.
FILE_NAME = 'AIRS.2002.08.01.L3.RetStd_H031.v4.0.21.0.G06104133732.hdf'
GRID_NAME = 'ascending_MW_only'
DATAFIELD_NAME = 'Temperature_MW_A'

dset = Dataset(FILE_NAME)
data = dset.variables[DATAFIELD_NAME][11,:,:].astype(np.float64)

# Replace the filled value with NaN
fillvalue = dset.variables[DATAFIELD_NAME]._FillValue
data[data == fillvalue] = np.nan
cmin = np.nanmin(data)
cmax = np.nanmax(data)

latitude = dset.variables['Latitude'][:]
longitude = dset.variables['Longitude'][:]

# Draw an equidistant cylindrical projection using the low resolution
# coastline database.
m = Basemap(projection='cyl', resolution='l',
            llcrnrlat=-90, urcrnrlat = 90,
            llcrnrlon=-180, urcrnrlon = 180)

m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(-90., 90., 30.))
m.drawmeridians(np.arange(-180., 181., 45.))

# Render the image in the projected coordinate system.
x, y = m(longitude, latitude)
m.pcolor(x, y, data, alpha=0.90)
plt.clim(vmin=cmin, vmax=cmax)
m.colorbar()

plt.title('{0}\n{1}'.format(FILE_NAME, DATAFIELD_NAME))
plt.show()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
plt.savefig(filename)
