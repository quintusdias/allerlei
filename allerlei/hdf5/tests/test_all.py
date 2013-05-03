import sys
if sys.hexversion < 0x03000000:
    from StringIO import StringIO
else:
    from io import StringIO

import unittest

import numpy as np
import pkg_resources

import allerlei

class TestHdf5Examples(unittest.TestCase):

    def setUp(self):
        # Save sys.stdout.
        self.stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        # Restore stdout.
        sys.stdout = self.stdout

    def test_all(self):
        # Just run all the examples.
        for x in dir(allerlei.hdf5):
            example = getattr(allerlei.hdf5, x)
            if hasattr(example, 'run'):
                
                # Szip not available on my machine.
                if x == 'h5ex_d_szip':
                    with self.assertRaises(RuntimeError):
                        example.run()
                elif x == 'h5ex_g_visit':
                    hdf5file = pkg_resources.resource_filename(allerlei.__name__,
                                                               "data/h5ex_g_visit.h5")

                else:
                    example.run()


        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()

