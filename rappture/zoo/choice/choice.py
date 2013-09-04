# ----------------------------------------------------------------------
#  EXAMPLE: Rappture <choice> elements
# ======================================================================
import sys

import Rappture

# open the XML file containing the run parameters
driver = Rappture.library('tool.xml')
io = Rappture.library(sys.argv[1])

driver.put("output.choice(outs).about.label", "Echo of choice")
choice = io.get("input.(stats).current")
driver.put("output.choice(outs).current", choice)

Rappture.result(driver)
sys.exit()
