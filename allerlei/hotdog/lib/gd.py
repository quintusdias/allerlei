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
        int32 GDattach(int32 gdfid, char *grid);
        intn  GDdetach(int32 gid);
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
def attach(gdfid, gridname):
    """Attach to an existing grid structure.

    Parameters
    ----------
    gdfid : int
        Grid file id.
    gridname : str
        Name of grid to be attached.

    Returns
    -------
    grid_id : int
        Grid identifier.

    Raises
    ------
    IOError if associated library routine fails.
    """
    gdid = _lib.GDattach(gdfid, gridname.encode())
    yield gdid
    detach(gdid)

def close(gdfid):
    """Close an HDF-EOS file.

    Parameters
    ----------
    fid : int
        Grid file id.

    Raises
    ------
    IOError if associated library routine fails.
    """
    status = _lib.GDclose(gdfid)
    _handle_error(status)

def detach(grid_id):
    """Detach from grid structure.

    Parameters
    ----------
    grid_id : int
        Grid identifier.

    Raises
    ------
    IOError if associated library routine fails.
    """
    status = _lib.GDdetach(grid_id)
    _handle_error(status)

@contextmanager
def open(filename, access=DFACC_READ):
    gdfid = _lib.GDopen(filename.encode(), access)
    yield gdfid
    close(gdfid)

