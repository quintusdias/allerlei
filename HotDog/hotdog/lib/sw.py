from contextlib import contextmanager
import pkg_resources
import numpy as np
from cffi import FFI

from ..core import DFACC_READ, HDFE_NENTFLD, HDFE_NENTDIM

ffi = FFI()
ffi.cdef("""
        typedef int int32;
        typedef int intn;
        typedef double float64;

        int32 SWattach(int32 swfid, char *swathname);
        intn  SWdetach(int32 swfid);
        intn  SWclose(int32 fid);
        int32 SWopen(char *name, intn access);
        """)
_lib = ffi.verify("""
        #include "mfhdf.h"
        #include "HE2_config.h"
        #include "HdfEosDef.h"
        """,
        libraries=['hdfeos', 'Gctp', 'mfhdf', 'df', 'jpeg', 'z'],
        include_dirs=['/usr/include/hdf', '/opt/local/include'],
        library_dirs=['/usr/lib/hdf', '/opt/local/lib'])

def _handle_error(status):
    if status < 0:
        raise IOError("Library routine failed.")

@contextmanager
def attach(swfid, swathname):
    """Attach to an existing swath structure.

    Parameters
    ----------
    swfid : int
        Swath file id.
    swathname : str
        Name of swath to which we wish to attach.

    Returns
    -------
    swath_id : int
        Swath identifier.

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    swid = _lib.SWattach(swfid, swathname.encode())
    yield swid
    detach(swid)

def close(swfid):
    """Close an HDF-EOS file.

    Parameters
    ----------
    fid : int
        Grid file id.

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    status = _lib.SWclose(swfid)
    _handle_error(status)

def detach(swath_id):
    """Detach from grid structure.

    Parameters
    ----------
    swath_id : int
        Grid identifier.

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    status = _lib.SWdetach(swath_id)
    _handle_error(status)

@contextmanager
def open(filename, access=DFACC_READ):
    swfid = _lib.SWopen(filename.encode(), access)
    yield swfid
    close(swfid)
