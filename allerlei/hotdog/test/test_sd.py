import unittest

import matplotlib.pyplot as plt

import numpy as np
import pkg_resources

from allerlei.hotdog.lib import hdf as SD
import allerlei


class TestSD(unittest.TestCase):

    def setUp(self):
        self.sdfile = pkg_resources.resource_filename(allerlei.__name__,
                                                       "data/TOMS-EP_L3-TOMSEPL3_2000m0101_v8.HDF")

    def tearDown(self):
        pass

    def test_sd(self):
        with SD.start(self.sdfile, SD.DFACC_READ) as sdid:
            vals = SD.fileinfo(sdid)
            with SD.select(sdid, 3) as sds_id:
                info = SD.getinfo(sds_id)
                self.assertEqual(info[0], 'Reflectivity')
                attr_idx = SD.findattr(sds_id, 'long_name')
                attr_name, datatype, count = SD.attrinfo(sds_id, attr_idx)
                long_name = SD.readattr(sds_id, attr_idx)
                self.assertEqual(long_name, 'Effective Surface Reflectivity')
                attr_idx = SD.findattr(sds_id, '_FillValue')
                fv = SD.readattr(sds_id, attr_idx)
                data = SD.readdata(sds_id)
                self.assertEqual(data[0, 0], 999.0)
                self.assertEqual(data[179, 287], 98.0)
                SD.endaccess(sds_id)


if __name__ == "__main__":
    unittest.main()

