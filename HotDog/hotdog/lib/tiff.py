from contextlib import contextmanager
import numpy as np
from cffi import FFI

ffi = FFI()
ffi.cdef("""
    typedef ... uint32;                                                     
    typedef ... tmsize_t;                                                     
    typedef ... toff_t;          /* file offset */                                  
    typedef ... ttag_t;          /* directory tag */                                
    typedef ... tdir_t;          /* directory index */                              
    typedef uint16_t tsample_t;  /* sample number */                                
    typedef ... tstrile_t;       /* strip or tile number */                         
    typedef uint32_t tstrip_t;   /* strip number */                                 
    typedef ... ttile_t;         /* tile number */                                  
    typedef int32_t tsize_t;     /* i/o size in bytes */                            
    typedef void * tdata_t;      /* image data ref */ 

    typedef ... TIFF;
    void TIFFClose(TIFF *tif);
    extern TIFF* TIFFOpen(const char*, const char*);
    extern int TIFFSetField(TIFF*, uint32_t, ...);
    tsize_t TIFFWriteEncodedTile(TIFF *tif, ttile_t tile, tdata_t buf,
                                 tsize_t size);
    tsize_t TIFFWriteEncodedStrip(TIFF *tif, tstrip_t strip, tdata_t buf,
                                  tsize_t size);
    tsize_t TIFFWriteTile(TIFF *tif, tdata_t buf, uint32_t x, uint32_t y,
                          uint32_t z, tsample_t sample);
        """)
_lib = ffi.verify("""
                  #include "tiffio.h"
                  """,
                  libraries=['tiff', 'jpeg', 'z'],
                  include_dirs=['/opt/local/include'],
                  library_dirs=['/opt/local/lib'])

tags_bytes = ['XMLPacket']
tags_int16 = ['PhotometricInterpretation', 'PlanarConfiguration',
              'SampleFormat']
tags_int32 = ['BitsPerSample', 'ImageWidth', 'ImageLength', 'RowsPerStrip',
              'SamplesPerPixel', 'TileWidth', 'TileLength']
tagnumber = {'ImageWidth': 256,
             'ImageLength': 257,
             'BitsPerSample': 258,
             'PhotometricInterpretation': 262,
             'SamplesPerPixel': 277,
             'RowsPerStrip': 278,
             'PlanarConfiguration': 284,
             'TileWidth': 322,
             'TileLength': 323,
             'SampleFormat': 339,
             'XMLPacket': 700}

PLANARCONFIG_CONTIG = 1
PLANARCONFIG_SEPARATE = 2

PHOTOMETRIC_MINISWHITE = 0
PHOTOMETRIC_MINISBLACK = 1
PHOTOMETRIC_RGB = 2
PHOTOMETRIC_PALETTE = 3
PHOTOMETRIC_MASK = 4
PHOTOMETRIC_SEPARATED = 5
PHOTOMETRIC_YCBCR = 6

SAMPLEFORMAT_UINT = 1  # !unsigned integer data */
SAMPLEFORMAT_INT = 2  # !signed integer data */
SAMPLEFORMAT_IEEEFP = 3  # !IEEE floating point data */
SAMPLEFORMAT_VOID = 4   # !untyped data */
SAMPLEFORMAT_COMPLEXINT = 5  #complex signed int */
SAMPLEFORMAT_COMPLEXIEEEFP = 6  # complex ieee floating */

def _handle_error(status):
    if status < 0:
        raise IOError("Library routine failed.")

@contextmanager
def open(filename, mode='r'):
    tiffp = _lib.TIFFOpen(filename.encode(), mode.encode())
    yield tiffp
    _lib.TIFFClose(tiffp)

def setfield(tifp, tagname, *args):
    """Corresponds to TIFFSetField.
    Parameters
    ----------
    tifp : object
        File pointer returned by TIFFOpen.
    tagname : str
        String specifying a tag.
    args : positional arguments
        Tag values.

    Raises
    ------
    IOError
        If the library routine fails.
    """
    if tagname == 'XMLPacket':
        value = ffi.new("char []", args[0].encode())
        status = _lib.TIFFSetField(tifp, tagnumber[tagname],
                                   ffi.cast("uint32_t", len(value)), value);
    elif tagname in tags_int16:
        value = ffi.cast("short", args[0])
        status = _lib.TIFFSetField(tifp, tagnumber[tagname], value);
    elif tagname in tags_int32:
        value = ffi.cast("int", args[0])
        status = _lib.TIFFSetField(tifp, tagnumber[tagname], value);
    else:
        raise NotImplementedError("Unrecognized tag.")

    _handle_error(status)

def close(tiffp):
    _lib.TIFFClose(tiffp)

def writeencodedstrip(tiffp, stripnum, imagedata): 
    if imagedata.dtype == np.float32:
        datap = ffi.cast("float *", imagedata.ctypes.data)
        nbytes = imagedata.size * 4
    elif imagedata.dtype == np.uint8:
        datap = ffi.cast("uint8_t *", imagedata.ctypes.data)
        nbytes = imagedata.size * 1
    else:
        raise NotImplementedError("untested datatype")
    status = _lib.TIFFWriteEncodedStrip(tiffp, stripnum, datap, nbytes)
    _handle_error(status)

def writetile(tiffp, imagedata, x, y, z=0, sample=0):
    if imagedata.dtype == np.float32:
        datap = ffi.cast("float *", imagedata.ctypes.data)
    else:
        raise NotImplementedError("untested datatype")
    status = _lib.TIFFWriteTile(tiffp, datap, x, y, z, sample)
    _handle_error(status)

if __name__ == "__main__":
    pass
