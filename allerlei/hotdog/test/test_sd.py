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
        sdid = SD.start(self.sdfile, SD.DFACC_READ)
        vals = SD.fileinfo(sdid)
        sds_id = SD.select(sdid, 3)
        info = SD.getinfo(sds_id)
        print(info[0])
        attr_idx = SD.findattr(sds_id, 'long_name')
        attr_name, datatype, count = SD.attrinfo(sds_id, attr_idx)
        long_name = SD.readattr(sds_id, attr_idx)
        attr_idx = SD.findattr(sds_id, '_FillValue')
        fv = SD.readattr(sds_id, attr_idx)
        data = SD.readdata(sds_id)
        self.assertEqual(data[0, 0], 999.0)
        self.assertEqual(data[179, 287], 98.0)
        SD.endaccess(sds_id)
        SD.end(sdid)


if __name__ == "__main__":
    unittest.main()
