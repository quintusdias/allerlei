# ----------------------------------------------------------------------
#  EXAMPLE: Rappture <group> elements
# ======================================================================
import sys

import Rappture

if __name__ == "__main__":

    # open the XML file containing the run parameters
    driver = Rappture.library('tool.xml')
    io = Rappture.library(sys.argv[1])

    re = io.get("input.group.(models).(recomb).current")
    tn = io.get("input.group.(models).(tau).(taun).current")
    tp = io.get("input.group.(models).(tau).(taup).current")

    temp = io.get("input.group.(ambient).(temp).current")

    msg = "Models:\n"
    msg += "  Recombination:  {0}\n"
    msg += "  taun:  {1}\n"
    msg += "  taup:  {2}\n\n"
    msg += "Ambient:\n"
    msg += "  tempK = {3}"

    msg = msg.format(re, tn, tp, temp)
    driver.put("output.log", msg)

    Rappture.result(driver)
    sys.exit()

