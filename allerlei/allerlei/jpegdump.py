"""Parses a JPEG file, prints out metadata."""

import xml.etree.cElementTree as ET
import io
import struct

info = {
        0xFFC0: ('SOF', 'Start of Frame'),
        0xFFC1: ('SOF', 'Start of Frame'),
        0xFFC2: ('SOF', 'Start of Frame'),
        0xFFC3: ('SOF', 'Start of Frame'),
        0xFFC4: ('DHT', 'Define Huffman Table'),
        0xFFC5: ('SOF', 'Start of Frame'),
        0xFFC6: ('SOF', 'Start of Frame'),
        0xFFC7: ('SOF', 'Start of Frame'),
        0xFFC8: ('SOF', 'Start of Frame'),
        0xFFC9: ('SOF', 'Start of Frame'),
        0xFFCA: ('SOF', 'Start of Frame'),
        0xFFCB: ('SOF', 'Start of Frame'),
        0xFFCC: ('DAC', 'Define Arithmetic coding conditioning'),
        0xFFCD: ('SOF', 'Start of Frame'),
        0xFFCE: ('SOF', 'Start of Frame'),
        0xFFCF: ('SOF', 'Start of Frame'),
        0xFFD0: ('RST', 'Restart with modulo 8 count'),
        0xFFD1: ('RST', 'Restart with modulo 8 count'),
        0xFFD2: ('RST', 'Restart with modulo 8 count'),
        0xFFD3: ('RST', 'Restart with modulo 8 count'),
        0xFFD4: ('RST', 'Restart with modulo 8 count'),
        0xFFD5: ('RST', 'Restart with modulo 8 count'),
        0xFFD6: ('RST', 'Restart with modulo 8 count'),
        0xFFD7: ('RST', 'Restart with modulo 8 count'),
        0xFFD8: ('SOI', 'Start of Image'),
        0xFFD9: ('EOI', 'End of Image'),
        0xFFDA: ('SOS', 'Start of Scan'),
        0xFFDB: ('DQT', 'Define Quantization Table'),
        0xFFDC: ('DNL', 'Define Number of Lines'),
        0xFFDD: ('DRI', 'Define Restart Interval'),
        0xFFDE: ('DHP', 'Define Heirarchical Progression'),
        0xFFDF: ('EXP', 'Expand Reference Component'),
        0xFFE0: ('APP0', 'Application Segment 0'),
        0xFFE1: ('APP1', 'Application Segment 1'),
        0xFFE2: ('APP2', 'Application Segment'),
        0xFFE3: ('APP3', 'Application Segment'),
        0xFFE4: ('APP4', 'Application Segment'),
        0xFFE5: ('APP5', 'Application Segment'),
        0xFFE6: ('APP6', 'Application Segment'),
        0xFFE7: ('APP7', 'Application Segment'),
        0xFFE8: ('APP8', 'Application Segment'),
        0xFFE9: ('APP9', 'Application Segment'),
        0xFFEA: ('APP10', 'Application Segment'),
        0xFFEB: ('APP11', 'Application Segment'),
        0xFFEC: ('APP12', 'Application Segment'),
        0xFFED: ('APP13', 'Application Segment'),
        0xFFEE: ('APP14', 'Application Segment'),
        0xFFEF: ('APP15', 'Application Segment'),
        0xFFF0: ('JPG0', 'Reserved'),
        0xFFF1: ('JPG1', 'Reserved'),
        0xFFF2: ('JPG2', 'Reserved'),
        0xFFF3: ('JPG3', 'Reserved'),
        0xFFF4: ('JPG4', 'Reserved'),
        0xFFF5: ('JPG5', 'Reserved'),
        0xFFF6: ('JPG6', 'Reserved'),
        0xFFF7: ('JPG7', 'Reserved'),
        0xFFF8: ('JPG8', 'Reserved'),
        0xFFF9: ('JPG9', 'Reserved'),
        0xFFFA: ('JPG10', 'Reserved'),
        0xFFFB: ('JPG11', 'Reserved'),
        0xFFFC: ('JPG12', 'Reserved'),
        0xFFFD: ('JPG13', 'Reserved'),
        0xFFFE: ('COM', 'Comment'),
        }

ctype = {
        0: 'unknown',
        1: 'monochrome',
        3: 'RGB',
        4: 'CMYK'
        }

coding_process_map = {
        0XFFC0: 'Sequential',
        0XFFC1: 'Sequential',
        0XFFC2: 'Progressive',
        0XFFC3: 'Lossless',
        0XFFC4: 'Sequential',
        0XFFC5: 'Sequential',
        0XFFC6: 'Progressive',
        0XFFC7: 'Lossless',
        0XFFC8: 'Sequential',
        0XFFC9: 'Sequential',
        0XFFCA: 'Progressive',
        0XFFCB: 'Lossless',
        0XFFCC: 'Sequential',
        0XFFCD: 'Sequential',
        0XFFCE: 'Progressive',
        0XFFCF: 'Lossless',
        }

