import os
from datetime import datetime
from functools import lru_cache as memoized, lru_cache

import arvados.errors

from arvados_cwl_tester.client import ArvadosClient
from arvados_cwl_tester.cwl_runner import run_cwl_arvados
from arvados_cwl_tester.entities import Process, ProcessStatus, Project
from arvados_cwl_tester.helpers import Colors, get_username

DEFAULT_PROJECT_UUID = None

__all__ = [
    "get_or_create_project",
    "find_process_in_new_project",
    "save_file",
    "check_if_process_is_finished",
    "check_if_project_is_completed",
    "arvados_run",
    "arvados_project_uuid",
]


@lru_cache
def get_or_create_project(target: str) -> Project:
    """
    Create one project per day for all user tests.
    """
    username = get_username()
    subproject_name = f"arvados_cwl_tester {username} {datetime.now():%Y-%m-%d}"
    client = ArvadosClient()
    project = client.find_project_by_name(target, subproject_name)
    if project:
        return project
    # Create project in target
    try:
        project = client.create_project(target, subproject_name)
    except arvados.errors.ApiError as e:
        if e.resp.status == 422:
            # Project was already created in a concurrent test, return existing project
            project = client.find_project_by_name(target, subproject_name)
            if project:
                return project
        raise
    print(
        Colors.BOLD
        + f"Project {subproject_name} was created succesfully: {project.uuid}"
    )
    return project


def find_process_in_new_project(project_uuid: str, test_name: str):
    client = ArvadosClient()
    return client.get_container_request_by_parent_uuid(project_uuid, test_name)


def save_file(collection_uuid: str, filename: str, output_filename: str = None):
    client = ArvadosClient()
    collection = client.get_collection(collection_uuid)
    if not os.path.exists("./logs"):
        os.makedirs("./logs")
    # TODO: add to this file command of the process
    with collection.reader.open(filename, "r") as file_reader:
        with open(f"./logs/{output_filename}" or f"./logs/{filename}", "w") as file:
            file.write(file_reader.read())


def check_if_process_is_finished(process: Process, test_name: str):
    if process.status in [
        ProcessStatus.COMPLETED,
        ProcessStatus.FAILED,
        ProcessStatus.CANCELLED,
    ]:
        print(Colors.OKBLUE + f"Process '{test_name}' is finished!")
        return True

    # print(process.log_uuid.stderr)
    print(process.log_uuid.command)
    return False


def check_if_project_is_completed(process: Process, test_name: str):
    if process.status == ProcessStatus.COMPLETED:
        print(
            Colors.OKGREEN + f"Process '{test_name}' was completed successfully :-) !"
        )
        return True
    log_name = (
        f"{test_name.replace('.', '_').replace(' ', '_')}_{process.uuid}_stderr.txt"
    )
    print(
        Colors.ERROR
        + f"Process '{test_name}' failed or cancelled :(, saving logs to {log_name}"
    )
    save_file(process.log_uuid, "stderr.txt", log_name)
    return False


def get_current_pytest_name() -> str:
    """
    Get current pytest name
    Returns:
        str, current pytest name
    """
    if "PYTEST_CURRENT_TEST" not in os.environ:
        raise Exception("arvados_run can be used only in pytest test")

    return os.environ["PYTEST_CURRENT_TEST"].split(":")[-1].split(" ")[0]


class Result:
    def __init__(self, process: Process):
        self.client = ArvadosClient()
        self.process = process

    @property
    @memoized()
    def files(self) -> dict:
        """
        Create dictionary with outputs from process
        Arguments:
            process: class Process
        Returns:
            Dictionary containing outputs filenames as keys and dictionaries as values, with following fields: 'size', 'basename' and 'location''
        """
        collection = self.client.get_collection(self.process.output_uuid)
        data_hash = collection.portable_data_hash

        outputs = {}
        for file in collection.reader.all_files():
            outputs[file.name()] = {
                "size": file.size(),
                "basename": file.name(),
                "location": f"{data_hash}/{file.name()}",
            }
        return outputs


def arvados_run(cwl_path: str, inputs: dict, project_uuid: str = None) -> Result:
    """
    Run process, return process object (class Process)
    Check if project is finished, check if project is completed.
    Arguments:
        cwl_path: str, path to cwl file that will be executed
        inputs: dict, containing cwl inputs. This is optional, because sometimes cwl doesn't require input.
        arvados_project: str, uuid of project when process will be executed. Example: arkau-ecds9343fdscdsdcd
    Returns:
        dict, containing outputs filenames as keys and dictionaries as values,
        with following fields: 'size', 'basename' and 'location'
    """

    if project_uuid is None and DEFAULT_PROJECT_UUID is None:
        raise Exception(
            "You need to use set_project_uuid function to set default project"
        )

    project = project_uuid or DEFAULT_PROJECT_UUID

    new_created_project = get_or_create_project(project)
    test_name = f"{get_current_pytest_name()} {datetime.now():%Y-%m-%d %H:%M:%S%f%z}"
    run_cwl_arvados(cwl_path, inputs, new_created_project.uuid, test_name)

    process = find_process_in_new_project(new_created_project.uuid, test_name)

    assert check_if_process_is_finished(process, new_created_project.name)
    assert check_if_project_is_completed(process, new_created_project.name)

    return Result(process)


def arvados_project_uuid(uuid: str):
    global DEFAULT_PROJECT_UUID
    DEFAULT_PROJECT_UUID = uuid
