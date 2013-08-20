import unittest
import pdcm
from pdcm import Pdcm

class TestLidcIdri0000(unittest.TestCase):

    def setUp(self):
        self.filename = '/opt/data/dicom/LIDC-IDRI/LIDC-IDRI-0046/1.3.6.1.4.1.14519.5.2.1.6279.6001.189975013581257814721620649088/000000/000000.dcm'

    def test_dicom_prefix(self):
        pdo = Pdcm(self.filename)
        self.assertEqual(pdo['dicom prefix'], b'DICM')


if __name__ == "__main__":
    unittest.main()