coding_method_map = {
        0XFFC0: 'Huffman',
        0XFFC1: 'Huffman',
        0XFFC2: 'Huffman',
        0XFFC3: 'Huffman',
        0XFFC4: 'Huffman',
        0XFFC5: 'Huffman',
        0XFFC6: 'Huffman',
        0XFFC7: 'Huffman',
        0XFFC8: 'Huffman',
        0XFFC9: 'Huffman',
        0XFFCA: 'Huffman',
        0XFFCB: 'Huffman',
        0XFFCC: 'Huffman',
        0XFFCD: 'Arithmetic',
        0XFFCE: 'Arithmetic',
        0XFFCF: 'Arithmetic',
        }

def jpegdump(filename, offset=0):
    """Dumps jpeg information."""
    with open(filename, 'rb') as fp:

        fp.seek(offset)

        sig = fp.read(2)
        marker, = struct.unpack('>H', sig)
        dump_segment(marker, fp.tell()-2, 2)

        (marker, segment_length) = recover_valid_marker(fp)
        start_of_segment = fp.tell() - 4

        while True:

            if marker == 0xFFC4 or marker == 0xFFCC:
                # Huffman table or arithmetic coding conditioning (???)
                dump_segment(marker, start_of_segment, segment_length)

            elif marker in range(0xFFC0, 0xFFD0):
                # SOF except for FFC8 or FFCC
                dump_sof_segment(fp, marker, start_of_segment, segment_length)

            elif marker in range(0xFFD0, 0xFFD8):
                print('RST marker 0x%x at %d' % (marker, fp.tell()-2))
                fp.seek(-2, io.SEEK_CUR)

                marker = process_entropy_encoded_segment(fp)
                if marker == 0xFFD9:
                    print('End of Image (EOI) at %d' % fp.tell())
                    return

                (marker, segment_length) = recover_valid_marker(fp)
                start_of_segment = fp.tell() - 4
                continue

            elif marker == 0xFFD9:
                # EOI, we are done
                dump_segment(marker, start_of_segment, segment_length)
                break

            elif marker == 0xFFDA:
                # Start of Scan ==> entropy encoded segment
                dump_segment(marker, start_of_segment, segment_length)

                fp.seek(start_of_segment + segment_length + 2)
                marker = process_entropy_encoded_segment(fp)
                if marker == 0xFFD9:
                    print('End of Image (EOI) at %d' % fp.tell())
                    return
                
                (marker, segment_length) = recover_valid_marker(fp)
                start_of_segment = fp.tell() - 4
                continue

            elif marker in range(0xFFDB, 0xFFDF):
                dump_segment(marker, start_of_segment, segment_length)
                
            elif marker == 0xFFE0:
                dump_app0_segment(fp, marker, start_of_segment, segment_length)
            elif marker == 0xFFE1:
                # App1
                dump_segment(marker, start_of_segment, segment_length)
                process_app1(fp, segment_length)

            elif marker == 0xFFE2:
                # App2
                dump_segment(marker, start_of_segment, segment_length)
                process_app2(fp)

            elif marker in range(0xFFE3, 0xFFEB):
                # APPn
                dump_segment(marker, start_of_segment, segment_length)

            elif marker == 0xFFEC:
                # APP12
                dump_segment(marker, start_of_segment, segment_length)
                x = fp.read(segment_length - 2)
                print('    %s' % x)

            elif marker == 0xFFED:
                # APP13
                dump_segment(marker, start_of_segment, segment_length)

            elif marker == 0xFFEE:
                # APP14
                dump_segment(marker, start_of_segment, segment_length)
                x = fp.read(segment_length - 2)
                if x[0:6] == 'Adobe' + '\x00':
                    print('    Adobe:')

            elif marker == 0xFFEF:
                # APP15
                dump_segment(marker, start_of_segment, segment_length)

            elif marker in range(0xFFF0, 0xFFFE):
                # JPGn
                dump_segment(marker, start_of_segment, segment_length)

            elif marker == 0xFFFE:
                # COM marker
                dump_segment(marker, start_of_segment, segment_length)
                comment = f.read(segment_length-2)
                print('    %s' % comment)

            # Seek to the start of the next marker.
            fp.seek(start_of_segment + segment_length + 2)

            (marker, segment_length) = recover_valid_marker(fp)
            start_of_segment = fp.tell() - 4

