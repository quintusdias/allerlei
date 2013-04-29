"""
This example shows how to create intermediate groups with a single call to
h5py.h5g.create.

Tested with:
    HDF5:   1.8.10
    Python: 3.2.3
    Numpy:  1.7.1
    H5PY:   2.1.2
"""

import sys

import numpy as np
import h5py

def run(FILE):

    fid = h5py.h5f.open(FILE.encode())
    gid = h5py.h5g.open(fid, '/'.encode())

    # Print all the objects in the file to show that intermediate groups
    # have been created.
    print("\nObjects in the file:")
    h5py.h5o.visit(gid, ovisit, info=True)

def ovisit(name, info):
    """Operator function, prints name and type of object being examined."""

    # Let's prepend with a leading slash, just so we have the full path.
    if name == '.':
        name = '/'
    if info.type == h5py.h5o.TYPE_GROUP:
        fmt = "/%s (Group)"
    elif info.type == h5py.h5o.TYPE_DATASET:
        fmt = "/%s (Dataset)"
    elif info.type == h5py.h5o.TYPE_NAMED_DATATYPE:
        fmt = "/%s (Datatype)"
    else:
        fmt = "/%s (Unknown)"
    print( fmt % name.decode('utf-8'))

if __name__ == "__main__":
    run(sys.argv[1])        
