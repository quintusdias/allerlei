from contextlib import contextmanager
import pkg_resources
import numpy as np
from cffi import FFI

from ..core import DFACC_READ, HDFE_NENTFLD

ffi = FFI()
ffi.cdef("""
        typedef int int32;
        typedef int intn;
        typedef double float64;

        int32 GDattach(int32 gdfid, char *grid);
        intn  GDdetach(int32 gid);
        intn  GDclose(int32 fid);
        int32 GDinqfields(int32 gridid, char *fieldlist, int32 rank[],
                          int32 numbertype[]);
        int32 GDinqgrid(char *filename, char *gridlist, int32 *strbufsize);
        int32 GDnentries(int32 gridid, int32 entrycode, int32 *strbufsize);
        intn  GDgridinfo(int32 gridid, int32 *xdimsize, int32 *ydimsize,
                         float64 upleft[2], float64 lowright[2]);
        int32 GDopen(char *name, intn access);
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

def gridinfo(grid_id):
    """Return information about a grid structure.

    Parameters
    ----------
    grid_id : int
        Grid identifier.

    Returns
    -------
    gridsize : tuple
        Number of rows, columns in grid.
    upleft, lowright : np.float64[2]
        Location in meters of upper left, lower right corners.

    Raises
    ------
    IOError if associated library routine fails.
    """
    xdimsize = ffi.new("int32 *")
    ydimsize = ffi.new("int32 *")
    upleft_buffer = ffi.new("float64[]", 2)
    lowright_buffer = ffi.new("float64[]", 2)
    status = _lib.GDgridinfo(grid_id, xdimsize, ydimsize,
                             upleft_buffer, lowright_buffer)
    _handle_error(status)

    gridsize = (ydimsize[0], xdimsize[0])

    upleft = np.zeros(2, dtype=np.float64)
    upleft[0] = upleft_buffer[0]
    upleft[1] = upleft_buffer[1]

    lowright = np.zeros(2, dtype=np.float64)
    lowright[0] = lowright_buffer[0]
    lowright[1] = lowright_buffer[1]

    return gridsize, upleft, lowright

def inqfields(gridid):
    """Retrieve information about data fields defined in a grid.

    Returns
    -------
    fields : list
        List of fields in the grid.
    ranks : list
        List of ranks corresponding to the fields
    numbertypes : list
        List of numbertypes corresponding to the fields

    Raises
    ------
    IOError if associated library routine fails.
    """
    nfields, strbufsize = nentries(gridid, HDFE_NENTFLD)
    fieldlist_buffer = ffi.new("char[]", b'\0' * (strbufsize + 1))
    rank_buffer = ffi.new("int[]", nfields)
    numbertype_buffer = ffi.new("int[]", nfields)
    nfields2 = _lib.GDinqfields(gridid, fieldlist_buffer,
                                rank_buffer, numbertype_buffer)
    fieldlist = ffi.string(fieldlist_buffer).decode('ascii').split(',')

    ranks = []
    numbertypes = []
    for j in range(len(fieldlist)):
        ranks.append(rank_buffer[j])
        numbertypes.append(numbertype_buffer[j])

    return fieldlist, ranks, numbertypes

def inqgrid(filename):
    """Retrieve grid structures defined in HDF-EOS file.

    Parameters
    ----------
    grid_id : int
        Grid identifier.

    Returns
    -------
    gridlist : list
        List of grids defined in HDF-EOS file.

    Raises
    ------
    IOError if associated library routine fails.
    """
    strbufsize = ffi.new("int32 *")
    ngrids = _lib.GDinqgrid(filename.encode(), ffi.NULL, strbufsize)
    gridbuffer = ffi.new("char[]", b'\0' * (strbufsize[0] + 1))
    ngrids = _lib.GDinqgrid(filename.encode(), gridbuffer, ffi.NULL)
    _handle_error(ngrids)
    gridlist = ffi.string(gridbuffer).decode('ascii').split(',')
    return gridlist

def nentries(gridid, entry_code):
    """Return number of specified objects in a grid.

    Parameters
    ----------
    grid_id : int
        Grid identifier.
    entry_code : int
        Entry code, either HDFE_NENTDIM or HDFE_NENTDFLD

    Returns
    -------
    nentries, strbufsize : tuple of ints
       Number of specified entries, number of bytes in descriptive strings. 

    Raises
    ------
    IOError if associated library routine fails.
    """
    strbufsize = ffi.new("int32 *")
    nentries = _lib.GDnentries(gridid, entry_code, strbufsize)
    return nentries, strbufsize[0]

@contextmanager
def open(filename, access=DFACC_READ):
    gdfid = _lib.GDopen(filename.encode(), access)
    yield gdfid
    close(gdfid)

