import unittest

import matplotlib.pyplot as plt

import numpy as np
import pkg_resources

from hotdog.lib import hdf as SD
import hotdog


class TestSD(unittest.TestCase):

    def setUp(self):
        self.sdfile = pkg_resources.resource_filename(hotdog.__name__,
                                                       "data/TOMS-EP_L3-TOMSEPL3_2000m0101_v8.HDF")

    def tearDown(self):
        pass

    def test_getrange(self):
        with SD.start(self.sdfile, SD.DFACC_READ) as sdid:
            idx = SD.nametoindex(sdid, 'Reflectivity')
            with SD.select(sdid, idx) as sds_id:
                smax, smin = SD.getrange(sds_id)
                self.assertEqual(smax, 105.0)
                self.assertEqual(smin, -5.0)

    def test_sd(self):
        with SD.start(self.sdfile, SD.DFACC_READ) as sdid:
            idx = SD.nametoindex(sdid, 'Reflectivity')
            with SD.select(sdid, idx) as sds_id:
                info = SD.getinfo(sds_id)
                self.assertEqual(info[0], 'Reflectivity')
                attr_idx = SD.findattr(sds_id, 'long_name')
                attr_name, datatype, count = SD.attrinfo(sds_id, attr_idx)
                long_name = SD.readattr(sds_id, attr_idx)
                self.assertEqual(long_name, 'Effective Surface Reflectivity')
                attr_idx = SD.findattr(sds_id, '_FillValue')
                fv = SD.readattr(sds_id, attr_idx)
                self.assertEqual(fv, 999.0)
                data = SD.readdata(sds_id)
                self.assertEqual(data[0, 0], 999.0)
                self.assertEqual(data[179, 287], 98.0)


if __name__ == "__main__":
    unittest.main()

