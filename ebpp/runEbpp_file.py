import pandapower as pp
import pandas as pd
import pandapower.plotting.plotly as pltly
import pandapower.plotting as plt

import json
import os
import sys

import ebpp
import utils as utils

from errors import ConvError, InvalidError, JsonError, PPError



# def RUN(data):
#     try:
#         #json.loads(data)
#         json.load(data)
#     except:
#         raise JsonError("Could not parse json from request data")

#     status = utils.get_or_error("status", data)
#     if status == "SIM_REQUEST":
#         return ebpp.sim_request(data)
#     else:
#         raise InvalidError(f"Status \"{status}\" is not a valid status code.")



_json=None
with open(file="C:\FILES\PROJECTS\pandafp\demo\EMS\J_CSPA_FULL_cfg.json", encoding='utf-8') as json_file:
    print(json_file)
    _json = json.load(json_file)

print("LEN:", len(_json))

data=_json

status = utils.get_or_error("status", data)
resultRun = None,

if status == "SIM_REQUEST":
    resultRun = ebpp.sim_request(data)
print("RESULT:", resultRun)

