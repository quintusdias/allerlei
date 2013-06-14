import sys
import tempfile
import unittest

import numpy as np
import pkg_resources

try:
    import gdal
except ImportError:
    pass

from hotdog.lib import sd as SD
import hotdog

@unittest.skipIf('gdal' not in sys.modules, "gdal-python is not installed")
class TestGdal(unittest.TestCase):

    def setUp(self):
        self.sdfile = pkg_resources.resource_filename(hotdog.__name__,
                                                       "data/TOMS-EP_L3-TOMSEPL3_2000m0101_v8.HDF")

    def tearDown(self):
        pass

    def test_basic(self):
        with SD.start(self.sdfile, SD.DFACC_READ) as sdid:
            idx = SD.nametoindex(sdid, 'Reflectivity')
            with SD.select(sdid, idx) as sds_id:
                data = SD.readdata(sds_id)

        driver = gdal.GetDriverByName('GTiff')
        with tempfile.NamedTemporaryFile(suffix=".tif") as tfile:
            dst_ds = driver.Create(tfile.name, data.shape[1], data.shape[0], 1,
                                   gdal.GDT_FLOAT32)
            #dst_ds.SetGeoTransform([

if __name__ == "__main__":
    unittest.main()

