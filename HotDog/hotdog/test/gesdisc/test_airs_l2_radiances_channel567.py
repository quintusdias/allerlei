import os
import unittest

from hotdog.lib import sw as SW

try:
    DATA_ROOT = os.environ['EOSDATAROOT']
except KeyError:
    DATA_ROOT = None

@unittest.skipIf(DATA_ROOT is None, "No dataroot set.")
class TestGESDISC(unittest.TestCase):

    def setUp(self):
        self.swathfile = os.path.join(DATA_ROOT, 
                                      "AIRS.2002.12.31.001.L2.CC_H.v4.0.21.0.G06100185050.hdf")
        self.swathname = 'L2_Standard_cloud-cleared_radiance_product'

    def tearDown(self):
        pass

    def test_airs_l2_radiances_channel567(self):
        with SW.open(self.swathfile) as swfid:
            with SW.attach(swfid, self.swathname) as swath_id:
                self.assertTrue(True)

