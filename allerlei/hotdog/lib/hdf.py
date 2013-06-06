DFE_NONE = 0
DFACC_READ = 1

from cffi import FFI
ffi = FFI()
ffi.cdef("""
        typedef int int32;
        typedef int intn;

        int32 SDstart(char *name, int32 accs);
        intn SDfileinfo(int32 sd_id, int32 *n_datasets, int32 *n_file_attrs);
        intn SDend(int32 id);
        """)
hdf = ffi.verify("""
        #include "mfhdf.h"
        """,
        libraries=['mfhdf', 'df', 'jpeg', 'z'],
        include_dirs=['/usr/include/hdf'],
        library_dirs=['/usr/lib/hdf'])

def SDstart(filename, access=DFACC_READ):
    sdid = hdf.SDstart(filename, access)
    return sdid

def SDfileinfo(sdid):
    nvarsp = ffi.new("int32 *")
    ngattsp = ffi.new("int32 *")
    status = hdf.SDfileinfo(sdid, nvarsp, ngattsp)
    if status != 0:
        raise IOError("Library routine failed.")
    return nvarsp[0], ngattsp[0]

def SDend(sdid):
    status = hdf.SDend(sdid)
    return status

if __name__ == "__main__":

    file = b'/home/jevans/data/hdf/MODATML2.A2000055.0000.005.2006253045900.hdf'
    sdid = SDstart(file, DFACC_READ) # for read access
    vals = SDfileinfo(sdid)
    print(vals)
    SDend(sdid)
