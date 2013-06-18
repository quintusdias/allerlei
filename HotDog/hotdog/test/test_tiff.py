import tempfile
import unittest

import numpy as np
import pkg_resources

from hotdog.lib import tiff as TIFF
import hotdog


class TestTiff(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_basic(self):
        with tempfile.NamedTemporaryFile(suffix=".tif") as tfile:
            with TIFF.open(tfile.name, 'w') as tifp:
                TIFF.setfield(tifp, 'ImageWidth', 1024)
                TIFF.setfield(tifp, 'ImageLength', 1024)
                TIFF.setfield(tifp, 'SamplesPerPixel', 3)
                TIFF.setfield(tifp, 'BitsPerSample', 8)
                TIFF.setfield(tifp, 'PlanarConfiguration', TIFF.PLANARCONFIG_CONTIG)
                TIFF.setfield(tifp, 'PhotometricInterpretation', TIFF.PHOTOMETRIC_RGB)
                TIFF.setfield(tifp, 'TileWidth', 256)
                TIFF.setfield(tifp, 'TileLength', 256)
            import shutil
            shutil.copyfile(tfile.name, '/home/jevans/a.tif')

if __name__ == "__main__":
    unittest.main()


