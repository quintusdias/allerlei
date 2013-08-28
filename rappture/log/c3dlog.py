import subprocess
import sys

import Rappture

driver = Rappture.library('tool.xml')

args = ['c3d']
#args.append(sys.argv[1])
args.append('/homes/5/jevans/space/data/nifti/zstat1.nii')
args.append('-info-full')
output = subprocess.check_output(args)

driver.put("output.log", output)
Rappture.result(driver)
sys.exit()
