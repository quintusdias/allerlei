"""
This example shows how to read and write data to a compact dataset.
The program first writes integers to a compact dataset with dataspace
dimensions of DIM0xDIM1, then closes the file.  Next, it reopens
the file, reads back the data, and outputs it to the screen.

Minimum intended software versions
    HDF5:   1.8
    Python: 3.2
    H5PY:   2.1.2
"""

import numpy as np
import h5py

FILE = "h5ex_d_compact.h5"
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
    space_id = h5py.h5s.create_simple(dims)

    # Create the dataset creation property list.  Set the layout to compact.
    dcpl = h5py.h5p.create(h5py.h5p.DATASET_CREATE)
    dcpl.set_layout(h5py.h5d.COMPACT)

    # Create the datasets using the dataset creation property list.
    dset = h5py.h5d.create(fid, DATASET.encode(), h5py.h5t.STD_I32BE,
                           space_id, dcpl)

    # Write the data to the dataset.
    dset.write(h5py.h5s.ALL, h5py.h5s.ALL, wdata)

    # Close and release resources.
    del dcpl
    del dset
    del space_id
    del fid

    # Reopen file and dataset.
    file = h5py.h5f.open(FILE.encode())
    dset = h5py.h5d.open(file, DATASET.encode())

    # Retrieve the dataset creation property list and print the layout.
    dcpl = dset.get_create_plist()
    layout = dcpl.get_layout()

    ddict = {h5py.h5d.COMPACT: "H5D_COMPACT",
             h5py.h5d.CONTIGUOUS: "H5D_CONTIGUOUS",
             h5py.h5d.CHUNKED: "H5D_CHUNKED"}
    print("Storage layout for %s is %s" % (DATASET, ddict[layout])) 

    # Read the data and output to the screen.
    newdata = np.zeros((DIM0, DIM1), dtype=np.int32)
    dset.read(h5py.h5s.ALL,h5py.h5s.ALL, newdata)
    print(newdata)


if __name__ == "__main__":
    run()        
   
