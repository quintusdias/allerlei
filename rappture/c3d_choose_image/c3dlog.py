import subprocess
import sys
import tempfile

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

    io = Rappture.library(sys.argv[1])
    nii_data = io.get('input.string(niftyfile).current')

    with tempfile.NamedTemporaryFile(suffix='.nii', mode='wb', delete=False) as nii:
        nii.write(nii_data)
        output = drive_c3d(nii.name)

    driver.put("output.log", output)
    Rappture.result(driver)
    sys.exit()

