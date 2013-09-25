"""
Wrapper for slicer
"""
import base64
import glob
import logging
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import zipfile

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
    slicer_env, freesurfer_env : dictionary
        Environment needed to run slicer, freesurfer.
    slicer_output, freesurfer_output : str
        stdout output of slicer, freesurfer commands.  Can be seen in the
        rappture GUI by clicking in the "Result" drop-down, choose
        "Output Log".
    scalar_image : array
        Scalar map (could be trace scalar map or adc).
    logger : logging.Logger
        Debugging purposes only.  Writes to a file in your home
        directory.
    temporary_directory : str
        Temporary directory into which intermediate products are written.
    DWIToDTIEstimation : str
    DiffusionTensorScalarMeasurements : str
    nrrd2nifti_converter : str
        Paths to slicer executables.
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
        self.freesurfer_output = ''
        self.scalar_image = None

        self.temporary_directory = None

        self.slicer_env = None
        self.freesurfer_env = None

        self.setup_slicer_environment()
        self.setup_freesurfer_environment()
        self.setup_logging(use_logging)

    def setup_logging(self, use_logging):
        """
        Initialize logging for debugging purposes.

        Parameters
        ----------
        use_logging : bool
           Either to use logging or not.
        """

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

    def setup_freesurfer_environment(self):
        """
        Setup the environment needed to run freesurfer.
        """
        if socket.gethostname() == 'nciphub':
            # Set environment for NCIPHUB.
            env = dict(os.environ)
            env['FREESURFER_HOME'] = '/apps/share64/debian7/freesurfer/5.3.0'
            env['FSFAST_HOME'] = '/apps/share64/debian7/freesurfer/5.3.0/fsfast'
            env['FSF_OUTPUT_FORMAT'] = 'nii.gz'
            env['SUBJECTS_DIR'] = '/apps/share64/debian7/freesurfer/5.3.0/subjects'
            env['MNI_DIR'] = '/apps/share64/debian7/freesurfer/5.3.0/mni'
            env['FSL_DIR'] = '/usr/lib/fsl'
            env['FSLDIR'] = '/usr/lib/fsl'
            env['LD_LIBRARY_PATH'] = '/usr/lib/fsl/lib'

        else:
            # Set environment for MGH.
            env = dict(os.environ)
            env['FREESURFER_HOME'] = os.path.join(os.environ['HOME'],
                                                  'space/freesurfer')
            env['FSFAST_HOME'] = os.path.join(os.environ['HOME'],
                                              'space/freesurfer/fsfast')
            env['FSF_OUTPUT_FORMAT'] = 'nii.gz'
            env['SUBJECTS_DIR'] = os.path.join(os.environ['HOME'],
                                               'space/data/freesurfer/diffusion_tutorial/diffusion_recons')
            env['MNI_DIR'] = os.path.join(os.environ['HOME'], 'freesurfer/mni')
            env['FSL_DIR'] = os.path.join(os.environ['HOME'], 'space/fsl/fsl')
            env['FSLDIR'] = os.path.join(os.environ['HOME'], 'space/fsl/fsl')

        env['PATH'] = os.environ['PATH'] \
                    + ':' \
                    + os.path.join(env['FREESURFER_HOME'], 'bin')  \
                    + ':' \
                    + os.path.join(env['FSL_DIR'], 'bin') \

        self.freesurfer_env = env


    def setup_slicer_environment(self):
        """
        Setup the environment needed to run slicer.
        """
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

        self.slicer_env = env
        self.DWIToDTIEstimation = os.path.join(slicer_root,
                                               'lib/Slicer-4.2/cli-modules/DWIToDTIEstimation')
        self.DiffusionTensorScalarMeasurements = os.path.join(slicer_root,
                                                              'lib/Slicer-4.2/cli-modules/DiffusionTensorScalarMeasurements')

        # Need to convert to nifti.
        self.nrrd2nifti_converter = os.path.join(slicer_root,
                                                 'lib/Slicer-4.2/cli-modules/ResampleScalarVolume')



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
        self.scalar_image = img.get_data()
    
        shutil.rmtree(self.temporary_directory)

        self.log('Done!')

    def drive_freesurfer(self, zip_file):
        """Calls Freesurfer's dt_recon.  Has no Rappture dependencies, so this
        part can be debugged from the command line.

        Parameters
        ----------
        zip_file : str
            zip file containing DICOMs and associated data files
        """
        with zipfile.ZipFile(zip_file) as zfile:
            self.temporary_directory = tempfile.mkdtemp()

            # Extract each member of the zip file to the temporary
            # directory.
            msg = 'Unzipping zip file to {0}...'
            self.log(msg.format(self.temporary_directory))
            for zipmember in zfile.namelist():
                zfile.extract(zipmember, self.temporary_directory)

            self.run_dt_recon()

            adc_file = os.path.join(self.temporary_directory, 'adc.nii')
            img = nib.load(adc_file)
            self.scalar_image = img.get_data()
    
            shutil.rmtree(self.temporary_directory)

        self.log('Done with freesurfer!')

    def run_dt_recon(self):
        """Run dt_recon on the input files.  The stdout output is collected
        into the dt_recon_output field.
        """
        # We need one dicom file to start us off.  Just take the first one
        # that we find.
        self.log("Running dt_recon...")
        dicom_files = glob.glob(os.path.join(self.temporary_directory, '*.dcm'))
        first_dicom_file = dicom_files[0]

        # The BVEC and BVALS files must currently have these names exactly.
        bvecs_file = os.path.join(self.temporary_directory, 'bvecs.dat')
        bvals_file = os.path.join(self.temporary_directory, 'bvals.dat')

        # Construct the list of arguments and execute the dt_recon process.
        # Save the results from stdout, which we will use to populate the
        # rappture log GUI element.
        # Write the output to the same directory.
        command = "dt_recon --i {dicom_file} --b {bvals} {bvecs} --o {outdir} --no-reg --debug"
        command = command.format(dicom_file=first_dicom_file,
                                 bvals=bvals_file,
                                 bvecs=bvecs_file,
                                 outdir=self.temporary_directory)
        self.log(command)
        self.freesurfer_output = subprocess.check_output(command.split(' '),
                                                         env=self.freesurfer_env)

    def slice_to_str(self, idx):
        """Extract a slice to a base64 string.
        """
        islice = self.scalar_image[:, :, idx]

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
                scalar_image_str = base64.b64encode(tfile2.read())

        return scalar_image_str

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
        self.slicer_output = subprocess.check_output(command.split(' '), env=self.slicer_env)

        command = '{scalar_command} --enumeration Trace {dti_file} {trace_file}'
        command = command.format(scalar_command=self.DiffusionTensorScalarMeasurements,
                                 dti_file=os.path.join(self.temporary_directory, 'dti.nrrd'),
                                 trace_file=os.path.join(self.temporary_directory, 'trace.nrrd'))
        self.log(command)
        self.slicer_output += subprocess.check_output(command.split(' '), env=self.slicer_env)
            
        # Convert it to NIFTI
        command = '{converter} {trace_nrrd} {trace_nifti}'
        command = command.format(converter=self.nrrd2nifti_converter,
                                 trace_nrrd=os.path.join(self.temporary_directory, 'trace.nrrd'),
                                 trace_nifti=os.path.join(self.temporary_directory, 'trace.nii'))
        self.log(command)
        self.slicer_output += subprocess.check_output(command.split(' '), env=self.slicer_env)


    def drive_slicer_on_rappture_inputs(self, slicer_data):
        """
        We know that we are to run slicer, so do it.

        Parameters
        ----------
        slicer_data : str
            Raw base64 string that constitutes the NRRD file as input.
        """
        with tempfile.NamedTemporaryFile(suffix='.nrrd') as tfile:
            tfile.write(slicer_data)
            tfile.flush()
            self.drive_slicer(tfile.name)

        self.driver.put("output.sequence(slicer).about.label", "Trace Map")
        self.driver.put("output.sequence(slicer).index.label", "Slice")
        for j in range(self.scalar_image.shape[2]):

            # Write the label for the jth image.
            self.driver.put("output.sequence(slicer).element({0}).index".format(j), j+1)
            self.driver.put("output.sequence(slicer).element({0}).image.current".format(j),
                            self.slice_to_str(j))


    def drive_freesurfer_on_rappture_inputs(self, freesurfer_data):
        """
        We know that we are to run freesurfer, so do it.

        Parameters
        ----------
        freesurfer_data : str
            Raw base64 string that constitutes the zip file containing all
            the DICOMs and bval/bvec inputs.
        """
        with tempfile.NamedTemporaryFile(suffix='.zip') as tfile:
            tfile.write(freesurfer_data)
            tfile.flush()
            self.drive_freesurfer(tfile.name)

        self.driver.put("output.sequence(freesurfer).about.label", "ADC Map")
        self.driver.put("output.sequence(freesurfer).index.label", "Slice")
        for j in range(self.scalar_image.shape[2]):

            # Write the label for the jth image.
            self.driver.put("output.sequence(freesurfer).element({0}).index".format(j), j+1)
            self.driver.put("output.sequence(freesurfer).element({0}).image.current".format(j),
                            self.slice_to_str(j))


    def run(self):
        """
        Runs the wrapping process from the point of Rappture.
        """
        # The "loader" gui element currently reads in the NRRD file
        # images as a base64 string.  We will write it back out as a real NRRD
        # file and drive a pure-python method with only that as input.
        # Use the loader.
        slicer_data = self.driver.get('input.group(tabs).group(slicer).string(slicer).current')
        self.log("slicer data is {0} bytes.".format(len(slicer_data)))

        freesurfer_data = self.driver.get('input.group(tabs).group(freesurfer).string(freesurfer).current')
        self.log("freesurfer data is {0} bytes.".format(len(freesurfer_data)))

        if len(slicer_data) > 0:
            self.drive_slicer_on_rappture_inputs(slicer_data)
        if len(freesurfer_data) > 0:
            self.drive_freesurfer_on_rappture_inputs(freesurfer_data)

        # Populate the log output.
        output = ''
        if len(self.slicer_output) > 0:
            output += "Output of slicer process\n"
            output += "------------------------\n"
            output += self.slicer_output
        if len(self.freesurfer_output) > 0:
            output += "Output of freesurfer process\n"
            output += "------------------------\n"
            output += self.freesurfer_output

        self.driver.put("output.log", output)

        Rappture.result(self.driver)



if __name__ == "__main__":
    DRIVER = Rappture.library(sys.argv[1])
    WRAPPER = SlicerWrapper(driver=DRIVER, use_logging=True)
    WRAPPER.run()
    #WRAPPER = SlicerWrapper(driver=None, use_logging=True)
    #nrrd_file = '/homes/5/jevans/space/data/slicer/DiffusionMRI_tutorialData/dwi.nhdr'
    #WRAPPER.drive_slicer(nrrd_file)
    sys.exit()
