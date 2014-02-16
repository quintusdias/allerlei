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
        intn  SWfieldinfo(int32 swathid, char *fieldname, int32 *rank,
                          int32 dims[], int32 *numbertype, char *dimlist);
        int32 SWnentries(int32 swfid, int32 entrycode, int32 *strbufsize);
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

def inqswath(filename):
    """Retrieve swath structures defined in HDF-EOS file.

    Parameters
    ----------
    swath_id : int
        Swath identifier.

    Returns
    -------
    swathlist : list
        List of swaths defined in HDF-EOS file.

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    strbufsize = ffi.new("int32 *")
    nswaths = _lib.SWinqgrid(filename.encode(), ffi.NULL, strbufsize)
    swathbuffer = ffi.new("char[]", b'\0' * (strbufsize[0] + 1))
    nswaths = _lib.SWinqgrid(filename.encode(), swathbuffer, ffi.NULL)
    _handle_error(nswaths)
    swathlist = ffi.string(swathbuffer).decode('ascii').split(',')
    return swathlist

def nentries(gridid, entry_code):
    """Return number of specified objects in a swath.

    Parameters
    ----------
    swath_id : int
        Swath identifier.
    entry_code : int
        Entry code, either HDFE_NENTDIM or HDFE_NENTDFLD

    Returns
    -------
    nentries, strbufsize : int
       Number of specified entries, number of bytes in descriptive strings. 

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    strbufsize = ffi.new("int32 *")
    nentries = _lib.SWnentries(gridid, entry_code, strbufsize)
    return nentries, strbufsize[0]

@contextmanager
def open(filename, access=DFACC_READ):
    swfid = _lib.SWopen(filename.encode(), access)
    yield swfid
    close(swfid)
