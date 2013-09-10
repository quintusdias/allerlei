import glob
import os
import subprocess
import sys
import tempfile
import zipfile

import Rappture

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
    with zipfile.ZipFile(input_zip_file) as zfile:
        with MyTemporaryDirectory() as tdir:
            print("Temporary directory is {0}".format(tdir.name))
                
            # Extract each member of the zip file to the temporary
            # directory.
            for zipmember in zfile.namelist():
                zfile.extract(zipmember, tdir.name)
    
            # We need one dicom file to start us off.  Just take the first one that we
            # find.
            dicom_files = glob.glob(os.path.join(tdir.name, '*.dcm'))
            first_dicom_file = dicom_files[0]
        
            # The BVEC and BVALS files must currently have these names exactly.
            bvecs_file = os.path.join(tdir.name, 'bvecs.dat')
            bvals_file = os.path.join(tdir.name, 'bvals.dat')
        
            # Write the output to the same directory.
            output_dir = tdir.name
        
            # Construct the list of arguments.
            args = ['dt_recon', '--i', first_dicom_file,
                    '--b', bvals_file, bvecs_file,
                    '--o', output_dir,
                    '--no-reg', '--debug']
            print("Command lines is {0}".format(' '.join(args)))
            try:
                output = subprocess.check_output(args, shell=True)
            except OSError as e:
                import pdb; pdb.set_trace()
                print('hi')
                raise
            except subprocess.CalledProcessError as e:
                import pdb; pdb.set_trace()
                print('hi')
                raise
        
    return output

if __name__ == "__main__":
    io = Rappture.library(sys.argv[1])
    zipdata = io.get('input.string(zipfile).current')

    with tempfile.NamedTemporaryFile(suffix='.zip', mode='wb', delete=False) as zfile:
        zfile.write(zipdata)
        zfile.flush()
        output = drive_dtrecon(zfile.name)

    driver.put("output.log", output)
    Rappture.result(driver)
    sys.exit()

