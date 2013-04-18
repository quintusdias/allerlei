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
DATASET1 = "Copy1"
DATASET2 = "Copy2"
RANK = 2
DIM1 = 3
DIM2 = 4
NUMP = 2 # no, definitely not "NUMPY"

def run():

    # Create two files containing identical datasets.  Write 0's to one and
    # 1's to the other.
    buf1 = np.zeros((DIM1, DIM2), dtype=np.int32)
    buf2 = np.ones((DIM1, DIM2), dtype=np.int32)

    fid1 = h5py.h5f.create(FILE1.encode())
    fid2 = h5py.h5f.create(FILE2.encode())

    dims = (DIM1, DIM2)
    space1 = h5py.h5s.create_simple(dims)
    space2 = h5py.h5s.create_simple(dims)

    dset1 = h5py.h5d.create(fid1, DATASET1.encode(), h5py.h5t.NATIVE_INT32, space1)
    dset2 = h5py.h5d.create(fid2, DATASET2.encode(), h5py.h5t.NATIVE_INT32, space2)

    dset1.write(h5py.h5s.ALL, h5py.h5s.ALL, buf1)
    dset2.write(h5py.h5s.ALL, h5py.h5s.ALL, buf2)


    # Open the two files.  Select two point in one file, write values to
    # those point locations, then copy and write the values to the other
    # file.
    file1 = h5py.h5f.open(FILE1.encode())
    file2 = h5py.h5f.open(FILE2.encode())
    dset1 = h5py.h5d.open(file1, DATASET1.encode())
    dset2 = h5py.h5d.open(file2, DATASET2.encode())
    fid1 = dset1.get_space()
    mid1 = h5py.h5s.create_simple((2,))

    coord = np.zeros((NUMP, RANK))
    coord[0] = [0, 3]
    coord[1] = [0, 1]
    fid1.select_elements(coord)

    val = np.array([53, 59], dtype=np.int32)
    dset1.write(mid1, fid1, val, h5py.h5t.NATIVE_INT32)

    fid2 = fid1.copy()
    dset2.write(mid1, fid2, val, h5py.h5t.NATIVE_INT32)

    # Open both files and print the contents of the datasets.
    file1 = h5py.h5f.open(FILE1.encode())
    file2 = h5py.h5f.open(FILE2.encode())
    dset1 = h5py.h5d.open(file1, DATASET1.encode())
    dset2 = h5py.h5d.open(file2, DATASET2.encode())

    bufnew = np.zeros((DIM1, DIM2), dtype=np.int32)
    dset1.read(h5py.h5s.ALL, h5py.h5s.ALL, bufnew)

    print("\nDataset '%s' in file '%s' contains:" % (DATASET1, FILE1))
    print(bufnew)

    dset2.read(h5py.h5s.ALL, h5py.h5s.ALL, bufnew)

    print("\nDataset '%s' in file '%s' contains:" % (DATASET2, FILE2))
    print(bufnew)

if __name__ == "__main__":
    run()

