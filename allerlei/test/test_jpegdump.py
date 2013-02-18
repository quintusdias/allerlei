from io import StringIO
import pkg_resources
import sys
import unittest

import allerlei
from allerlei import jpegdump

class TestJpegDump(unittest.TestCase):

    def setUp(self):
        self.jpgfile = pkg_resources.resource_filename(allerlei.__name__,
                                                       "data/CoyotePack2.jpg")
        # Save sys.stdout.
        self.stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        # Restore stdout.
        sys.stdout = self.stdout

    def test_jpegdump(self):
        jpegdump(self.jpgfile)
        actual = sys.stdout.getvalue().strip()
        lines = ['SOI marker 0xffd8 (Start of Image) at 0, 2',
                 'APP0 marker 0xffe0 (Application Segment 0) at 2, 16',
                 'APP1 marker 0xffe1 (Application Segment 1) at 20, 3303',
                 '    APP1 type:  unknown',
                 'APP2 marker 0xffe2 (Application Segment) at 3325, 3160',
                 '    APP2 type:  unknown',
                 'DQT marker 0xffdb (Define Quantization Table) at 6487, 67',
                 'DQT marker 0xffdb (Define Quantization Table) at 6556, 67',
                 'SOF marker 0xffc0 (Start of Frame) at 6625, 17',
                 '    Size:  832 x 1114',
                 '    Color:  RGB',
                 '    Bits per Sample:  8',
                 '    Samples per Pixel:  3',
                 '    Coding process:  Sequential',
                 '    Coding method:  Huffman',
                 'DHT marker 0xffc4 (Define Huffman Table) at 6644, 31',
                 'DHT marker 0xffc4 (Define Huffman Table) at 6677, 181',
                 'DHT marker 0xffc4 (Define Huffman Table) at 6860, 31',
                 'DHT marker 0xffc4 (Define Huffman Table) at 6893, 181',
                 'SOS marker 0xffda (Start of Scan) at 7076, 12',
                 '    Entropy encoded segment starting at 7090',
                 '    Entropy encoded segment ending at 992743',
                 'End of Image (EOI) at 992743']
        expected = "\n".join(lines)
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()

