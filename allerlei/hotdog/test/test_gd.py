import unittest

import matplotlib.pyplot as plt

import numpy as np
import pkg_resources

from allerlei.hotdog.lib import gd as GD
import allerlei


class TestSD(unittest.TestCase):

    def setUp(self):
        self.gridfile = pkg_resources.resource_filename(allerlei.__name__,
                                                        "data/TOMS-EP_L3-TOMSEPL3_2000m0101_v8.HDF")

    def tearDown(self):
        pass

    def test_gd(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()


