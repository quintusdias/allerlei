import base64
import os
import subprocess
import sys
import tempfile

import Rappture

def drive_output(input_file, outputfile, angle):
    args = ['convert', input_file.name, '-rotate', str(angle)]
    args.append(outputfile.name)
    log = ' '.join(args)
    log += '\n'
    log += subprocess.check_output(args)
    return log

if __name__ == "__main__":
    driver = Rappture.library('tool.xml')

    io = Rappture.library(sys.argv[1])

    # Get the input image data and angle by which to rotate.
    data = io.get('input.image.current')
    anglestr = io.get('input.(angle).current')
    angle = anglestr.split('deg')[0]

    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bmp') as ifile:
        ifile.write(data)
        ifile.flush()
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bmp') as ofile:
            log = drive_output(ifile, ofile, angle)
            with open(ofile.name, 'r') as oifile:
                outdata = oifile.read()
            log += "Size of output data is {0} bytes".format(len(outdata))

    driver.put("output.log", log)
    driver.put("output.image(outi).about.label", "Rotated Image")
    driver.put("output.image(outi).current", base64.b64encode(outdata))

    # Add a little html node.
    htmltext = 'html://<p style="text-align: center;">'
    htmltext += '<a href="angles.html">Learn more about angles...</a></p>'
    driver.put("output.image(outi).note.contents", htmltext)


    Rappture.result(driver)
    sys.exit()
