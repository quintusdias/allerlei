import unittest

import numpy as np

from allerlei import hdf5

class TestHdf5Examples(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_all(self):
        # Just run all the examples.
        for x in dir(hdf5):
            example = getattr(hdf5, x)
            if hasattr(example, 'run'):
                example.run()

        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()

