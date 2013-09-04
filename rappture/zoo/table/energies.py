# ----------------------------------------------------------------------
#  EXAMPLE: Rappture <energies> elements
# ======================================================================
import random
import sys

import Rappture


# open the XML file containing the run parameters
driver = Rappture.library('tool.xml')
io = Rappture.library(sys.argv[1])

L = io.get("input.number(L).current")
L = Rappture.Units.convert(L, "m", "off")

emass = float(io.get("input.number(emass).current"))
m = emass * 9.11e-31  # kg
h = 4.13566743e-15    # in eVs
J2eV = 6.241506363e17
nhomo = round(random.random() * 19 + 1)

driver.put("output.table.about.label", "Energy Levels")
driver.put("output.table.column(labels).label", "Name")
driver.put("output.table.column(energies).label", "Energy")
driver.put("output.table.column(energies).units", "eV")

for n in range(1,21):
    E = float(n) * float(n) * h * h / (8.0 * m * float(L)**2 * J2eV)
    label = "HOMO" if n == nhomo else str(n)
    driver.put(path="output.table.data",
               value="{0} {1:.3g}\n".format(label, E),
               append=True)

Rappture.result(driver)
sys.exit()
