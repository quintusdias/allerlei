DFE_NONE = 0
DFACC_READ = 1

from cffi import FFI
ffi = FFI()
ffi.cdef("""
        typedef int int32;
        typedef int intn;

        intn  SDend(int32 id);
        intn  SDendaccess(int32 sds_id);
        intn  SDgetinfo(int32 sds_id, char *sds_name, int32 *rank,
                        int32 dimsizes[], int32 *datatype, int32 *nattrs);
        intn  SDfileinfo(int32 sd_id, int32 *n_datasets, int32 *n_file_attrs);
        int32 SDfindattr(int32 obj_id, char *attr_name);
        int32 SDselect(int32 sd_id, int32 sds_index);
        int32 SDstart(char *name, int32 accs);
        """)
hdf = ffi.verify("""
        #include "mfhdf.h"
        """,
        libraries=['mfhdf', 'df', 'jpeg', 'z'],
        include_dirs=['/usr/include/hdf'],
        library_dirs=['/usr/lib/hdf'])

def _handle_error(status):
    if status != 0:
        raise IOError("Library routine failed.")

def SDselect(sdid, sds_index):
    sds_id = hdf.SDselect(sdid, sds_index)
    return sds_id

def SDgetinfo(sds_id):
    name = ffi.new("char[]", b'\0' * 64)
    rank = ffi.new("int32 *")
    status = hdf.SDgetinfo(sds_id, name, rank, ffi.NULL, ffi.NULL, ffi.NULL)
    _handle_error(status)
    dimsizes = ffi.new("int32[]", rank[0])
    datatype = ffi.new("int32 *")
    nattrs = ffi.new("int32 *")
    status = hdf.SDgetinfo(sds_id, ffi.NULL, ffi.NULL, dimsizes, datatype, nattrs)
    _handle_error(status)
    return ffi.string(name).decode('ascii'), rank, dimsizes, datatype, nattrs

def SDstart(filename, access=DFACC_READ):
    sdid = hdf.SDstart(filename, access)
    return sdid

def SDfileinfo(sdid):
    nvarsp = ffi.new("int32 *")
    ngattsp = ffi.new("int32 *")
    status = hdf.SDfileinfo(sdid, nvarsp, ngattsp)
    _handle_error(status)
    return nvarsp[0], ngattsp[0]

def SDfindattr(obj_id, name):
    nvarsp = ffi.new("int32 *")
    ngattsp = ffi.new("int32 *")
    idx = hdf.SDfindattr(obj_id, name.encode())
    _handle_error(idx)
    return idx

def SDend(sdid):
    status = hdf.SDend(sdid)
    return status

def SDendaccess(sds_id):
    status = hdf.SDendaccess(sds_id)
    _handle_error(status)

if __name__ == "__main__":

    file = b'/home/jevans/data/hdf/MODATML2.A2000055.0000.005.2006253045900.hdf'
    sdid = SDstart(file, DFACC_READ) # for read access
    vals = SDfileinfo(sdid)
    for idx in range(vals[0]):
        sds_id = SDselect(sdid, idx)
        info = SDgetinfo(sds_id)
        print(idx)
        print(info[0])
        attr_idx = SDfindattr(sds_id, 'long_name')
        print(attr_idx)
        SDendaccess(sds_id)
    SDend(sdid)
