from contextlib import contextmanager
import numpy as np
from cffi import FFI

ffi = FFI()
ffi.cdef("""
        typedef ... TIFF;
        extern TIFF* TIFFOpen(const char*, const char*);
        void TIFFClose(TIFF *tif);
        """)
_lib = ffi.verify("""
        #include "tiffio.h"
        """,
        libraries=['tiff', 'jpeg', 'z'],
        include_dirs=['/usr/include/hdf', '/opt/local/include'],
        library_dirs=['/opt/local/lib'])

def _handle_error(status):
    if status < 0:
        raise IOError("Library routine failed.")

@contextmanager
def open(filename, mode='r'):
    tiffp = _lib.TIFFOpen(filename.encode(), mode.encode())
    yield tiffp
    _lib.TIFFClose(tiffp)

def close(tiffp):
    _lib.TIFFclose(tiffp)

if __name__ == "__main__":
    pass
