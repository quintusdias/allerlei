# ----------------------------------------------------------------------
#  EXAMPLE: Rappture <sequence> elements
# ======================================================================
import base64
import sys
import tempfile

import skimage.io
import Rappture

if __name__ == "__main__":

    # open the XML file containing the run parameters
    driver = Rappture.library("tool.xml")
    io = Rappture.library(sys.argv[1])

    data = io.get("input.image.current")
    nframes = int(io.get("input.(nframes).current"))

    # Make a temporary image file from this base64 data.
    # Read it back in again (as an image) to make use of numpy.
    with tempfile.NamedTemporaryFile(suffix='.jpg', mode='wb') as tfile:
        tfile.write(base64.b64decode(data))
        tfile.flush()

        image_data = skimage.io.imread(tfile.name)
        height, width, nchannels = image_data.shape

        # Make the sequence image half the size of the original.
        zwidth = int(round(0.5*width))
        zheight = int(round(0.5*height))

        driver.put("output.sequence(outs).about.label",
                   "Animated sequence")
        driver.put("output.sequence(outs).index.label", "Frame")

        for n in range(nframes):
            frac = (n + 1) / float(nframes)
            x0 = int(round(0.5 * frac * width))
            y0 = int(round(0.5 * frac * height))
            frame_data = image_data[x0:x0+zheight, y0:y0+zwidth, :]

            cmd = "output.sequence(outs).element({0}).index".format(n)
            driver.put(cmd, n + 1)

            # Write the frame out to a temporary file, suck it back 
            # into a base64 string.
            with tempfile.NamedTemporaryFile(suffix='.jpg') as tempframef:
                skimage.io.imsave(tempframef.name, frame_data)
                with open(tempframef.name, 'r') as fptr:
                    jpeg_file_data = fptr.read()

            # Now write that "string" back to the frame element.
            cmd = "output.sequence(outs).element({0}).image.current"
            cmd = cmd.format(n)
            driver.put(cmd, base64.b64encode(jpeg_file_data))

            cmd = "output.sequence(outs).element({0}).about.label"
            cmd = cmd.format(n)
            driver.put(cmd, "{0} of {1}".format(n + 1, nframes))

    Rappture.result(driver)
    sys.exit()
