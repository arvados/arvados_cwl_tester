import logging
from datetime import datetime, timedelta
import os

import arvados
from arvados.errors import ApiError

from biocwltest.arvados_connection.entities import Project, Container, Process, Collection
from biocwltest.arvados_connection.exceptions import ProjectNotFoundError, ProcessNotFoundError, \
    CollectionNotFoundError


class ArvadosClient:
    def __init__(self):
        self.api = arvados.api('v1')

    def get_project(self, uuid: str) -> Project:
        """
        Get project by uuid
        """
        try:
            response = self.api.groups().get(uuid=uuid).execute()
            return Project.from_dict(**response)
        except ApiError as e:
            if e.resp.status == 404:
                raise ProjectNotFoundError(f"No project with uuid {uuid}")
            raise

    def get_collection(self, uuid: str) -> Collection:
        """
        Get collection by uuid
        """
        try:
            response = self.api.collections().get(uuid=uuid).execute()
            return Collection.from_dict(**response)
        except ApiError as e:
            if e.resp.status == 404:
                raise CollectionNotFoundError(f"No collection with uuid {uuid}")
            raise

    def create_project(self, parent_uuid: str, test_name: str) -> Project:
        """
        Create test project in target project. Trash it after one week.
        :param parent_uuid: Target project uuid
        :return: dictionary with project data
        """
        user = os.popen("git config user.name").read()

        response = self.api.groups().create(body={
            "group_class": "project",
            "owner_uuid": parent_uuid,
            "name": f'Testing {test_name} {datetime.now():%Y-%m-%d %H:%M:%S%z} {user}',
            "trash_at": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        }).execute()
        return Project.from_dict(**response)

    def list_container_requests_in_project(self, parent_uuid: str):
        return arvados.util.keyset_list_all(
            self.api.container_requests().list,
            filters=[["owner_uuid", "=", parent_uuid]]
        )

    def get_container_request_by_parent_uuid(self, parent_uuid: str) -> Process:
        """
        Return first container request from parent project. Raise exception if empty
        :param parent_uuid:
        :return:
        """
        requests = list(self.list_container_requests_in_project(parent_uuid))
        if not requests:
            raise ProcessNotFoundError(f"No processes are found in {parent_uuid} project")
        if len(requests) > 1:
            logging.warning(f"Multiple processes found in {parent_uuid}")
        response = requests[0]
        container = self.get_container(response['container_uuid'])
        return Process.from_dict(**response, container=container)

    def get_container(self, uuid: str) -> Container:
        try:
            response = self.api.containers().get(uuid=uuid).execute()
            return Container.from_dict(**response)
        except ApiError as e:
            if e.resp.status == 404:
                raise ProcessNotFoundError(f"No container with uuid {uuid}")
            raise

    # TODO: Starting workflow from Python SDK
    # def create_container_request(self, cwl_path: str, project_uuid: str, inputs: Dict) -> Process:
    #     """
    #     Create container request and start it
    #     :param cwl_path:
    #     :param project_uuid:
    #     :param inputs:
    #     :return:
    #     """
    #     workflow_definition = yaml.safe_load(cwl_path)
    #     user = os.popen("git config user.name").read()
    #     # Construct Container Request from Template (prepare workflow run)
    #     mounts = {
    #         '/var/lib/cwl/cwl.input.json': {'kind': 'json', 'content': inputs},
    #         '/var/lib/cwl/workflow.json': {'kind': 'json', 'content': workflow_definition},
    #         '/var/spool/cwl': {'kind': 'collection', 'writable': True},
    #         'stdout': {'kind': 'file', 'path': '/var/spool/cwl/cwl.output.json'}
    #     }
    #
    #     cr = {
    #         'command': ['arvados-cwl-runner', '--local', '--api=containers', '/var/lib/cwl/workflow.json#main',
    #                     '/var/lib/cwl/cwl.input.json'],
    #         'name': f"Testing {os.path.basename(cwl_path)} {user}",
    #         'mounts': mounts,
    #         'container_image': 'arvados/jobs',
    #         'priority': 1,
    #         'output_path': '/var/spool/cwl',
    #         'runtime_constraints': {'ram': 256000000, 'vcpus': 1, 'API': True},
    #         'owner_uuid': project_uuid
    #     }
    #     new_cr = self.api.container_requests().create(body=cr).execute()
    #     return Process.from_dict(**new_cr)
    #
    # def commit_container_request(self, process: Process):
    #     """
    #     Start process, only works if container request is in state `Draft`
    #     :param process:
    #     :return:
    #     """
    #     if process.state != 'Draft':
    #         raise ContainerRunError(f"Incorrect process state, is: {process.state}, should be Draft")
    #
    #     response = self.api.container_requests().update(uuid=process.uuid, body={'state': 'Committed'}).execute()
    #     container = self.get_container(response['container_uuid'])
    #     return Process.from_dict(**response, container=container)
