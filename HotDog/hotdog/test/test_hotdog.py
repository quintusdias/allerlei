import os
import sys
import tempfile
import unittest

import numpy as np
import pkg_resources

from hotdog.lib import sd as SD
from hotdog.lib import tiff as TIFF
import hotdog

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

        nrows, ncols = data.shape
        with tempfile.NamedTemporaryFile(suffix=".tif") as tfile:
            with TIFF.open(tfile.name, 'w') as tifp:
                TIFF.setfield(tifp, 'ImageWidth', ncols)
                TIFF.setfield(tifp, 'ImageLength', nrows)
                TIFF.setfield(tifp, 'SamplesPerPixel', 1)
                TIFF.setfield(tifp, 'BitsPerSample', 32)
                TIFF.setfield(tifp, 'PlanarConfiguration', TIFF.PLANARCONFIG_CONTIG)
                TIFF.setfield(tifp, 'PhotometricInterpretation', TIFF.PHOTOMETRIC_MINISBLACK)
                TIFF.setfield(tifp, 'SampleFormat', TIFF.SAMPLEFORMAT_IEEEFP)
                TIFF.setfield(tifp, 'RowsPerStrip', nrows)
                TIFF.writeencodedstrip(tifp, 0, data)
            import shutil
            shutil.copyfile(tfile.name,
                            os.path.join(os.environ['HOME'], 'b.tif'))



if __name__ == "__main__":
    unittest.main()


