from contextlib import contextmanager
import numpy as np
from cffi import FFI

ffi = FFI()
ffi.cdef("""
        typedef ... TIFF;
        void TIFFClose(TIFF *tif);
        extern TIFF* TIFFOpen(const char*, const char*);
        extern int TIFFSetField(TIFF*, uint32_t, ...);
        """)
_lib = ffi.verify("""
        #include "tiffio.h"
        """,
        libraries=['tiff', 'jpeg', 'z'],
        include_dirs=['/usr/include/hdf', '/opt/local/include'],
        library_dirs=['/opt/local/lib'])

tags_int16 = ['PhotometricInterpretation', 'PlanarConfiguration']
tags_int32 = ['BitsPerSample', 'ImageWidth', 'ImageLength', 'SamplesPerPixel',
              'TileWidth', 'TileLength']
tagnumber = {'ImageWidth': 256,
             'ImageLength': 257,
             'BitsPerSample': 258,
             'PhotometricInterpretation': 262,
             'SamplesPerPixel': 277,
             'PlanarConfiguration': 284,
             'TileWidth': 322,
             'TileLength': 323}

PLANARCONFIG_CONTIG = 1
PLANARCONFIG_SEPARATE = 2

PHOTOMETRIC_RGB = 2

def _handle_error(status):
    if status < 0:
        raise IOError("Library routine failed.")

@contextmanager
def open(filename, mode='r'):
    tiffp = _lib.TIFFOpen(filename.encode(), mode.encode())
    yield tiffp
    _lib.TIFFClose(tiffp)

def setfield(tifp, tagname, *args):
    if tagname in tags_int16:
        value = ffi.cast("short", args[0])
        status = _lib.TIFFSetField(tifp, tagnumber[tagname], value);
    elif tagname in tags_int32:
        value = ffi.cast("int", args[0])
        status = _lib.TIFFSetField(tifp, tagnumber[tagname], value);
    else:
        raise NotImplementedError("Unrecognized tag.")

    _handle_error(status)

def close(tiffp):
    _lib.TIFFclose(tiffp)

if __name__ == "__main__":
    pass
