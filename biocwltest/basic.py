from biocwltest.arvados_connection import create_new_project, find_process_in_new_project, check_if_process_is_finished, check_if_project_is_completed, check_list_of_outputs
from biocwltest.arvados_connection.entities import Process
from biocwltest.cwl_runner import run_cwl_arvados
from biocwltest.helpers import load_json

import os


if os.path.isfile("./test/variables.json"):
    VARIABLES = load_json("./test/variables.json")
    FILES = VARIABLES["resources"]["files"]


def basic_arvados_test(target_project:str, test_name: str, cwl_path: str, inputs_dictionary: dict) -> Process:
    new_created_project = create_new_project(target_project, test_name)
    run_cwl_arvados(cwl_path, inputs_dictionary, new_created_project.uuid, new_created_project.name)

    process = find_process_in_new_project(new_created_project.uuid)

    assert check_if_process_is_finished(process) is True
    assert check_if_project_is_completed(process) is True
    # check_list_of_outputs(process)
    return process

# def run_pipeline_on_ouputs(process: Process):
#     pass
