import unittest

import matplotlib.pyplot as plt

import numpy as np
import pkg_resources

from hotdog.lib import gd as GD
from hotdog import core
import hotdog


class TestGD(unittest.TestCase):

    def setUp(self):
        self.gridfile = pkg_resources.resource_filename(hotdog.__name__,
                                                        "data/TOMS-EP_L3-TOMSEPL3_2000m0101_v8.HDF")

    def tearDown(self):
        pass

    def test_inqgrid(self):
        gridlist = GD.inqgrid(self.gridfile)
        self.assertEqual(gridlist, ['TOMS Level 3'])

    def test_gridinfo(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                gridsize, upleft, lowright = GD.gridinfo(gridid)
                self.assertEqual(gridsize, (180, 288))
                np.testing.assert_array_equal(upleft,
                                              np.array([-180000000.0,
                                                        90000000.0]))
                np.testing.assert_array_equal(lowright,
                                              np.array([180000000.0,
                                                        -90000000.0]))

    def test_inqfields(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                fields, ranks, numbertypes = GD.inqfields(gridid)
                self.assertEqual(fields,
                                 ['Ozone', 'Reflectivity', 'Aerosol',
                                  'Erythemal'])
                self.assertEqual(ranks, [2, 2, 2, 2])
                self.assertEqual(numbertypes, [core.DFNT_FLOAT] * 4)

    def test_nentries(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                ndims, _ = GD.nentries(gridid, core.HDFE_NENTDIM)
                self.assertEqual(ndims, 2)
                nfields, _ = GD.nentries(gridid, core.HDFE_NENTFLD)
                self.assertEqual(nfields, 4)

    def test_basic(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gdid:
                self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()


