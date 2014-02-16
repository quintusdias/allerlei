import unittest

import matplotlib.pyplot as plt

import numpy as np
import pkg_resources

from hotdog.lib import gd as GD
from hotdog import core
import hotdog


class TestGD(unittest.TestCase):

    def setUp(self):
        relpath = "data/TOMS-EP_L3-TOMSEPL3_2000m0101_v8.HDF"
        self.gridfile = pkg_resources.resource_filename(hotdog.__name__,
                                                        relpath)

    def tearDown(self):
        pass

    def test_inqgrid(self):
        gridlist = GD.inqgrid(self.gridfile)
        self.assertEqual(gridlist, ['TOMS Level 3'])

    def test_readfield(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                data = GD.readfield(gridid, 'Reflectivity')

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

    def test_ij2ll(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                projcode, zonecode, spherecode, projparms = GD.projinfo(gridid)
                (nrow, ncol), upleft, lowright = GD.gridinfo(gridid)
                pixcen = GD.pixreginfo(gridid)
                pixcnr = GD.origininfo(gridid)

                row = np.array([[0, 0], [179, 179]], np.int32)
                col = np.array([[0, 287], [287, 0]], np.int32)
                lon, lat = GD.ij2ll(projcode, zonecode, projparms, spherecode,
                                    ncol, nrow, upleft, lowright, row, col,
                                    pixcen, pixcnr)
                np.testing.assert_array_equal(lon, 
                                              np.array([[-179.375, 179.375],
                                                        [179.375, -179.375]]))
                np.testing.assert_array_equal(lat, 
                                              np.array([[89.5, 89.5],
                                                        [-89.5, -89.5]]))
                    

    def test_origininfo(self):
        # Verify GDorigininfo
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                origincode = GD.origininfo(gridid)
                self.assertEqual(origincode, core.HDFE_GD_UL)

    def test_pixreginfo(self):
        # Verify GDpixreginfo
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                pixregcode = GD.pixreginfo(gridid)
                self.assertEqual(pixregcode, core.HDFE_CENTER)

    def test_projinfo(self):
        # Verify GDprojinfo
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                projcode, zonecode, spherecode, projparms = GD.projinfo(gridid)
                self.assertEqual(projcode, 0)
                self.assertEqual(zonecode, -1)
                self.assertEqual(spherecode, 0)
                np.testing.assert_array_equal(projparms,
                                              np.zeros(13, dtype=np.float64));

    def test_inqfields(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                fields, ranks, numbertypes = GD.inqfields(gridid)
                self.assertEqual(fields,
                                 ['Ozone', 'Reflectivity', 'Aerosol',
                                  'Erythemal'])
                self.assertEqual(ranks, [2, 2, 2, 2])
                self.assertEqual(numbertypes, [core.DFNT_FLOAT] * 4)

    def test_inqdims(self):
        with GD.open(self.gridfile, GD.DFACC_READ) as gdfid:
            with GD.attach(gdfid, 'TOMS Level 3') as gridid:
                dims, dimsizes = GD.inqdims(gridid)
                self.assertEqual(dims,("XDim", "YDim"))
                self.assertEqual(dimsizes, (288, 180))

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


