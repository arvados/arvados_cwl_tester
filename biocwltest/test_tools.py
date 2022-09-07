from biocwltest.helpers import *
from biocwltest import *


def test_load_file():
    assert type(helpers.load_file("./examples/example_pipeline.cwl")) == list


def test_create_input_yml():
    helpers.create_input_yml(
        {
            "metaInfoFile": {
                "class": "File",
                "location": "keep:b05083d7db79c2e4e211dbef369e98a7+76/sampleList_E-MTAB-8208.txt",
            },
            "fastqCollection": {
                "class": "File",
                "location": "keep:00780063929dcd34186ae2394505202d+422439",
            }
        }
    )


def test_run_cwl(): # 
    inputs = {"name": "example.txt"}
    run_cwl("components/single_step/single_step.cwl", inputs)
