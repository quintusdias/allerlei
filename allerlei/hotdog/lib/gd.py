from contextlib import contextmanager
import pkg_resources
import numpy as np
from cffi import FFI

DFACC_READ = 1

ffi = FFI()
ffi.cdef("""
        typedef int int32;
        typedef int intn;

        int32 GDopen(char *name, intn access);
        intn  GDclose(int32 fid);
        """)
_lib = ffi.verify("""
        #include "mfhdf.h"
        #include "HE2_config.h"
        #include "HdfEosDef.h"
        """,
        libraries=['hdfeos', 'Gctp', 'mfhdf', 'df', 'jpeg', 'z'],
        include_dirs=['/opt/hdfeos2/include', '/usr/include/hdf', '/opt/local/include'],
        library_dirs=['/opt/hdfeos2/lib', '/usr/lib/hdf', '/opt/local/lib'])

def _handle_error(status):
    if status < 0:
        raise IOError("Library routine failed.")

@contextmanager
def open(filename, access=DFACC_READ):
    gdfid = _lib.GDopen(filename.encode(), access)
    yield gdfid
    _lib.GDclose(gdfid)

def close(gdfid):
    status = _lib.GDclose(gdfid)
    return status
