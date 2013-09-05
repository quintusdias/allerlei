# ----------------------------------------------------------------------
#  EXAMPLE: Rappture <choice> elements
# ======================================================================
import sys

import Rappture

# open the XML file containing the run parameters
io = Rappture.library(sys.argv[1])

io.put("output.choice(outs).about.label", "Echo of choice")
choice = io.get("input.(stats).current")
io.put("output.choice(outs).current", choice)

Rappture.result(io)
sys.exit()
