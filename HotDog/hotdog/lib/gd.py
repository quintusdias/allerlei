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
        int32 GDij2ll(int32 projcode, int32 zonecode,
                      float64 projparm[], int32 spherecode, int32 xdimsize,
                      int32 ydimsize, float64 upleft[], float64 lowright[],
                      int32 npts, int32 row[], int32 col[], float64
                      longititude[], float64 latitude[], int32 pixcen,
                      int32 pixcnr);
        int32 GDinqfields(int32 gridid, char *fieldlist, int32 rank[],
                          int32 numbertype[]);
        int32 GDinqgrid(char *filename, char *gridlist, int32 *strbufsize);
        int32 GDnentries(int32 gridid, int32 entrycode, int32 *strbufsize);
        intn  GDgridinfo(int32 gridid, int32 *xdimsize, int32 *ydimsize,
                         float64 upleft[2], float64 lowright[2]);
        int32 GDopen(char *name, intn access);
        intn  GDorigininfo(int32 gridid, int32 *origincode);
        intn  GDpixreginfo(int32 gridid, int32 *pixregcode);
        intn  GDprojinfo(int32 gridid, int32 *projcode, int32 *zonecode,
                         int32 *spherecode, float64 projparm[]);
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
    IOError
        If associated library routine fails.
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
    IOError
        If associated library routine fails.
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
    IOError
        If associated library routine fails.
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
    IOError
        If associated library routine fails.
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

def ij2ll(projcode, zonecode, projparm, spherecode, xdimsize, ydimsize, upleft,
          lowright, row, col, pixcen, pixcnr):
    """Convert coordinates (i, j) to (longitude, latitude).

    Parameters
    ----------
    projcode : int
        GCTP projection code
    zonecode : int
        GCTP zone code used by UTM projection
    projparm : ndarray
        Projection parameters.
    spherecode : int
        GCTP spherecode
    xdimsize, ydimsize : int
        Size of grid.
    upleft, lowright : ndarray
        Upper left, lower right corner of the grid in meter (all projections
        except Geographic) or DMS degree (Geographic).
    row, col : ndarray
        row, column numbers of the pixels (zero based)

    Returns
    -------
    longitude, latitude : ndarray
        Longitude and latitude in decimal degrees.

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    longitude = np.zeros(col.shape, dtype=np.float64)
    latitude = np.zeros(col.shape, dtype=np.float64)
    upleftp = ffi.cast("float64 *", upleft.ctypes.data)
    lowrightp = ffi.cast("float64 *", lowright.ctypes.data)
    projparmp = ffi.cast("float64 *", projparm.ctypes.data)
    colp = ffi.cast("int32 *", col.ctypes.data)
    rowp = ffi.cast("int32 *", row.ctypes.data)
    longitudep = ffi.cast("float64 *", longitude.ctypes.data)
    latitudep = ffi.cast("float64 *", latitude.ctypes.data)
    status = _lib.GDij2ll(projcode, zonecode, projparmp, spherecode,
                          xdimsize, ydimsize, upleftp, lowrightp, col.size,
                          rowp, colp, longitudep, latitudep, pixcen, pixcnr)
    return longitude, latitude

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
    IOError
        If associated library routine fails.
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
    IOError
        If associated library routine fails.
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
    IOError
        If associated library routine fails.
    """
    strbufsize = ffi.new("int32 *")
    nentries = _lib.GDnentries(gridid, entry_code, strbufsize)
    return nentries, strbufsize[0]

@contextmanager
def open(filename, access=DFACC_READ):
    gdfid = _lib.GDopen(filename.encode(), access)
    yield gdfid
    close(gdfid)

def origininfo(grid_id):
    """Return grid pixel origin information.

    Parameters
    ----------
    grid_id : int
        Grid identifier.

    Returns
    -------
    origincode : int
        Origin code.

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    origincode = ffi.new("int32 *")
    status = _lib.GDorigininfo(grid_id, origincode)
    _handle_error(status)

    return origincode[0]

def pixreginfo(grid_id):
    """Return pixel registration information.

    Parameters
    ----------
    grid_id : int
        Grid identifier.

    Returns
    -------
    pixregcode : int
        Pixel registration code.

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    pixregcode = ffi.new("int32 *")
    status = _lib.GDpixreginfo(grid_id, pixregcode)
    _handle_error(status)

    return pixregcode[0]

def projinfo(grid_id):
    """Return grid projection information.

    Parameters
    ----------
    grid_id : int
        Grid identifier.

    Returns
    -------
    projode : int
        GCTP projection code.
    zonecode : int
        GCTP zone code used by UTM projection.
    spherecode : int
        GCTP spheroid code
    projparm : ndarray
        GCTP projection parameters

    Raises
    ------
    IOError
        If associated library routine fails.
    """
    projcode = ffi.new("int32 *")
    zonecode = ffi.new("int32 *")
    spherecode = ffi.new("int32 *")
    projparm = np.zeros(13, dtype=np.float64)
    projparmp = ffi.cast("float64 *", projparm.ctypes.data)
    status = _lib.GDprojinfo(grid_id, projcode, zonecode, spherecode,
                             projparmp)
    _handle_error(status)

    return projcode[0], zonecode[0], spherecode[0], projparm