def process_entropy_encoded_segment(f):
    """See B.1.1.5 of Rec. T.81."""
    print("    Entropy encoded segment starting at %d" % f.tell())

    no_marker = True
    y = ''
    while no_marker:
        x = f.read(1)
        while x != b'\xff':
            x = f.read(1)

        y = f.read(1)
        if y == b'\x00':
            continue
        else:
            no_marker = False

    # Backtrack to the start of the marker.
    f.seek(-2, io.SEEK_CUR)
    print('    Entropy encoded segment ending at %d' % f.tell())

    marker, = struct.unpack('>H', b'\xff' + y)
    return marker


def dump_segment(marker, pos, length):
    """Print what we know about this segment."""
    print("%s marker 0x%x (%s) at %d, %d" % (info[marker][0], marker,
        info[marker][1], pos, length)) 

def recover_valid_marker(f):
    """Recover the next marker identifying a segment."""

    recognized_markers = range(0xFFC0, 0xFFFF)

    start_of_segment = f.tell()
    x = f.read(2)
    marker = struct.unpack('>H', x)[0]
    if marker == 0xFFD9:
        # End-Of-Image, so there's no segment length to retrieve.
        return (marker, 0)

    x = f.read(2)
    marker_length = struct.unpack('>H', x)[0]

    invalid_marker = False

    while not ((marker in recognized_markers) and (marker_length != 0)):
        if marker == 0xFFFF:
            f.seek(f.tell()-2)
            x = '\xff'
            while x == '\xff':
                # Swallow the padded bytes.
                x = f.read(1)

            marker = struct.unpack('>H', x + '\xff')
            x = f.read(2)
            marker_length = struct.unpack('>H', x)
            continue

        # marker or marker length must be invalid.  Try to find the next valid
        # marker by seeking ahead byte-by-byte.
        invalid_marker = True
        f.seek(f.tell() - 2)
        x = f.read(1)
        while x != '\xff':
            x = f.read(1)

        y = f.read(1)
        marker = struct.unpack('>H', y + x)
        x = f.read(2)
        marker_length = struct.unpack('>H', x)

    if invalid_marker:
        raise RuntimeError("invalid marker???")

    return marker, marker_length

def process_app1(f, segment_length):
    """Process the APP1 segment."""
    start = f.tell()
    x = f.read(6)
    if x[0:6] == b'Exif\x00\x00':
        print('    APP1 type:  Exif')
    elif x[0:5] == b'G3FAX':
        print('    APP1 type:  G3Fax')
    else:
        f.seek(start)
        x = f.read(29)
        if x[0:28] == b'http://ns.adobe.com/xap/1.0/':
            print('    APP1 type:  XMP')
            s = f.read(segment_length - 29)
            print(s)
        else:
            print('    APP1 type:  unknown')

def process_app2(f):
    """Process the APP2 segment."""
    x = f.read(12)
    if x[0:11] == 'ICC_PROFILE':
        x = f.read(1)
        num_chunks = struct.unpack('>B', x)
        print('    APP2 type:  ICC_PROFILE (chunk number %d)' % num_chunks)
    else:
        print('    APP2 type:  unknown')

def dump_app0_segment(f, marker, start_of_segment, segment_length):
    """Dump APP0 information.

    Raises:
        RuntimeError

    Reference:
        http://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
    """
    dump_segment(marker, start_of_segment, segment_length)

    # Identifier
    x = f.read(5)
    if x[0:4] == 'JFIF':
        buf = f.read(9)
        fmt = '>BBBHHBB'
        (major, minor, units, xden, yden, tw, th) = struct.unpack('>BBBHHBB', buf)
        print('    JFIF:') 
        print('        Version:  %d.%d' % (major, minor))

        density = {0: 'none', 1: 'inches', 2: 'centimeters'}
        print('        Density units:  %s' % density[units])
        print('        X Density:  %d' % xden)
        print('        Y Density:  %d' % yden)
        print('        Thumbnail size:  %d x %d' % (th, tw))
    elif x[0:4] == 'JFXX':
        print('    JXFF:')
        x = f.read(1)
        thumbnail_desc = {'0x10':  'JPEG',
                '0x11':  '1 byte per pixel palettised',
                '0x13':  '3 byte per pixel RGB'}
        print('        Format:  %s' % thumbnail_desc[x])

def dump_sof_segment(fp, marker, start_of_segment, segment_length):
    """Dump Start of Frame segment"""
    dump_segment(marker, start_of_segment, segment_length)
    x = fp.read(6)
    (P, Y, X, Nf) = struct.unpack('>BHHB', x)
    print('    Size:  %d x %d' % (Y, X))
    print('    Color:  %s' % ctype[Nf])
    print('    Bits per Sample:  %d' % P)
    print('    Samples per Pixel:  %d' % Nf)
    print('    Coding process:  %s' % coding_process_map[marker])
    print('    Coding method:  %s' % coding_method_map[marker])

if __name__ == "__main__":
    import sys
    jpegdump(sys.argv[1])
