from biocwltest.arvados_connection import create_new_project, find_process_in_new_project, check_if_process_is_finished
from biocwltest.arvados_connection.entities import Process
from biocwltest.cwl_runner import run_cwl_arvados


def basic_arvados_test(target_project, test_name, cwl_path, inputs_dictionary) -> Process:
    new_created_project = create_new_project(target_project)
    run_cwl_arvados(cwl_path, inputs_dictionary, new_created_project.uuid, test_name)
    process = find_process_in_new_project(new_created_project.uuid)  # Process will be a dictionary
    assert check_if_process_is_finished(process) is True
    return process
