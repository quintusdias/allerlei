"""
Wrapper for slicer
"""
import base64
import logging
import os
import shutil
import re
import socket
import subprocess
import sys
import tempfile

import skimage.io
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
    slicer_temp_dir, freesurfer_temp_dir : str
        Temporary directory into which intermediate products are written.
    slicer_data_root, freesurfer_data_root : str
        Paths where we can find example diffusion data sets.
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

        self.slicer_data_root = None
        self.freesurfer_data_root = None
        self.logger = None

        self.slicer_temp_dir = tempfile.mkdtemp()
        self.freesurfer_temp_dir = tempfile.mkdtemp()

        self.slicer_env = None
        self.freesurfer_env = None

        self.setup_slicer_environment()
        self.setup_freesurfer_environment()
        self.setup_logging(use_logging)


    def __del__(self):
        """
        Clean up any lingering resources upon exit.
        """
        shutil.rmtree(self.slicer_temp_dir)
        shutil.rmtree(self.freesurfer_temp_dir)



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

            self.freesurfer_data_root = '/data/groups/qinportal/diffusion'

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

            self.freesurfer_data_root = '/homes/5/jevans/space/data/diffusion'

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

        env['FSLOUTPUTTYPE'] = 'NIFTI_GZ'
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
        # Construct the necessary environment.
        # This has to include the LD_LIBRARY_PATH environment variable.
        env = dict(os.environ)
        if socket.gethostname() == 'nciphub':

            self.slicer_data_root = '/data/groups/qinportal/diffusion'

            slicer_root = '/apps/share64/debian7/slicer/4.2.1/Slicer-build'

        else:
            # MGH setup.

            self.slicer_data_root = '/homes/5/jevans/space/data/diffusion'

            slicer_root = '/usr/pubsw/packages/slicer/Slicer-4.2.2-1-linux-amd64'

        env['PATH'] = os.environ['PATH'] \
                    + ':' \
                    + os.path.join(slicer_root, 'lib/Slicer-4.2/cli-modules')

        env['LD_LIBRARY_PATH'] = os.path.join(slicer_root, 'lib/Slicer-4.2') \
                               + ':' \
                               + os.path.join(slicer_root, 'lib/Teem-1.10.0') \
                               + ':' \
                               + os.path.join(slicer_root, 'lib/Slicer-4.2/cli-modules')

        self.slicer_env = env



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
        self.log('Running slicer...')
        self.run_slicer(nrrdfile)
    
        trace_file = os.path.join(self.slicer_temp_dir, 'trace.nii')
        shutil.copyfile(trace_file,
                        os.path.join(os.environ['HOME'], 'trace.nii'))
        img = nib.load(trace_file)
        self.scalar_image = img.get_data()
    
        self.log('Done!')

    def drive_freesurfer(self, nrrdfile, bvalsfile, bvecsfile):
        """Calls Freesurfer's dt_recon.  Has no Rappture dependencies, so this
        part can be debugged from the command line.
        """
        self.log('Starting to drive freesurfer!')
        self.run_dt_recon(nrrdfile, bvalsfile, bvecsfile)

        adc_file = os.path.join(self.freesurfer_temp_dir, 'adc.nii')
        shutil.copyfile(adc_file, os.path.join(os.environ['HOME'], 'adc.nii'))
        img = nib.load(adc_file)
        self.scalar_image = img.get_data()
    
        self.log('Done running freesurfer!')

    def run_dt_recon(self, nrrdfile, bvalsfile, bvecsfile):
        """Run dt_recon on the input files.  The stdout output is collected
        into the dt_recon_output field.
        """
        self.log("Running dt_recon...")

        # Construct the list of arguments and execute the dt_recon process.
        # Save the results from stdout, which we will use to populate the
        # rappture log GUI element.
        # Write the output to the same directory.
        command = "dt_recon --i {nrrd} --b {bvals} {bvecs} --o {outdir} --no-reg --debug"
        command = command.format(nrrd=nrrdfile,
                                 bvals=bvalsfile,
                                 bvecs=bvecsfile,
                                 outdir=self.freesurfer_temp_dir)
        self.log(command)
        self.freesurfer_output = subprocess.check_output(command.split(' '),
                                                         env=self.freesurfer_env)
        self.log("Finished running dt_recon...")

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
            skimage.io.imsave(pngfile.name, faux_3d)
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
        self.log("Starting to run slicer...")
        # Construct a shell script with all the commands.
        command = 'DWIToDTIEstimation --enumeration WLS {dwi_file} {dti_file} {scalar_file}'
        command = command.format(dwi_file=nrrd_file,
                                 dti_file=os.path.join(self.slicer_temp_dir, 'dti.nrrd'),
                                 scalar_file=os.path.join(self.slicer_temp_dir, 'scalar_volume_b.nrrd'))
        self.log(command)
        self.slicer_output = subprocess.check_output(command.split(' '), env=self.slicer_env)

        command = 'DiffusionTensorScalarMeasurements --enumeration Trace {dti_file} {trace_file}'
        command = command.format(dti_file=os.path.join(self.slicer_temp_dir, 'dti.nrrd'),
                                 trace_file=os.path.join(self.slicer_temp_dir, 'trace.nrrd'))
        self.log(command)
        self.slicer_output += subprocess.check_output(command.split(' '), env=self.slicer_env)
            
        # Convert it to NIFTI
        command = 'ResampleScalarVolume {trace_nrrd} {trace_nifti}'
        trace_nrrd = os.path.join(self.slicer_temp_dir, 'trace.nrrd')
        trace_nifti = os.path.join(self.slicer_temp_dir, 'trace.nii')
        command = command.format(trace_nrrd=trace_nrrd,
                                 trace_nifti=trace_nifti)
        self.log(command)
        self.slicer_output += subprocess.check_output(command.split(' '),
                                                      env=self.slicer_env)
        self.log("Finished running slicer...")


    def drive_slicer_on_rappture_inputs(self, slicer_file):
        """
        We know that we are to run slicer, so do it.

        Parameters
        ----------
        slicer_file : str
            NRRD file to use as input to slicer.
        """
        self.drive_slicer(slicer_file)

        self.driver.put("output.sequence(slicer).about.label", "Slicer Trace Map")
        self.driver.put("output.sequence(slicer).index.label", "Slice")
        for j in range(self.scalar_image.shape[2]):

            # Write the label for the jth image.
            self.driver.put("output.sequence(slicer).element({0}).index".format(j), j+1)
            self.driver.put("output.sequence(slicer).element({0}).image.current".format(j),
                            self.slice_to_str(j))


    def drive_freesurfer_on_rappture_inputs(self, nrrdfile, bvalsfile, bvecsfile):
        """
        We know that we are to run freesurfer, so do it.

        Parameters
        ----------
        freesurfer_file : str
            Zip file of DICOMs to use as freesurfer input.
        """
        self.drive_freesurfer(nrrdfile, bvalsfile, bvecsfile)

        self.driver.put("output.sequence(freesurfer).about.label", "Freesurfer ADC Map")
        self.driver.put("output.sequence(freesurfer).index.label", "Slice")
        for j in range(self.scalar_image.shape[2]):

            # Write the label for the jth image.
            self.driver.put("output.sequence(freesurfer).element({0}).index".format(j), j+1)
            self.driver.put("output.sequence(freesurfer).element({0}).image.current".format(j),
                            self.slice_to_str(j))


    def run_differencing(self, slicer_scalar_file, freesurfer_scalar_file):
        """
        Produces difference map between slicer and freesurfer runs.

        Parameters
        ----------
        slicer_scalar_file : str
            Output of slicer diffusion tensor imaging.  The trace map.
        freesurfer_scalar_file : str
            Output of freesurfer diffusion tensor imaging.  The adc map.

        Returns
        -------
        difference_data : numpy image array
            Freesurfer subtracted from Slicer.
        """
        self.log("Running fslmaths...")
        # First convert the slicer trace map into an adc map.
        with tempfile.NamedTemporaryFile(suffix="*.nii.gz") as tfile:
            command = "fslmaths {trace} -div 3 {adc}"
            command = command.format(trace=slicer_scalar_file, adc=tfile.name)
            self.log(command)
            subprocess.check_output(command.split(' '),
                                    env=self.freesurfer_env)


            # Now construct the difference map.
            with tempfile.NamedTemporaryFile(suffix="*.nii.gz") as tfile2:
                command = "fslmaths {slicer} -sub {freesurfer} {output}"
                command = command.format(slicer=tfile.name,
                                         freesurfer=freesurfer_scalar_file,
                                         output=tfile2.name)
                self.log(command)
                subprocess.check_output(command.split(' '),
                                        env=self.freesurfer_env)

                diff_img = nib.load(tfile2.name)
                self.scalar_image = diff_img.get_data()

        self.log("Finished running fslmaths...")


    def run_differencing_for_rappture(self):
        """
        Only to be run when both freesurfer and slicer have run.
        """
        self.log("Running differencing for rappture environment...")

        self.driver.put("output.sequence(difference).about.label",
                        "Difference Map")
        self.driver.put("output.sequence(difference).index.label", "Slice")

        slicer_scalar_file = os.path.join(self.slicer_temp_dir, 'trace.nii')
        freesurfer_scalar_file = os.path.join(self.freesurfer_temp_dir,
                                              'adc.nii')

        self.run_differencing(slicer_scalar_file, freesurfer_scalar_file)


        for j in range(self.scalar_image.shape[2]):

            # Write the label for the jth image.
            self.driver.put("output.sequence(difference).element({0}).index".format(j), j+1)
            self.driver.put("output.sequence(difference).element({0}).image.current".format(j),
                            self.slice_to_str(j))


        self.log("Finished running differencing for rappture environment...")

    def stage_freesurfer_input(self, nrrdfile, niftifile, bvalsfile, bvecsfile):
        """
        """
        self.log("Starting to convert inputs for freesurfer consumption...")
        # This converts the 4D NRRD file to a 5D nifti.
        with tempfile.NamedTemporaryFile(suffix=".nii") as tfile:
            command = "ResampleScalarVectorDWIVolume {nrrd} {nifti}"
            command = command.format(nrrd=nrrdfile, nifti=tfile.name)
            self.log(command)
            output = subprocess.check_output(command.split(' '),
                                             env=self.slicer_env)
            self.log(output)

            # Get rid of that singleton dimension.
            img5d = nib.load(tfile.name)
            data5d = img5d.get_data()
            new_shape = [data5d.shape[0],
                         data5d.shape[1],
                         data5d.shape[2],
                         data5d.shape[4]]
            data4d = np.reshape(data5d, new_shape)
            affine = img5d.get_affine()
            img4d = nib.nifti1.Nifti1Image(data4d, affine)
            nib.nifti1.save(img4d, niftifile)

        bval, bvecs = self.extract_bvals_bvecs_from_nrrd(nrrdfile)

        # Write the bvals file.
        num_bvecs = len(bvecs)
        with open(bvalsfile, 'w') as fptr:
            for _ in range(num_bvecs):
                fptr.write("{:.6f}\n".format(bval))

        with open(bvecsfile, 'w') as fptr:
            for bvec in bvecs:
                fptr.write("{:f} {:f} {:f}\n".format(bvec[0], bvec[1], bvec[2]))

        self.log("Finished converting inputs for freesurfer consumption...")

    def extract_bvals_bvecs_from_nrrd(self, nrrdfile):
        """
        Extract bvals, bvecs from a NRRD file.

        Parameters
        ----------
        nrrdfile : str
            4D NRRD file, has bvals and bvecs in header.

        Returns
        -------
        bval, bvecs : tuple of bval, bvectors extracted from header of NRRD
        file.
        """
        bval = None
        bvecs = []

        # Define a regular expression for the bval lines.  E.g.
        # DWMRI_b-value:=1000.000000
        bval_regex = re.compile("DWMRI_b-value:=(?P<bval>\d*.\d*)")

        # Define a regular expression for the bvec lines, e.g.
        # DWMRI_gradient_0002:=-0.957381 0.077086 -0.278338
        # So there are as many as 9999+1 gradient vectors?
        # The floating point numbers are normalized, consisting of
        # six digits, with one space between them and NOT at the end.
        bvec_regex = re.compile("DWMRI_gradient_\d{4}:=(?P<floats>([+-]{0,1}0.\d{6}\s{0,1}){3})")
        with open(nrrdfile, 'r') as fptr:
            # Read until we get to the end of the header.
            line = fptr.readline()
            while line != '\n':
                match = bval_regex.match(line)
                if match is not None:
                    bval = float(match.group('bval'))
                match = bvec_regex.match(line)
                if match is not None:
                    # The match group is a string of three floats separated by
                    # a space.
                    strlist = match.group('floats').split(' ')
                    bvecs.append([float(x) for x in strlist])
                line = fptr.readline()

        return bval, bvecs

    def run(self):
        """
        Runs the wrapping process from the point of Rappture.
        """
        choice = self.driver.get('input.choice.current')
        if choice == 'dwi.nrrd':
            nrrdfile = os.path.join(self.slicer_data_root, choice)
            self.drive_slicer_on_rappture_inputs(nrrdfile)
            with tempfile.NamedTemporaryFile(suffix='.nii') as tnifti:
                with tempfile.NamedTemporaryFile(suffix='.dat') as tbval:
                    with tempfile.NamedTemporaryFile(suffix='.dat') as tbvec:
                        self.stage_freesurfer_input(nrrdfile,
                                                    tnifti.name,
                                                    tbval.name,
                                                    tbvec.name)
                        self.drive_freesurfer_on_rappture_inputs(tnifti.name,
                                                                 tbval.name,
                                                                 tbvec.name)

        self.run_differencing_for_rappture()

        # Populate the log output.
        output = ''
        if len(self.slicer_output) > 0:
            output += "Output of slicer process\n"
            output += "------------------------\n"
            output += self.slicer_output
            output += '\n\n\n'
        if len(self.freesurfer_output) > 0:
            output = "Output of freesurfer process\n"
            output = "----------------------------\n"
            output = self.freesurfer_output
            output += '\n\n\n'
        self.driver.put("output.log", output)


        Rappture.result(self.driver)



if __name__ == "__main__":
    DRIVER = Rappture.library(sys.argv[1])
    WRAPPER = SlicerWrapper(driver=DRIVER, use_logging=False)
    WRAPPER.run()
    sys.exit()
