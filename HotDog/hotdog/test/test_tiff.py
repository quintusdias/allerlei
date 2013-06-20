import os
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

    def test_xmp(self):
        data = np.zeros((256, 256, 3), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(suffix=".tif") as tfile:
            with TIFF.open(tfile.name, 'w') as tifp:
                TIFF.setfield(tifp, 'ImageWidth', 256)
                TIFF.setfield(tifp, 'ImageLength', 256)
                TIFF.setfield(tifp, 'RowsPerStrip', 256)
                TIFF.setfield(tifp, 'SamplesPerPixel', 3)
                TIFF.setfield(tifp, 'BitsPerSample', 8)
                TIFF.setfield(tifp, 'PlanarConfiguration', TIFF.PLANARCONFIG_CONTIG)
                TIFF.setfield(tifp, 'PhotometricInterpretation', TIFF.PHOTOMETRIC_RGB)
                TIFF.setfield(tifp, 'SampleFormat', TIFF.SAMPLEFORMAT_IEEEFP)
                TIFF.setfield(tifp, 'XMLPacket', 'This is a test')
                TIFF.writeencodedstrip(tifp, 0, data)
            import shutil
            shutil.copyfile(tfile.name,
                            os.path.join(os.environ['HOME'], 'b.tif'))

    def test_basic(self):
        with tempfile.NamedTemporaryFile(suffix=".tif") as tfile:
            with TIFF.open(tfile.name, 'w') as tifp:
                TIFF.setfield(tifp, 'ImageWidth', 1024)
                TIFF.setfield(tifp, 'ImageLength', 1024)
                TIFF.setfield(tifp, 'SamplesPerPixel', 1)
                TIFF.setfield(tifp, 'BitsPerSample', 32)
                TIFF.setfield(tifp, 'PlanarConfiguration', TIFF.PLANARCONFIG_CONTIG)
                TIFF.setfield(tifp, 'PhotometricInterpretation',
                              TIFF.PHOTOMETRIC_MINISBLACK)
                TIFF.setfield(tifp, 'SampleFormat', TIFF.SAMPLEFORMAT_IEEEFP)
                TIFF.setfield(tifp, 'TileWidth', 512)
                TIFF.setfield(tifp, 'TileLength', 512)
                data = np.zeros((512, 512), dtype=np.float32)
                TIFF.writetile(tifp, data, 0, 0)
                TIFF.writetile(tifp, data, 512, 0)
                TIFF.writetile(tifp, data, 0, 512)
                TIFF.writetile(tifp, data, 512, 512)
            import shutil
            shutil.copyfile(tfile.name,
                            os.path.join(os.environ['HOME'], 'a.tif'))

if __name__ == "__main__":
    unittest.main()


