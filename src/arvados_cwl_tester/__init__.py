from pathlib import Path

from arvados_cwl_tester.arvados_utils import arvados_run, arvados_project_uuid
from arvados_cwl_tester.helpers import load_json

# Load global variables from variables.json

VARIABLES = None

if Path("./test/variables.json").is_file():
    VARIABLES = load_json("./test/variables.json")
    for key, value in load_json("./test/variables.json").items():
        if key.upper() not in globals():
            globals()[key.upper()] = value
