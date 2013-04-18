from io import StringIO
import sys
import unittest

import numpy as np

from allerlei import hdf5

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
        for x in dir(hdf5):
            example = getattr(hdf5, x)
            if hasattr(example, 'run'):
                example.run()

        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()

