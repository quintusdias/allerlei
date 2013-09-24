"""
Wrapper for slicer
"""
import base64
import logging
import os
import shutil
import socket
import subprocess
import sys
import tempfile

from matplotlib import pyplot as plt
import numpy as np
import nibabel as nib

import Rappture

class SlicerWrapper(object):
    """
    Wraps DTI command line processing of NRRD files via Slicer cli modules.

    Attributes
    ----------
    driver : Rappture driver object
        Drives rappture processing.
    slicer_output : str
        stdout output of slicer commands.  Can be seen in the rappture GUI
        by clicking in the "Result" drop-down, choose "Output Log".
    adc_image : array
        ADC scalar map.
    logger : logging.Logger
        Debugging purposes only.  Writes to a file in your home
        directory.
    temporary_directory : str
        Temporary directory into which intermediate products are written.
    DWIToDTIEstimation: str
        Full path to DWIToDTIEstimation executable.
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

        # Empty values at first for these two Rappture GUI outputs.
        self.slicer_output = ''
        self.adc_image = None

        self.temporary_directory = None

        # Construct the full path to the DWIToDTIEstimation executable.
        # This has to include the LD_LIBRARY_PATH environment variable.
        if socket.gethostname() == 'nciphub':
            slicer_root = '/apps/share64/debian7/slicer/4.2.1/Slicer-build'

            # No need to use this on nciphub.  Just do it to be consistent.
            env = dict(os.environ)

        else:
            # MGH setup.
            slicer_root = '/usr/pubsw/packages/slicer/Slicer-4.2.2-1-linux-amd64'
            env = dict(os.environ)
            env['LD_LIBRARY_PATH'] = os.path.join(slicer_root, 'lib/Slicer-4.2') \
                                   + ':' \
                                   + os.path.join(slicer_root, 'lib/Teem-1.10.0') \
                                   + ':' \
                                   + os.path.join(slicer_root, 'lib/Slicer-4.2/cli-modules')

        self.slicer_42_env = env
        self.DWIToDTIEstimation = os.path.join(slicer_root,
                                               'lib/Slicer-4.2/cli-modules/DWIToDTIEstimation')
        self.DiffusionTensorScalarMeasurements = os.path.join(slicer_root,
                                                              'lib/Slicer-4.2/cli-modules/DiffusionTensorScalarMeasurements')

        # Need to convert to nifti.
        self.converter = os.path.join(slicer_root,
                                      'lib/Slicer-4.2/cli-modules/ResampleScalarVolume')


        if use_logging:
            logger = logging.getLogger('slicer')
            logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler(os.path.join(os.environ['HOME'],
                                               'slicer.log'))
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


    def drive_slicer(self, nrrdfile):
        """Calls Slicer's dti command line modules.  Has no Rappture
        dependencies, so this part can be debugged from the command line.

        Parameters
        ----------
        nrrdfile : str
            NRRD binary file.
        """
        self.temporary_directory = tempfile.mkdtemp()
    
        self.log('Running slicer...')
        self.run_slicer(nrrdfile)
    
        trace_file = os.path.join(self.temporary_directory, 'trace.nii')
        img = nib.load(trace_file)
        self.adc_image = img.get_data()
    
        shutil.rmtree(self.temporary_directory)

        self.log('Done!')

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

    def run_slicer(self, nrrd_file):
        """Run slicer cli modules on the input files.  The stdout output is collected.

        Parameters
        ----------
        nrrd_file : str
            Path to NRRD binary file.
        """
        # Construct a shell script with all the commands.
        command = '{dti_command} --enumeration WLS {dwi_file} {dti_file} {scalar_file}'
        command = command.format(dti_command=self.DWIToDTIEstimation,
                                 dwi_file=nrrd_file,
                                 dti_file=os.path.join(self.temporary_directory, 'dti.nrrd'),
                                 scalar_file=os.path.join(self.temporary_directory, 'scalar_volume_b.nrrd'))
        self.log(command)
        self.slicer_output = subprocess.check_output(command.split(' '), env=self.slicer_42_env)

        command = '{scalar_command} --enumeration Trace {dti_file} {trace_file}'
        command = command.format(scalar_command=self.DiffusionTensorScalarMeasurements,
                                 dti_file=os.path.join(self.temporary_directory, 'dti.nrrd'),
                                 trace_file=os.path.join(self.temporary_directory, 'trace.nrrd'))
        self.log(command)
        self.slicer_output += subprocess.check_output(command.split(' '), env=self.slicer_42_env)
            
        # Convert it to NIFTI
        command = '{converter} {trace_nrrd} {trace_nifti}'
        command = command.format(converter=self.converter,
                                 trace_nrrd=os.path.join(self.temporary_directory, 'trace.nrrd'),
                                 trace_nifti=os.path.join(self.temporary_directory, 'trace.nii'))
        self.log(command)
        self.slicer_output += subprocess.check_output(command.split(' '), env=self.slicer_42_env)


    def run(self):
        """
        Runs the wrapping process from the point of Rappture.
        """
        # The "loader" gui element currently reads in the NRRD file
        # images as a base64 string.  We will write it back out as a real NRRD
        # file and drive a pure-python method with only that as input.
        # Use the loader.
        nrrd_data = self.driver.get('input.string(nrrdfile).current')
        with tempfile.NamedTemporaryFile(suffix='.nrrd', delete=False) as tfile:
            tfile.write(nrrd_data)
            tfile.flush()
            self.drive_slicer(tfile.name)

        # Populate the rappture output elements.
        self.driver.put("output.log", self.slicer_output)


        self.driver.put("output.sequence(movie).about.label", "Trace Map")
        self.driver.put("output.sequence(movie).index.label", "Slice")
        for j in range(self.adc_image.shape[2]):

            # Write the label for the jth image.
            self.driver.put("output.sequence(movie).element({0}).index".format(j), j+1)
            self.driver.put("output.sequence(movie).element({0}).image.current".format(j),
                            self.slice_to_str(j))

        Rappture.result(self.driver)



if __name__ == "__main__":
    DRIVER = Rappture.library(sys.argv[1])
    WRAPPER = SlicerWrapper(driver=DRIVER, use_logging=True)
    WRAPPER.run()
    #WRAPPER = SlicerWrapper(driver=None, use_logging=True)
    #nrrd_file = '/homes/5/jevans/space/data/slicer/DiffusionMRI_tutorialData/dwi.nhdr'
    #WRAPPER.drive_slicer(nrrd_file)
    sys.exit()
