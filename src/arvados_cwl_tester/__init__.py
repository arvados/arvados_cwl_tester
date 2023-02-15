import os

from arvados_cwl_tester.arvados_utils import *
from arvados_cwl_tester.helpers import load_json

# load variables from json file
FILES = None
VARIABLES = None
DIRECTORIES = None
UUIDS = None

if os.path.isfile("./test/variables.json"):
    VARIABLES = load_json("./test/variables.json")

    FILES = VARIABLES["resources"]["files"]
    UUIDS = VARIABLES["testing_projects"]
    DIRECTORIES = VARIABLES["resources"]["directories"]
