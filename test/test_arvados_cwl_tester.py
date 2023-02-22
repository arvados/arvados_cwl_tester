from arvados_cwl_tester import *
from arvados_cwl_tester.helpers import create_input_yml, load_file, change_local_paths_to_abs
import os

def test_load_file():
    assert (
        type(load_file("./test/cwl_workflows/test_single_step/test_single_step.cwl"))
        == list
    )

def test_change_local_paths_to_abs_dict():

    assert change_local_paths_to_abs({
        "local_directory": {
            "class": "Directory",
            "path": "./test"
        },
        "arvados_directory": {
            "class": "Directory",
            "path": "keep:cdsfdnkcnhksjcnkwr234"
        }
    }) == {
        "local_directory": {
            "class": "Directory",
            "path": f"{os.getcwd()}/test"
        },
        "arvados_directory": {
            "class": "Directory",
            "path": "keep:cdsfdnkcnhksjcnkwr234"
        }
    }

def test_change_local_paths_to_abs_arrays():
    
    assert change_local_paths_to_abs({
        "directories": [
            {"class": "Directory", "path": "./test/data"},
            {"class": "Directory","path": "keep:cdscsijee"}
            ],
        "files": [
            {"class": "File", "path": "keep:cdsfdnkcnhksjcnkwr234/some_file.txt"},
            {"class": "File", "path": "./test/data/my_testing_file.txt"}
            ]
            }) == {
        "directories": [
            {"class": "Directory", "path": f"{os.getcwd()}/test/data"},
            {"class": "Directory", "path": "keep:cdscsijee"}
            ],
        "files": [
            {"class": "File","path": "keep:cdsfdnkcnhksjcnkwr234/some_file.txt"},
            {"class": "File","path": f"{os.getcwd()}/test/data/my_testing_file.txt"}
            ]
            }

def test_change_local_paths_cat():
    inputs_dictionary = { "file": {"class": "File", "path": "./test/data/my_testing_file.txt"}}
    assert change_local_paths_to_abs(inputs_dictionary) == {
            "file": {"class": "File", "path": f"{os.getcwd()}/test/data/my_testing_file.txt"}
        }

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


def test_create_input_yml_empty_dict():
    create_input_yml({})


def test_create_input_yml_empty():
    create_input_yml()


def test_variables_access():
    print(VARIABLES)
    assert MY_TESTING_FILE == {
            "class": "File",
            "path": "./test/data/my_testing_file.txt"
        }


def test_variables_and_projects():
    assert VARIABLES["projects"] == PROJECTS


# TODO: debug this test
# def test_step_cat():
#     arvados_project_uuid(PROJECTS["ours"])
#     result = arvados_run(
#         "./test/cwl_workflows/test_cat/test_cat.cwl",
#         {
#         "file": {
#             "class": "File",
#             "path": "./test/data/my_testing_file.txt"
#             }
#         }
#     )


def test_single_step_():
    arvados_project_uuid(PROJECTS["ours"])
    result = arvados_run(
        "./test/cwl_workflows/test_single_step/test_single_step.cwl",
        { "name": "example" }
    )

    assert "example.txt" in result.files
    assert result.files["example.txt"]["size"] == 0

    # TODO implement out related to cwl.output.json
    # outputs = result.outputs
    # assert len(outputs["testing_result"]) == 1
    # assert outputs["testing_result"]["size"] == 0
    # assert outputs["testing_result"]["basename"] == "example.txt"


def test_single_step_define_target_yourself():
    result = arvados_run(
        "./test/cwl_workflows/test_single_step/test_single_step.cwl",
        {"name": "example"},
        project_uuid=PROJECTS["ours"]
    )

    assert "example.txt" in result.files
    assert result.files["example.txt"]["size"] == 0
    assert result.command == ["touch", "example.txt", "example"]


def test_workflow():
    arvados_project_uuid(PROJECTS["ours"])
    result = arvados_run(
        "./test/cwl_workflows/test_workflow.cwl",
        {"name": "workflow_example"}
    )

    assert "workflow_example.txt" in result.files
    assert result.command != ["touch", "example.txt", "example"]

    # TODO implement out related to cwl.output.json
    # assert len(out["testing_results"]) == 3
    # assert out["testing_results"][0]["size"] == 0
    # assert out["testing_results"][0]["basename"] == "workflow_example.txt"
    # assert out["testing_results"][1]["size"] == 0
    # assert out["testing_results"][1]["basename"] == "workflow_example.txt"
    # assert out["testing_results"][2]["size"] == 0
    # assert out["testing_results"][2]["basename"] == "workflow_example.txt"
