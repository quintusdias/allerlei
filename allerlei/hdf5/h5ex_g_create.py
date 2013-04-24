"""
This example shows how to create, open, and close a group.

Tested with:
    HDF5:   1.8.10
    Python: 3.2.3
    Numpy:  1.7.1
    H5PY:   2.1.2
"""

import numpy as np
import h5py

FILE = "h5ex_g_create.h5"

def run():

    # Create a new file using the default properties.
    fid = h5py.h5f.create(FILE.encode())

    # Create a group named "G1" in the file.
    group = h5py.h5g.create(fid, "/G1".encode())

    # Close the group.  The handle "group" can no longer be used.
    del group

    # Re-open the group, obtaining a new handle.
    group = h5py.h5g.open(fid, "/G1".encode())

    # Close and release resources.
    del group
    del fid


if __name__ == "__main__":
    run()        
