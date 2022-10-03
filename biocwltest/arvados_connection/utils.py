from biocwltest.arvados_connection.client import ArvadosClient
from biocwltest.arvados_connection.entities import Process, ProcessStatus

__all__ = [
    "create_new_project",
    "find_process_in_new_project",
    "check_if_process_is_finished",
    "check_if_collection_output_not_empty",
    "check_if_project_is_completed",
    "check_list_of_outputs"
]


def create_new_project(target: str, test_name: str):
    # Create project in target
    client = ArvadosClient()
    project = client.create_project(target, test_name)
    print(f"Project was created succesfully: {project.uuid}")
    return project


def find_process_in_new_project(project_uuid: str):
    client = ArvadosClient()
    return client.get_container_request_by_parent_uuid(project_uuid)


def check_if_process_is_finished(process: Process):
    return process.status in [
        ProcessStatus.COMPLETED,
        ProcessStatus.FAILED,
        ProcessStatus.CANCELLED
    ]

def check_if_project_is_completed(process: Process):
    return process.status == ProcessStatus.COMPLETED


def check_if_collection_output_not_empty(process: Process):
    client = ArvadosClient()
    output = client.get_collection(process.output_uuid)
    return output.file_count > 0

# def check_list_of_outputs(process: Process) -> list:
#     client = ArvadosClient()
#     output = client.get_collection(process.output_uuid)
#     print(output)
    