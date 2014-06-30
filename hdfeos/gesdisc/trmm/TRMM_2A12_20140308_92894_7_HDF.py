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
FILE_NAME = '2A12.20140308.92894.7.HDF'
DATAFIELD_NAME = 'surfaceRain'

# Retrieve the data.
dset = Dataset(FILE_NAME)
data = dset.variables[DATAFIELD_NAME][:].astype(np.float64)
units = dset.variables[DATAFIELD_NAME].units

# Construct an indexed version of the data.
levels = [0.0, 0.1, 1.0, 10.0, 30.0]
Z = np.zeros(data.shape, dtype=np.float64)
for j in range(len(levels)-1):
    Z[np.logical_and(data >= levels[j], data < levels[j+1])] = j  
Z[data >= levels[-1]] = len(levels)


# Retrieve the geolocation data.
latitude = dset.variables['Latitude'][:]
longitude = dset.variables['Longitude'][:]

# There is a wrap-around effect to deal with.
# Wrap the trailing end of the swath into the positive range (>180)
#longitude[longitude < 0] += 360
longitude[longitude < -165] += 360

# Draw an equidistant cylindrical projection using the low resolution
# coastline database.
m = Basemap(projection='cyl', resolution='l',
            llcrnrlat=-90, urcrnrlat = 90,
            llcrnrlon=-165, urcrnrlon = 197)

m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(-90., 90., 30.), [True, False, False, False])
m.drawmeridians(np.arange(-180, 180., 45.), [False, False, False, True])

# Render the image in the projected coordinate system.
x, y = m(longitude, latitude)

# Use a discretized colormap since we have only two levels.
colors = ['#0000ff', '#0088ff', '#8888ff', '#ff8888', '#ff0000']
cmap = mpl.colors.ListedColormap(colors)
bounds = np.arange(6)
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
m.pcolormesh(x, y, Z, cmap=cmap, norm=norm)
color_bar = plt.colorbar()
color_bar.set_ticks([0.5, 1.5, 2.5, 3.5, 4.5])
color_bar.set_ticklabels(['0', '0.1', '1.0', '10', '30'])


#m.colorbar()
fig = plt.gcf()

plt.title('{0}\n{1}'.format(FILE_NAME, DATAFIELD_NAME))
plt.show()

filename = "{0}.{1}.png".format(FILE_NAME[:-4], DATAFIELD_NAME)
fig.savefig(filename)
