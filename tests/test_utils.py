from arvados_cwl_tester.helpers import create_input_yml, load_file
from arvados_cwl_tester import create_ouputs_dict, check_if_collection_output_not_empty, basic_arvados_test

uuid = "arind-j7d0g-11cq990ue0u0cyg"


def test_load_file():
    assert type(load_file("./tests/cwl_workflows/test_single_step/test_single_step.cwl")) == list


def test_create_input_yml():
    create_input_yml(
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


def test_create_input_yml_empty():
    create_input_yml({})


# Example how to run this tests on some CommanLineTool
def test_single_step():
    input_name = "example.txt"
    run = basic_arvados_test(
        uuid,
        "Example test",
        "./cwl_workflows/test_single_step/test_single_step.cwl",
        {
            "name": input_name
        }
    )
    assert check_if_collection_output_not_empty(run)
    output_dict = create_ouputs_dict(run)
    assert input_name in output_dict
    assert output_dict[input_name]["size"] == 0
    assert output_dict[input_name]["basename"] == input_name
