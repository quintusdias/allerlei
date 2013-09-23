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


class DtReconWrapper(object):
    """
    Wraps command line processing of dicom files via Freesurfer's dt_recon.

    Attributes
    ----------
    driver : Rappture driver object
        Drives rappture processing.
    dt_recon_output : str
        stdout output of dt_recon command.  Can be seen in the rappture GUI
        by clicking in the "Result" drop-down, choose "Output Log".
    adc_image : array
        3d image that constitutes the ADC map.
    logger : logging.Logger
        Debugging purposes only.  Writes to a file in your home
        directory.
    """

    def __init__(self, driver=None, use_logging=False):
        """
        Parameters
        ----------
        driver : Rappture driver object
            Drives rappture processing.
        use_logging : bool
            If true, turns on logging for debugging purposes.
        """
        self.driver = driver
        self.adc_image = None

        # Empty strings at first for these two Rappture GUI outputs.
        self.dt_recon_output = ''

        if use_logging:
            logger = logging.getLogger('dt_recon')
            logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler(os.path.join(os.environ['HOME'],
                                               'dt_recon.log'))
            fmt_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            formatter = logging.Formatter(fmt_string)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            self.logger = logger
        else:
            self.logger = None

    def log(self, msg):
        """
        Log a message if so ordered.
        """
        if self.logger is not None:
            self.logger.info(msg)


    def drive_dtrecon(self, input_zip_file):
        """Calls Freesurfer's dt_recon.  Has no Rappture dependencies, so this
        part can be debugged from the command line.

        Parameters
        ----------
        input_zip_file : zip file
            zip file containing DICOMs and associated data files

        """
        with zipfile.ZipFile(input_zip_file) as zfile:
            tdir = tempfile.mkdtemp()

            # Extract each member of the zip file to the temporary
            # directory.
            self.log('Unzipping zip file to {0}...'.format(tdir))
            for zipmember in zfile.namelist():
                zfile.extract(zipmember, tdir)

            self.run_dt_recon(tdir)
            self.extract_adc_slice(tdir)

            shutil.rmtree(tdir)

        self.log('Done!')

    def extract_adc_slice(self, tdir):
        """Extracts a slice from ADC map.  The result is a base64 string
        extracted from the 32nd slice of the ADC nifti file.

        Parameters
        ----------
        tdir : str
            Path of temporary directory.  Inputs to dt_recon have been
            unpacked here.
        """
        # Read in the ADC map.  Use the 32nd slice out of 64 (ad hoc).
        adc_file = os.path.join(tdir, 'adc.nii')
        img = nib.load(adc_file)
        self.adc_image = img.get_data()


    def slice_to_str(self, idx):
        """Extract a slice to a base64 string.
        """
        islice = self.adc_image[:, :, idx]

        # Rotate by 90 degrees clockwise.  That's the standard way to do it?
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

        # Save the resulting slice as a PNG file, then read it back in.
        # Rappture expects to render the image from a base64-encoded string,
        # so they get a base64 string encoded from the raw bytes constituting
        # the PNG file.
        with tempfile.NamedTemporaryFile(suffix='.png') as pngfile:
            plt.imsave(pngfile.name, faux_3d)
            with open(pngfile.name, 'r') as tfile2:
                adc_image_str = base64.b64encode(tfile2.read())

        return adc_image_str

    def run_dt_recon(self, tdir):
        """Run dt_recon on the input files.  The stdout output is collected
        into the dt_recon_output field.

        Parameters
        ----------
        tdir : str
            Path of temporary directory.  Inputs to dt_recon have been
            unpacked here.
        """
        # We need one dicom file to start us off.  Just take the first one
        # that we find.
        self.log("Running dt_recon...")
        dicom_files = glob.glob(os.path.join(tdir, '*.dcm'))
        first_dicom_file = dicom_files[0]

        # The BVEC and BVALS files must currently have these names exactly.
        bvecs_file = os.path.join(tdir, 'bvecs.dat')
        bvals_file = os.path.join(tdir, 'bvals.dat')

        # Write the output to the same directory.
        output_dir = tdir

        # Construct the list of arguments and execute the dt_recon process.
        # Save the results from stdout, which we will use to populate the
        # rappture log GUI element.
        args = ['dt_recon', '--i', first_dicom_file,
                '--b', bvals_file, bvecs_file,
                '--o', output_dir,
                '--no-reg', '--debug']
        self.log(' '.join(args))
        self.dt_recon_output = subprocess.check_output(args)

    def run(self):
        """
        Runs the wrapping process from the point of Rappture.
        """
        zipfile = self.driver.get('input.choice.current')
        self.drive_dtrecon(zipfile)

        # Populate the rappture output elements.  The slider is actually
        # a "sequence" of images.
        self.driver.put("output.log", self.dt_recon_output)
        self.driver.put("output.sequence(movie).about.label", "ADC Map")
        self.driver.put("output.sequence(movie).index.label", "Slice")

        for j in range(self.adc_image.shape[2]):

            # Write the jth frame of the ADC map.
            # The element attribute must be part of the named element, but the
            # index must be assigned.
            element = "output.sequence(movie).element({0}).index".format(j)
            self.driver.put(element, j+1)

            # Turn each slice in the ADC map into a base64 string.
            element = "output.sequence(movie).element({0}).image.current"
            element = element.format(j)
            self.log(element)
            self.driver.put(element, self.slice_to_str(j))

        Rappture.result(self.driver)


if __name__ == "__main__":
    DRIVER = Rappture.library(sys.argv[1])
    WRAPPER = DtReconWrapper(driver=DRIVER, use_logging=True)
    WRAPPER.run()
    sys.exit()
