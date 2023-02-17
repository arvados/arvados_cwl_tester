from arvados_cwl_tester.helpers import create_input_yml, load_file
from arvados_cwl_tester.arvados_utils import create_outputs_dict
from arvados_cwl_tester import arvados_run

TESTING_PROJECT = "arind-j7d0g-11cq990ue0u0cyg"


def test_load_file():
    assert (
        type(load_file("./tests/cwl_workflows/test_single_step/test_single_step.cwl"))
        == list
    )


def test_create_input_yml():
    create_input_yml(
        {
            "metaInfoFile": {
                "class": "File",
                "location": "keep:b05083d7db/sampleList_E-MTAB-8208.txt",
            },
            "fastqCollection": {
                "class": "File",
                "location": "keep:007+422439",
            },
        }
    )

def test_create_input_yml_empty():
    create_input_yml({})


def test_create_input_yml_empty():
    create_input_yml()


def test_single_step():
    out = arvados_run(
        TESTING_PROJECT,
        "./tests/cwl_workflows/test_single_step/test_single_step.cwl",
        {"name": "example.txt"},
    )
    print(out)
    
    # TODO implement out
    # assert len(out["testing_result"]) == 1
    # assert out["testing_result"]["size"] == 0
    # assert out["testing_result"]["basename"] == "example.txt"


def test_workflow():
    out = arvados_run(
        TESTING_PROJECT,
        "./tests/cwl_workflows/test_workflow.cwl",
        {"name": "workflow_example.txt"},
    )
    # assert len(out["testing_results"]) == 3
    # assert out["testing_results"][0]["size"] == 0
    # assert out["testing_results"][0]["basename"] == "workflow_example.txt"
    # assert out["testing_results"][1]["size"] == 0
    # assert out["testing_results"][1]["basename"] == "workflow_example.txt"
    # assert out["testing_results"][2]["size"] == 0
    # assert out["testing_results"][2]["basename"] == "workflow_example.txt"
