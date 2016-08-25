# -*- coding: utf-8 -*-

import subprocess
import re

def fetchCpuLoad():
    wmic = subprocess.run(["wmic", "cpu", "get", "loadpercentage"], stdout=subprocess.PIPE, universal_newlines=False)
    match = re.search("[0-9]+", wmic.stdout.decode("utf-8"))
    if match:
        return match.group(0)
    else:
        return "unknown"

