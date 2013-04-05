import numpy as np
import h5py

FILE = "cmprss.h5"
RANK = 2
DIM0 = 100
DIM1 = 20

def run():
    # Create a file.
    fid = h5py.h5f.create(FILE.encode())

    # Create dataset "Compressed Data" in the group using absolute names.
    dims = (DIM0, DIM1)
    space_id = h5py.h5s.create_simple(dims)

    dcpl = h5py.h5p.create(h5py.h5p.DATASET_CREATE)

    # Datasets must be chunked for compression.
    cdims = (20, 20)
    dcpl.set_chunk(cdims)

    # Set ZLIB / DEFLATE compression using compression level 6.
    dcpl.set_deflate(6)

    dset = h5py.h5d.create(fid, "Compressed_Data".encode(),
                           h5py.h5t.STD_I32BE, 
                           space_id, dcpl, h5py.h5p.DEFAULT)

    buf = np.zeros((DIM0, DIM1))
    for i in range(DIM0):
        buf[i] = i + np.arange(DIM1)

    dset.write(h5py.h5s.ALL, h5py.h5s.ALL, buf)

    # Now reopen the file and dataset.
    fid = h5py.h5f.open(FILE.encode())
    dset = h5py.h5d.open(fid, "Compressed_Data".encode())

    dcpl = dset.get_create_plist()

    numfilt = dcpl.get_nfilters()
    print("Number of filters associated with dataset:  %d" % numfilt)

    for j in range(numfilt):
        code, flags, values, name = dcpl.get_filter(j)
        print(name.decode('utf-8'))

    newdata = np.zeros((DIM0, DIM1))
    dset.read(h5py.h5s.ALL,h5py.h5s.ALL, newdata)
    print(newdata)

if __name__ == "__main__":
    run()

