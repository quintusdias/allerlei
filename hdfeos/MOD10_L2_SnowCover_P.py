import os

import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset
import numpy as np

# Identify the HDF-EOS2 swath data file.
FILE_NAME = 'MOD10_L2.A2000065.0040.005.2008235221207.hdf'

# The swath name is 'MOD_Swath_Snow', but we don't need that.

# Identify the data field.
DATAFIELD_NAME = 'Snow_Cover'

def run():
    rows = slice(5, 4060, 10)
    cols = slice(5, 2708, 10)

    dset = Dataset(FILE_NAME)
    data = dset.variables['Snow_Cover'][rows, cols].astype(np.float64)

    latitude = dset.variables['Latitude'][:]
    longitude = dset.variables['Longitude'][:]

    m = Basemap(projection='npstere', resolution='l',
                boundinglat=64, lon_0 = 0)
    m.drawlsmask(land_color='coral', ocean_color='aqua', resolution='l')
    m.drawcoastlines(linewidth=0.5)
    #m.fillcontinents(color='coral', lake_color='aqua')
    m.drawparallels(np.arange(-80., 81., 20.))
    m.drawmeridians(np.arange(-180., 181., 20.))
    m.drawmapboundary(fill_color='black')

    x, y = m(longitude, latitude)

    #m.pcolor(longitude, latitude, data, latlon=True, alpha=0.5)
    m.pcolor(x, y, data, alpha=0.25)

    # See http://stackoverflow.com/questions/4478725/...
    # .../partially-transparent-scatter-plot-but-with-a-solid-color-bar
    color_bar = plt.colorbar(n=2)
    color_bar.set_alpha(1)
    color_bar.set_ticks([0, 39])
    color_bar.set_ticklabels(['missing data', 'ocean'])
    color_bar.draw_all()

    plt.title('{0}\nSnow Cover'.format(FILE_NAME))
    plt.savefig('MOD10_L2.A2000065.0040.005.2008235221207_Snow_Cover_P_m.png')

if __name__ == "__main__":
    run()


