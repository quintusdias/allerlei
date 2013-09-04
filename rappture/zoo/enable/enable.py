# ----------------------------------------------------------------------
#  EXAMPLE: Rappture <enable> attributes
# ======================================================================
#  AUTHOR:  Michael McLennan, Purdue University
#  Copyright (c) 2004-2005  Purdue Research Foundation
#
#  See the file "license.terms" for information on usage and
#  redistribution of this file, and for a DISCLAIMER OF ALL WARRANTIES.
# ======================================================================
import sys
import Rappture


# open the XML file containing the run parameters
driver = Rappture.library('tool.xml')
io = Rappture.library(sys.argv[1])

model = io.get("input.(model).current")
if model == "dd":
    result = "Drift-Diffusion:\n"
    recomb = io.get("input.(dd).(recomb).current")
    if recomb:
        taun = io.get("input.(dd).(taun).current")
        taup = io.get("input.(dd).(taup).current")
        result += "  TauN:  {0}\n  TauP  {1}".format(taun, taup)
elif model == "bte":
    result = "Boltzmann Transport Equation:\n"
    temp = io.get("input.(bte).(temp).current")
    secret = io.get("input.(bte).(secret).current")
    result += "  Temperature:  {0}\n  Hidden number:  {1}"
    result = result.format(temp, secret)
elif model == "negf":
    result = "NEGF Analysis:\n"
    tbe = io.get("input.(negf).(tbe).current")
    tau = io.get("input.(negf).(tau).current")
    result += "  Tight-binding energy: {0}\n  High-energy lifetime: {1}\n"
    result = result.format(tbe, tau)
else:
    raise RuntimeError("can't understand {0}".format(model))

driver.put("output.log", result)

Rappture.result(driver)
sys.exit()
