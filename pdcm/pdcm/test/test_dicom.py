import unittest
import pdcm
from pdcm import Pdcm

class TestLidcIdri0000(unittest.TestCase):

    def setUp(self):
        self.filename = '/opt/data/dicom/LIDC-IDRI/LIDC-IDRI-0046/1.3.6.1.4.1.14519.5.2.1.6279.6001.189975013581257814721620649088/000000/000000.dcm'

    def test_dicom_prefix(self):
        # Must be DICM
        pdo = Pdcm(self.filename)
        self.assertEqual(pdo['dicom prefix'], b'DICM')

    def test_vr_as(self):
        # AS is an age string.  This example is anonymized to None, though.
        pdo = Pdcm(self.filename)
        self.assertIsNone(pdo['PatientAge'].value)

    def test_vr_cs(self):
        # CS is "code string"
        pdo = Pdcm(self.filename)
        self.assertEqual(pdo['PatientIdentityRemoved'].value, "YES ")

    def test_vr_lo(self):
        # LO is a string.
        pdo = Pdcm(self.filename)
        self.assertEqual(pdo['Manufacturer'].value,
                         'GE MEDICAL SYSTEMS')

    def test_vr_ui(self):
        # must be a UID (string)
        pdo = Pdcm(self.filename)
        expected = '.'.join(['1', '3', '6', '1', '4', '1', '14519', '5', '2',
                             '1', '6279', '6001',
                             '108197977278206587394389018458'])
        self.assertEqual(pdo['StorageMediaFileSetUID'].value, expected)

    def test_vr_us(self):
        # US is unsigned short.
        pdo = Pdcm(self.filename)
        self.assertEqual(pdo['Rows'].value, 2022)


if __name__ == "__main__":
    unittest.main()
