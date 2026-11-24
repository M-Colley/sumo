#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
# Copyright (C) 2008-2026 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License, v. 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    runner.py
# @author  Mark Colley
# @date    2026-11-24

import os
import sys
import xml.etree.ElementTree as ET

if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import sumolib  # noqa
import traci  # noqa

traci.start([sumolib.checkBinary("sumo"), "-r", "input_routes.rou.xml",
             "-a", "input_additional.add.xml", "--no-step-log", "--no-duration-log"] + sys.argv[1:], numRetries=1)
try:
    traci.simulationStep(20)
    traci.simulation.saveState("vtype-reload.snap.xml")
    state = ET.parse("vtype-reload.snap.xml")
    state.find("./vTypeDistribution[@id='dist']").set("vTypes", "t2")
    state.write("vtype-reload.snap.xml")

    traci.simulation.loadState("vtype-reload.snap.xml")
    traci.vehicle.add("after1", "r", "t1", depart="21", departSpeed="max")
    traci.vehicle.add("after2", "r", "t2", depart="24", departSpeed="max")
    traci.simulationStep(45)
finally:
    traci.close()

output = ET.parse("counts.xml").getroot()
counts = {tag: [int(interval.find("./edge[@id='AB']").attrib["departed"])
                for interval in output.findall(f"./interval[@id='{tag}']")]
          for tag in ("selected", "all")}
assert counts["all"] == [1, 2], counts
assert counts["selected"] == [1, 1], counts
print("The reloaded distribution selects only its current member.")
