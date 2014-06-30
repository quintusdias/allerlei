import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset
import numpy as np

# Identify the HDF-EOS2 swath data file.
FILE_NAME = 'MOD29.A2013196.1250.005.2013196195940.hdf'

# Identify the data field.
DATAFIELD_NAME = 'Ice_Surface_Temperature'

rows = slice(2, 2030, 5)
cols = slice(2, 1354, 5)

dset = Dataset(FILE_NAME)
data = dset.variables[DATAFIELD_NAME][rows, cols].astype(np.float64)
units = dset.variables[DATAFIELD_NAME].units
scale = dset.variables[DATAFIELD_NAME].scale_factor
fillvalue = dset.variables[DATAFIELD_NAME]._FillValue
valid_range = dset.variables[DATAFIELD_NAME].valid_range

# Create a masked array out of it.
# Scale factor and add_offset are already applied.
data[data < float(valid_range[0])*scale] = np.nan
data[data > float(valid_range[1])*scale] = np.nan
datam = np.ma.masked_array(data, mask=np.isnan(data))

latitude = dset.variables['Latitude'][:]
longitude = dset.variables['Longitude'][:]

# Draw a polar stereographic projection using the low resolution coastline
# database.
m = Basemap(projection='spstere', resolution='l',
            boundinglat=-64, lon_0 = 0)
m.drawcoastlines(linewidth=0.5)
m.drawparallels(np.arange(-80.,-59,10.))
m.drawmeridians(np.arange(-180.,179.,30.), labels=[True,False,True,True])

x, y = m(longitude, latitude)
m.pcolormesh(x, y, datam, alpha=0.90)
m.colorbar()

fig = plt.gcf()

plt.title('{0} ({1})\n'.format(DATAFIELD_NAME, units))
plt.show()

fig.savefig('MOD10_L2.A2000065.0040.005.2008235221207_Snow_Cover_P_m.png')
