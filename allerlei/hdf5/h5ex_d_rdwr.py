"""
This example shows how to read and write data to a dataset.  The
program first writes integers to a dataset with dataspace dimensions
of DIM0xDIM1, then closes the file.  Next, it reopens the file,
reads back the data, and outputs it to the screen.

Minimum intended software versions
    HDF5:   1.8
    Python: 3.2
    H5PY:   2.1.2
"""

import numpy as np
import h5py

FILE = "h5ex_d_rdwr.h5"
DATASET = "DS1"
DIM0 = 4
DIM1 = 7

def run():

    # Initialize the data.
    wdata = np.zeros((DIM0, DIM1), dtype=np.int32)
    for i in range(DIM0):
        for j in range(DIM1):
            wdata[i][j] = i * j - j

    # Create a new file using the default properties.
    fid = h5py.h5f.create(FILE.encode())

    # Create the dataspace.  No maximum size parameter needed.
    dims = (DIM0, DIM1)
    space = h5py.h5s.create_simple(dims)

    # Create the datasets using default properties.
    dset = h5py.h5d.create(fid, DATASET.encode(), h5py.h5t.STD_I32LE, space)

    # Write the data to the dataset.
    dset.write(h5py.h5s.ALL, h5py.h5s.ALL, wdata)

    # Close and release resources.
    del dset
    del space
    del fid

    # Reopen the file and dataset using default properties.
    fid = h5py.h5f.open(FILE.encode())
    dset = h5py.h5d.open(fid, DATASET.encode())

    # Read the data using default properties.
    rdata = np.zeros((DIM0, DIM1), dtype=np.int32)
    dset.read(h5py.h5s.ALL, h5py.h5s.ALL, rdata)

    print("%s:" % DATASET)
    print(rdata)

if __name__ == "__main__":
    run()        
