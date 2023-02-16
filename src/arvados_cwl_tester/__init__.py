import os

from arvados_cwl_tester.arvados_utils import arvados_run
from arvados_cwl_tester.helpers import load_json

# Load global variables from globals.json
if os.path.isfile("./test/variables.json"):
    for key, value in load_json("./test/variables.json").items():
        if key.upper() not in globals():
            globals()[key.upper()] = value
