from contextlib import contextmanager
import pkg_resources
import numpy as np
from cffi import FFI

DFE_NONE = 0
DFACC_READ = 1
DFNT_CHAR = 4
DFNT_FLOAT = 5

ffi = FFI()
ffi.cdef("""
        typedef int int32;
        typedef int intn;

        intn  SDend(int32 id);
        intn  SDendaccess(int32 sds_id);
        intn  SDgetinfo(int32 sds_id, char *sds_name, int32 *rank,
                        int32 dimsizes[], int32 *datatype, int32 *nattrs);
        intn  SDfileinfo(int32 sd_id, int32 *n_datasets, int32 *n_file_attrs);
        intn  SDattrinfo(int32 obj_id, int32 attr_index, 
                         char *attr_name, int32 *data_type, int32 *count);
        int32 SDfindattr(int32 obj_id, char *attr_name);
        intn  SDreadattr(int32 obj_id, int32 attr_index, void *buffer);
        intn  SDreaddata(int32 sds_id, int32 *start, int32 *stride,
                         int32 *edge, void *buffer);
        int32 SDselect(int32 sd_id, int32 sds_index);
        int32 SDstart(char *name, int32 accs);
        """)
_lib = ffi.verify("""
        #include "mfhdf.h"
        """,
        libraries=['mfhdf', 'df', 'jpeg', 'z'],
        include_dirs=['/usr/include/hdf', '/opt/local/include'],
        library_dirs=['/usr/lib/hdf', '/opt/local/lib'])

def _handle_error(status):
    if status < 0:
        raise IOError("Library routine failed.")

@contextmanager 
def select(sdid, sds_index):
    sds_id = _lib.SDselect(sdid, sds_index)
    yield sds_id
    _lib.SDendaccess(sds_id)

def attrinfo(obj_id, attr_index):
    attr_name = ffi.new("char[]", b'\0' * 64)
    data_type = ffi.new("int32 *")
    count = ffi.new("int32 *")
    status = _lib.SDattrinfo(obj_id, attr_index, attr_name, data_type, count);
    _handle_error(status)
    return ffi.string(attr_name).decode('ascii'), data_type[0], count[0]

def getinfo(sds_id):
    name = ffi.new("char[]", b'\0' * 64)
    rank = ffi.new("int32 *")
    status = _lib.SDgetinfo(sds_id, name, rank, ffi.NULL, ffi.NULL, ffi.NULL)
    _handle_error(status)

    dimsizes = np.zeros(rank[0], dtype=np.int32)
    dimsizesp = ffi.cast("int *", dimsizes.ctypes.data)

    datatype = ffi.new("int32 *")
    nattrs = ffi.new("int32 *")
    status = _lib.SDgetinfo(sds_id, ffi.NULL, ffi.NULL, dimsizesp, datatype, nattrs)
    _handle_error(status)

    return (ffi.string(name).decode('ascii'),
            rank[0],
            dimsizes,
            datatype[0],
            nattrs[0])

@contextmanager
def start(filename, access=DFACC_READ):
    sdid = _lib.SDstart(filename.encode(), access)
    yield sdid
    _lib.SDend(sdid)

def fileinfo(sdid):
    """
    Returns
    -------
    data : tuple
        nvars, ngatts
    """
    nvarsp = ffi.new("int32 *")
    ngattsp = ffi.new("int32 *")
    status = _lib.SDfileinfo(sdid, nvarsp, ngattsp)
    _handle_error(status)
    return nvarsp[0], ngattsp[0]

def findattr(obj_id, name):
    idx = _lib.SDfindattr(obj_id, name.encode())
    _handle_error(idx)
    return idx

def end(sdid):
    status = _lib.SDend(sdid)
    return status

def endaccess(sds_id):
    status = _lib.SDendaccess(sds_id)
    _handle_error(status)

def readattr(obj_id, attr_idx):
    _, dtype, count = attrinfo(obj_id, attr_idx)
    if dtype == DFNT_CHAR:
        buffer = ffi.new("char[]", b'\0' * count)
    elif dtype == DFNT_FLOAT:
        buffer = ffi.new("float *")
    else:
        raise NotImplementedError("Only char attributes for now.")

    status = _lib.SDreadattr(obj_id, attr_idx, buffer)
    _handle_error(status)
    if dtype == DFNT_CHAR:
        return ffi.string(buffer).decode('ascii')
    elif dtype == DFNT_FLOAT:
        return buffer[0]

#def readdata(sds_id, start=None, stride=None, edge=None):
def readdata(sds_id, start=None, stride=None, edge=None):
    _, rank, dimsizes, dtype, _ = getinfo(sds_id)
    if start is None:
        start = np.zeros(dimsizes, dtype=np.int32)
        startp = ffi.cast("int *", start.ctypes.data)
    if edge is None:
        edge = np.array(dimsizes, dtype=np.int32)
        edgep = ffi.cast("int *", edge.ctypes.data)
    if stride is None:
        stridep = ffi.NULL
    if dtype == DFNT_FLOAT:
        data = np.zeros(dimsizes, dtype=np.float32)
        datap = ffi.cast("void *", data.ctypes.data)
    else:
        raise NotImplementedError("Only float datasets for now.")

    status = _lib.SDreaddata(sds_id, startp, stridep, edgep, datap)
    _handle_error(status)
    return data


if __name__ == "__main__":

    file = b'/opt/data/hdf/TOMS-EP_L3-TOMSEPL3_2000m0101_v8.HDF'
    sdid = start(file, DFACC_READ) # for read access
    vals = fileinfo(sdid)
    for idx in range(vals[0]):
        print(idx)
        sds_id = select(sdid, idx)
        info = getinfo(sds_id)
        print(info[0])
        attr_idx = findattr(sds_id, 'long_name')
        print(attr_idx)
        attr_name, datatype, count = attrinfo(sds_id, attr_idx)
        print(count)
        long_name = readattr(sds_id, attr_idx)
        print(long_name)
        endaccess(sds_id)
    end(sdid)
