"""
Shows how to use the h5s.copy function

This program creates two files, copy1.h5, and copy2.h5.  In copy1.h5,
it creates a 3x4 dataset called 'Copy1', and write 0's to this
dataset.  In copy2.h5, it create a 3x4 dataset called 'Copy2', and
write 1's to this dataset.

It closes both files, reopens both files, selects two points in
copy1.h5 and writes values to them.  Then it does an H5Scopy from
the first file to the second, and writes the values to copy2.h5.
It then closes the files, reopens them, and prints the contents of
the two datasets.   

Minimum intended software versions
    HDF5:   1.8
    Python: 3.2
    H5PY:   2.1.2
"""

import numpy as np
import h5py

FILE1 = "copy1.h5"
FILE2 = "copy2.h5"

RANK = 2
DIM1 = 3
DIM2 = 4
NUMP = 2

def run():

    # Create two files containing identical datasets.  Write 0's to one and
    # 1's to the other.
    buf1 = np.zeros((DIM1, DIM2))
    buf2 = np.ones((DIM1, DIM2))

    file1 = h5py.h5f.create(FILE1.encode())
    file2 = h5py.h5f.create(FILE2.encode())

    space1 = h5py.h5s.create_simple((DIM1, DIM2))
    space2 = h5py.h5s.create_simple((DIM1, DIM2))

    dset1 = h5py.h5d.create(file1, "Copy1".encode(), h5py.h5t.NATIVE_INT32,
                            space1)
    dset2 = h5py.h5d.create(file2, "Copy2".encode(), h5py.h5t.NATIVE_INT32,
                            space2)

    dset1.write(h5py.h5s.ALL, h5py.h5s.ALL, buf1)
    dset2.write(h5py.h5s.ALL, h5py.h5s.ALL, buf2)
                            
    # Open the two files.  Select two point in one file, write values to
    # those point locations, then copy and write the values to the other
    # file.
    file1 = h5py.h5f.open(FILE1.encode())
    file2 = h5py.h5f.open(FILE2.encode())
    dataset1 = h5py.h5f.open(file1, "Copy1".encode())
    dataset2 = h5py.h5f.open(file2, "Copy2".encode())



if __name__ == "__main__":
    run()
