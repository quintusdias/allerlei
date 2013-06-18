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
                print(tifp)

if __name__ == "__main__":
    unittest.main()


