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
    adc_image_str : str
        base64 encoded string constituting an entire image
        The ADC map output is rendered by this.  Can be seen in the rappture
        GUI by clicking in the "Result" drop-down, choose "Middle slice in ADC
        map file" (should be the default).
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

        # Empty strings at first for these two Rappture GUI outputs.
        self.dt_recon_output = ''
        self.adc_image_str = ''

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
            self.log('Unzipping zip file...')
            for zipmember in zfile.namelist():
                zfile.extract(zipmember, tdir)

            self.log('Running dt recon...')
            self.run_dt_recon(tdir)
            self.log('Extracting slice...')
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
        data = img.get_data()
        islice = data[:, :, 32]

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
                self.adc_image_str = base64.b64encode(tfile2.read())

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
        self.dt_recon_output = subprocess.check_output(args)

    def run(self):
        """
        Runs the wrapping process from the point of Rappture.
        """
        # The "loader" gui element currently reads in the zip file of DICOM
        # images as a base64 string.  We will write it back out as a real zip
        # file and drive a pure-python method with only that as input.
        zipdata = self.driver.get('input.string(zipfile).current')
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tfile:
            tfile.write(zipdata)
            tfile.flush()
            self.drive_dtrecon(tfile.name)

        # Populate the rappture output elements.
        self.driver.put("output.log", self.dt_recon_output)
        self.driver.put("output.image(outi).about.label",
                        "Middle slice in ADC map file.")
        self.driver.put("output.image(outi).current", self.adc_image_str)
        Rappture.result(self.driver)


if __name__ == "__main__":
    DRIVER = Rappture.library(sys.argv[1])
    WRAPPER = DtReconWrapper(driver=DRIVER)
    WRAPPER.run()
    sys.exit()
