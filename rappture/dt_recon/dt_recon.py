"""
Wrapper for dt_recon.
"""
import base64
import glob
import logging
from matplotlib import pyplot as plt
import numpy as np
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

import Rappture

import nibabel as nib

class MyTemporaryDirectory(object):
    """
    Implements context manager protocol for temp directory functionality.

    This is provided in Python 3.2 out-of-the-box.  We need it in 2.7 in
    order to guarantee clean-up of temporary directories in case that
    exceptions are raised during the operation of the tool.
    """
    def __init__(self):
        self.name = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exec_tb):
        """Clean up the temporary directory.
        """
        # Delete each item in the temp directory, then delete the
        # directory itself.
        lst = os.listdir(self.name)
        for item in lst:
            os.unlink(os.path.join(self.name, item))
        os.rmdir(self.name)

        # Finish off implementing the context manager protocol.
        if exc_type is None:
            return
        else:
            return False

def drive_dtrecon(input_zip_file):
    """Calls Freesurfer's dt_recon.

    Parameters
    ----------
    zfile : zip file
        zip file containing DICOMs and associated data files

    Returns
    -------
    output : str
        Metadata produced on stdout by system call to dt_recon.
    """
    logger = logging.getLogger('dt_recon')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(os.path.join(os.environ['HOME'], 'dt_recon.log'))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    with zipfile.ZipFile(input_zip_file) as zfile:
        tdir = tempfile.mkdtemp()

        # Extract each member of the zip file to the temporary
        # directory.
        logger.info('Unzipping zip file...')
        for zipmember in zfile.namelist():
            zfile.extract(zipmember, tdir)

        logger.info('Running dt recon...')
        output = run_dt_recon(tdir)
        logger.info('Extracting slice...')
        adc_image_str = extract_adc_slice(tdir)

        shutil.rmtree(tdir)

    logger.info('Done!')
    return output, adc_image_str

def run_dt_recon(tdir):
    """Run dt_recon on the input files.

    Parameters
    ----------
    tdir : str
        Path of temporary directory.  Inputs to dt_recon have been
        unpacked here.

    Returns
    -------
    output : str
        String collected from stdout of the results of running dt_recon.
    """
    # We need one dicom file to start us off.  Just take the first one
    # that we find.
    dicom_files = glob.glob(os.path.join(tdir, '*.dcm'))
    first_dicom_file = dicom_files[0]

    # The BVEC and BVALS files must currently have these names exactly.
    bvecs_file = os.path.join(tdir, 'bvecs.dat')
    bvals_file = os.path.join(tdir, 'bvals.dat')

    # Write the output to the same directory.
    output_dir = tdir

    # Construct the list of arguments.
    args = ['dt_recon', '--i', first_dicom_file,
            '--b', bvals_file, bvecs_file,
            '--o', output_dir,
            '--no-reg', '--debug']
    output = subprocess.check_output(args)

    return output

def extract_adc_slice(tdir):
    """Extracts a slice from ADC map.

    Parameters
    ----------
    tdir : str
        Path of temporary directory.  Inputs to dt_recon have been
        unpacked here.

    Returns
    -------
    output : str
        Base64 string representing a 1D slice image extracted from the
        ADC nifti file.
    """
    # Read in the ADC map.
    adc_file = os.path.join(tdir, 'adc.nii')
    img = nib.load(adc_file)
    data = img.get_data()
    islice = data[:, :, 32]

    # Rotate by 90 degrees clockwise
    islice = np.rot90(islice, 3)

    # Scale to 0-255
    add_offset = islice.min()
    scale_factor = 255.0 / (islice.max() - add_offset)
    islice = (islice - add_offset) * scale_factor
    islice = np.round(islice).astype(np.uint8)

    # Replicate in 3 layers to make it look like greyscale.
    faux_3d = np.zeros((islice.shape[0], islice.shape[1], 3))
    faux_3d[:, :, 0] = islice
    faux_3d[:, :, 1] = islice
    faux_3d[:, :, 2] = islice

    with tempfile.NamedTemporaryFile(suffix='.png') as pngfile:
        plt.imsave(pngfile.name, faux_3d)
        with open(pngfile.name, 'r') as tfile2:
            adc_image_str = base64.b64encode(tfile2.read())

    return adc_image_str

if __name__ == "__main__":
    DRIVER = Rappture.library(sys.argv[1])
    ZIPDATA = DRIVER.get('input.string(zipfile).current')

    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tfile:
        tfile.write(ZIPDATA)
        tfile.flush()
        OUTPUT, IMAGESTR = drive_dtrecon(tfile.name)

    DRIVER.put("output.log", OUTPUT)
    DRIVER.put("output.image(outi).about.label",
               "Middle slice in ADC map file.")
    DRIVER.put("output.image(outi).current", IMAGESTR)
    Rappture.result(DRIVER)
    sys.exit()

