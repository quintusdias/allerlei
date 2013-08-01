import pkg_resources
import unittest

import coos

class TestRadials(unittest.TestCase):

    def setUp(self):
        relfile = "data/RDLm_GMNB_2009_12_16_0000.ruv"
        fullfile = pkg_resources.resource_filename(coos.__name__, relfile)
        self.grand_manan_file = fullfile
        pass

    def tearDown(self):
        pass

    def test_write_netcdf(self):
        # Should be able to parse and write as netcdf.
        ruv = coos.CodarRadials()
        ruv.parse_ascii(self.grand_manan_file)
        pass

if __name__ == "__main__":
    unittest.main()

