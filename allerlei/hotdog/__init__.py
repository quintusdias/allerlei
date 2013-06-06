from cffi import FFI
ffi = FFI()
ffi.cdef("""
        int SDstart(char *name, int accs);
        """)
hdf = ffi.verify("""
        #include "mfhdf.h"
        """,
        libraries=['mfhdf', 'df', 'jpeg', 'z'],
        include_dirs=['/usr/include/hdf'],
        library_dirs=['/usr/lib/hdf'])
file = b'/home/jevans/data/hdf/MODATML2.A2000055.0000.005.2006253045900.hdf'
sdid = hdf.SDstart(file, 1) # for read access
