import pkg_resources
from cffi import FFI

DFE_NONE = 0
DFACC_READ = 1

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

def select(sdid, sds_index):
    sds_id = _lib.SDselect(sdid, sds_index)
    return sds_id

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
    dimsizes = ffi.new("int32[]", rank[0])
    datatype = ffi.new("int32 *")
    nattrs = ffi.new("int32 *")
    status = _lib.SDgetinfo(sds_id, ffi.NULL, ffi.NULL, dimsizes, datatype, nattrs)
    _handle_error(status)
    return ffi.string(name).decode('ascii'), rank, dimsizes, datatype, nattrs

def start(filename, access=DFACC_READ):
    sdid = _lib.SDstart(filename, access)
    return sdid

def fileinfo(sdid):
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
        endaccess(sds_id)
    end(sdid)
