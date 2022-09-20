from biocwltest import helpers
from biocwltest.basic_tests import basic_arvados_test
from biocwltest.cwl_runner import run_cwl


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
    run_cwl("components/single_step/single_step.cwl", {"name": "example.txt"})


def test_basic_arvados_test():
    assert basic_arvados_test("arind-j7d0g-1p06n3sacrzeqrt", "Test", "./examples/example_pipeline.cwl", {"name": "testing_name"}) == True
