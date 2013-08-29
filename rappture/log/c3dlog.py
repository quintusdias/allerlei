import subprocess
import sys

import Rappture

def drive_c3d(input_file):
    """Calls c3d to print image metadata to stdout.

    Parameters
    ----------
    input_file : str
        NIFTI file to be queried for metadata

    Returns
    -------
    output : str
        Metadata produced on stdout by system call to c3d.
    """
    args = ['c3d', input_file, '-info-full']
    output = subprocess.check_output(args)
    return output

if __name__ == "__main__":
    driver = Rappture.library('tool.xml')

    input_file = '/homes/5/jevans/space/data/nifti/zstat1.nii'
    output = drive_c3d(input_file)

    driver.put("output.log", output)
    Rappture.result(driver)
    sys.exit()

