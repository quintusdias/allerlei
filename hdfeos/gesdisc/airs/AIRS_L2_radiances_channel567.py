import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset
import numpy as np

# Identify the HDF-EOS2 swath data file.
FILE_NAME = 'AIRS.2002.12.31.001.L2.CC_H.v4.0.21.0.G06100185050.hdf'
SWATH_NAME = 'L2_Standard_cloud-cleared_radiance_product'
DATAFIELD_NAME = 'radiances'

dset = Dataset(FILE_NAME)
data = dset.variables['radiances'][:,:,567].astype(np.float64)

# Replace the filled value with NaN
data[data == -9999] = np.nan
cmin = np.nanmin(data)
cmax = np.nanmax(data)

latitude = dset.variables['Latitude'][:]
longitude = dset.variables['Longitude'][:]

# Draw a polar stereographic projection using the low resolution coastline
# database.
m = Basemap(projection='spstere', resolution='l',
            boundinglat=-65, lon_0 = 180)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(-80., -50., 5.))
m.drawmeridians(np.arange(-180., 181., 20.))

# Render the image in the projected coordinate system.
x, y = m(longitude, latitude)
m.pcolor(x, y, data, alpha=0.90)
plt.clim(vmin=cmin, vmax=cmax)
m.colorbar()

plt.title('{0}\n{1}'.format(FILE_NAME, DATAFIELD_NAME))
plt.show()

plt.savefig(FILE_NAME[:-4] + '.png')
